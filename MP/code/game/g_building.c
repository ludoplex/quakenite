/*
===========================================================================
QuakeNite Building System - Server Side

Handles structure spawning, placement validation, damage, and destruction.
Implements Fortnite-style building mechanics for the id Tech 3 engine.
===========================================================================
*/

#include "g_local.h"
#include "g_building.h"

// ============================================================================
// CVars
// ============================================================================
vmCvar_t g_buildingEnabled;
vmCvar_t g_buildingStartMaterials;
vmCvar_t g_buildingMaxStructures;

// ============================================================================
// Building Piece Definitions
// ============================================================================
static buildPieceDef_t buildPieceDefs[BUILD_NUM_TYPES] = {
	// BUILD_NONE
	{ BUILD_NONE, "None", "", "", {0, 0, 0}, {0, 0, 0}, 0, 0, 0 },

	// BUILD_WALL - Vertical wall, 64x64 face, 8 units thick
	{
		BUILD_WALL, "Wall",
		"models/buildables/wall.md3",
		"gfx/hud/build_wall.tga",
		{-32, -4, 0},       // mins
		{32, 4, 64},        // maxs
		BUILD_DEFAULT_HEALTH,
		10,                 // material cost
		BUILD_GRID_SIZE
	},

	// BUILD_FLOOR - Horizontal platform
	{
		BUILD_FLOOR, "Floor",
		"models/buildables/floor.md3",
		"gfx/hud/build_floor.tga",
		{-32, -32, -4},     // mins
		{32, 32, 4},        // maxs
		BUILD_DEFAULT_HEALTH,
		10,
		BUILD_GRID_SIZE
	},

	// BUILD_RAMP - 45-degree ramp
	{
		BUILD_RAMP, "Ramp",
		"models/buildables/ramp.md3",
		"gfx/hud/build_ramp.tga",
		{-32, -32, 0},      // mins
		{32, 32, 64},       // maxs
		BUILD_DEFAULT_HEALTH,
		10,
		BUILD_GRID_SIZE
	},

	// BUILD_ROOF - Angled roof piece
	{
		BUILD_ROOF, "Roof",
		"models/buildables/roof.md3",
		"gfx/hud/build_roof.tga",
		{-32, -32, 0},
		{32, 32, 32},
		100,
		10,
		BUILD_GRID_SIZE
	}
};

// ============================================================================
// G_RegisterBuildingCvars
// ============================================================================
void G_RegisterBuildingCvars( void ) {
	trap_Cvar_Register( &g_buildingEnabled, "g_buildingEnabled", "1", 0 );
	trap_Cvar_Register( &g_buildingStartMaterials, "g_buildingStartMaterials", "100", CVAR_ARCHIVE );
	trap_Cvar_Register( &g_buildingMaxStructures, "g_buildingMaxStructures", "256", CVAR_ARCHIVE );
}

// ============================================================================
// G_InitBuildingSystem
// ============================================================================
void G_InitBuildingSystem( void ) {
	int i;

	G_RegisterBuildingCvars();

	// Precache all buildable models
	for ( i = 1; i < BUILD_NUM_TYPES; i++ ) {
		if ( buildPieceDefs[i].modelPath[0] ) {
			G_ModelIndex( (char *)buildPieceDefs[i].modelPath );
		}
	}

	G_Printf( "QuakeNite building system initialized with %d piece types\n", BUILD_NUM_TYPES - 1 );
}

// ============================================================================
// G_GetBuildPieceDef
// ============================================================================
const buildPieceDef_t *G_GetBuildPieceDef( buildType_t type ) {
	if ( type < 0 || type >= BUILD_NUM_TYPES ) {
		return &buildPieceDefs[BUILD_NONE];
	}
	return &buildPieceDefs[type];
}

// ============================================================================
// G_SnapToGrid - Snap position to building grid
// ============================================================================
static void G_SnapToGrid( vec3_t origin, float gridSize ) {
	origin[0] = floor( origin[0] / gridSize + 0.5f ) * gridSize;
	origin[1] = floor( origin[1] / gridSize + 0.5f ) * gridSize;
	origin[2] = floor( origin[2] / gridSize + 0.5f ) * gridSize;
}

// ============================================================================
// G_CountBuildables - Count current buildable entities
// ============================================================================
int G_CountBuildables( void ) {
	int i, count = 0;
	gentity_t *ent;

	for ( i = 0; i < level.num_entities; i++ ) {
		ent = &g_entities[i];
		if ( !ent->inuse ) {
			continue;
		}
		if ( ent->s.eType == ET_BUILDABLE ) {
			count++;
		}
	}

	return count;
}

// ============================================================================
// G_CanPlaceBuildable - Check if placement is valid
// ============================================================================
qboolean G_CanPlaceBuildable( buildType_t type, vec3_t origin, vec3_t angles, gentity_t *builder ) {
	const buildPieceDef_t *def;
	trace_t tr;
	vec3_t mins, maxs;
	int i;
	gentity_t *hit;

	if ( !g_buildingEnabled.integer ) {
		return qfalse;
	}

	def = G_GetBuildPieceDef( type );
	if ( !def || type == BUILD_NONE ) {
		return qfalse;
	}

	// Check materials
	if ( builder && builder->client ) {
		if ( builder->client->ps.stats[STAT_QN_MATERIALS] < def->materialCost ) {
			return qfalse;
		}
	}

	// Check max structures
	if ( G_CountBuildables() >= g_buildingMaxStructures.integer ) {
		return qfalse;
	}

	// Calculate bounds (simplified - not rotating bounds)
	VectorCopy( def->mins, mins );
	VectorCopy( def->maxs, maxs );

	// Check for collision with world
	trap_Trace( &tr, origin, mins, maxs, origin, builder ? builder->s.number : -1, MASK_SOLID );

	if ( tr.startsolid || tr.allsolid ) {
		return qfalse;
	}

	// Check for overlapping buildables using proper AABB intersection
	for ( i = 0; i < level.num_entities; i++ ) {
		const buildPieceDef_t *hitDef;
		vec3_t newMins, newMaxs, hitMins, hitMaxs;

		hit = &g_entities[i];
		if ( !hit->inuse ) {
			continue;
		}
		if ( hit->s.eType != ET_BUILDABLE ) {
			continue;
		}

		// Get bounds for the existing buildable
		hitDef = G_GetBuildPieceDef( (buildType_t)hit->buildableType );
		if ( !hitDef ) {
			continue;
		}

		// Calculate actual world-space AABB bounds for new piece
		VectorAdd( origin, def->mins, newMins );
		VectorAdd( origin, def->maxs, newMaxs );

		// Calculate actual world-space AABB bounds for existing piece
		VectorAdd( hit->r.currentOrigin, hitDef->mins, hitMins );
		VectorAdd( hit->r.currentOrigin, hitDef->maxs, hitMaxs );

		// AABB intersection test
		if ( newMins[0] <= hitMaxs[0] && newMaxs[0] >= hitMins[0] &&
			 newMins[1] <= hitMaxs[1] && newMaxs[1] >= hitMins[1] &&
			 newMins[2] <= hitMaxs[2] && newMaxs[2] >= hitMins[2] ) {
			return qfalse;  // Collision with existing buildable
		}
	}

	return qtrue;
}

// ============================================================================
// G_BuildableThink - Per-frame think for buildables
// ============================================================================
void G_BuildableThink( gentity_t *ent ) {
	ent->nextthink = level.time + 1000;  // Think every second

	// Could add decay, effects, etc.
}

// ============================================================================
// G_BuildableDie - Called when buildable is destroyed
// ============================================================================
void G_BuildableDie( gentity_t *self, gentity_t *inflictor, gentity_t *attacker,
					 int damage, int mod ) {
	// Spawn destruction effect
	G_TempEntity( self->r.currentOrigin, EV_BUILD_DESTROY );

	// Remove entity
	G_FreeEntity( self );
}

// ============================================================================
// G_BuildablePain - Damage feedback
// ============================================================================
void G_BuildablePain( gentity_t *self, gentity_t *attacker, int damage, vec3_t point ) {
	// Could add damage visual effects
}

// ============================================================================
// G_SpawnBuildable - Create a new buildable structure
// ============================================================================
gentity_t *G_SpawnBuildable( buildType_t type, vec3_t origin, vec3_t angles, gentity_t *builder ) {
	gentity_t *ent;
	const buildPieceDef_t *def;
	vec3_t snappedOrigin;

	if ( !g_buildingEnabled.integer ) {
		return NULL;
	}

	def = G_GetBuildPieceDef( type );
	if ( !def || type == BUILD_NONE ) {
		return NULL;
	}

	// Snap to grid
	VectorCopy( origin, snappedOrigin );
	G_SnapToGrid( snappedOrigin, def->gridSnap );

	// Final placement check
	if ( !G_CanPlaceBuildable( type, snappedOrigin, angles, builder ) ) {
		return NULL;
	}

	// Allocate entity
	ent = G_Spawn();
	if ( !ent ) {
		G_Printf( "G_SpawnBuildable: no free entities\n" );
		return NULL;
	}

	// Set up entity
	ent->classname = "buildable";
	ent->s.eType = ET_BUILDABLE;
	ent->buildableType = type;
	ent->buildableOwner = builder ? builder->client->ps.clientNum : -1;

	// Position
	VectorCopy( snappedOrigin, ent->s.origin );
	VectorCopy( snappedOrigin, ent->r.currentOrigin );
	VectorCopy( angles, ent->s.angles );
	G_SetOrigin( ent, snappedOrigin );

	// Model
	ent->s.modelindex = G_ModelIndex( (char *)def->modelPath );

	// Send the buildable type in a spare entityState field for client
	ent->s.otherEntityNum2 = type;

	// Collision
	VectorCopy( def->mins, ent->r.mins );
	VectorCopy( def->maxs, ent->r.maxs );
	ent->r.contents = CONTENTS_SOLID;
	ent->clipmask = MASK_SOLID;
	ent->r.svFlags = SVF_USE_CURRENT_ORIGIN;

	// Health and damage
	ent->health = def->health;
	ent->takedamage = qtrue;
	ent->die = G_BuildableDie;
	ent->pain = G_BuildablePain;

	// Think function
	ent->think = G_BuildableThink;
	ent->nextthink = level.time + 1000;

	// Link to world
	trap_LinkEntity( ent );

	// Deduct materials from builder
	if ( builder && builder->client ) {
		builder->client->ps.stats[STAT_QN_MATERIALS] -= def->materialCost;
	}

	// Placement event for sound/effects
	G_AddEvent( ent, EV_BUILD_PLACE, type );

	return ent;
}

// ============================================================================
// G_BuildingPlayerSpawn - Give starting materials to player
// ============================================================================
void G_BuildingPlayerSpawn( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( g_buildingEnabled.integer ) {
		ent->client->ps.stats[STAT_QN_MATERIALS] = g_buildingStartMaterials.integer;
	}

	// Reset build state
	memset( &ent->client->buildState, 0, sizeof( ent->client->buildState ) );
}

// ============================================================================
// Client Commands
// ============================================================================

// Toggle build mode
void Cmd_BuildMode_f( gentity_t *ent ) {
	if ( !ent->client ) {
		return;
	}

	if ( !g_buildingEnabled.integer ) {
		trap_SendServerCommand( ent->s.number, "print \"Building is disabled on this server\n\"" );
		return;
	}

	ent->client->buildState.active = !ent->client->buildState.active;

	if ( ent->client->buildState.active ) {
		// Enter build mode
		ent->client->buildState.selectedType = BUILD_WALL;
		ent->client->buildState.rotation = 0;
		trap_SendServerCommand( ent->s.number, "print \"Build mode ON - Q to toggle, 1-4 to select piece, R to rotate\n\"" );
	} else {
		// Exit build mode
		trap_SendServerCommand( ent->s.number, "print \"Build mode OFF\n\"" );
	}
}

// Select piece type: "buildselect <type>"
void Cmd_BuildSelect_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int type;

	if ( !ent->client || !ent->client->buildState.active ) {
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	type = atoi( arg );

	if ( type > BUILD_NONE && type < BUILD_NUM_TYPES ) {
		ent->client->buildState.selectedType = type;
		trap_SendServerCommand( ent->s.number,
								va( "print \"Selected: %s\n\"", G_GetBuildPieceDef( type )->name ) );
	}
}

// Rotate preview: "buildrotate"
void Cmd_BuildRotate_f( gentity_t *ent ) {
	if ( !ent->client || !ent->client->buildState.active ) {
		return;
	}

	ent->client->buildState.rotation = ( ent->client->buildState.rotation + 90 ) % 360;
}

// Place structure: "buildplace"
void Cmd_BuildPlace_f( gentity_t *ent ) {
	vec3_t forward, end, origin, angles;
	trace_t tr;
	const buildPieceDef_t *def;

	if ( !ent->client ) {
		return;
	}

	if ( !ent->client->buildState.active ) {
		return;
	}

	// Cooldown check
	if ( level.time < ent->client->buildState.lastBuildTime + BUILD_COOLDOWN_MS ) {
		return;
	}

	def = G_GetBuildPieceDef( ent->client->buildState.selectedType );
	if ( !def ) {
		return;
	}

	// Check materials before tracing
	if ( ent->client->ps.stats[STAT_QN_MATERIALS] < def->materialCost ) {
		trap_SendServerCommand( ent->s.number, "print \"Not enough materials\n\"" );
		G_AddEvent( ent, EV_BUILD_FAIL, 0 );
		return;
	}

	// Calculate placement position (trace from view)
	AngleVectors( ent->client->ps.viewangles, forward, NULL, NULL );
	VectorCopy( ent->client->ps.origin, origin );
	origin[2] += ent->client->ps.viewheight;
	VectorMA( origin, BUILD_PREVIEW_RANGE, forward, end );

	trap_Trace( &tr, origin, NULL, NULL, end, ent->s.number, MASK_SOLID );

	VectorCopy( tr.endpos, origin );
	VectorSet( angles, 0, ent->client->buildState.rotation, 0 );

	// Attempt to place
	if ( G_SpawnBuildable( ent->client->buildState.selectedType, origin, angles, ent ) ) {
		ent->client->buildState.lastBuildTime = level.time;
	} else {
		// Placement failed
		G_AddEvent( ent, EV_BUILD_FAIL, 0 );
		trap_SendServerCommand( ent->s.number, "print \"Cannot place here\n\"" );
	}
}
