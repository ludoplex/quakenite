/*
===========================================================================
QuakeNite Building System - Client Side

Handles preview ghost, HUD elements, and buildable entity rendering.
===========================================================================
*/

#include "cg_local.h"
#include "cg_building.h"

// Global build state
cgBuildState_t cg_buildState;

// ============================================================================
// Building Piece Definitions (client-side mirror)
// ============================================================================
typedef struct {
	int         type;
	const char  *name;
	const char  *modelPath;
	const char  *iconPath;
	vec3_t      mins;
	vec3_t      maxs;
} cgBuildPieceDef_t;

static cgBuildPieceDef_t cgBuildPieces[BUILD_NUM_TYPES] = {
	{ BUILD_NONE, "None", "", "", {0, 0, 0}, {0, 0, 0} },
	{ BUILD_WALL, "Wall", "models/buildables/wall.md3", "gfx/hud/build_wall.tga",
	  {-32, -4, 0}, {32, 4, 64} },
	{ BUILD_FLOOR, "Floor", "models/buildables/floor.md3", "gfx/hud/build_floor.tga",
	  {-32, -32, -4}, {32, 32, 4} },
	{ BUILD_RAMP, "Ramp", "models/buildables/ramp.md3", "gfx/hud/build_ramp.tga",
	  {-32, -32, 0}, {32, 32, 64} },
	{ BUILD_ROOF, "Roof", "models/buildables/roof.md3", "gfx/hud/build_roof.tga",
	  {-32, -32, 0}, {32, 32, 32} },
};

// ============================================================================
// CG_InitBuildingSystem
// ============================================================================
void CG_InitBuildingSystem( void ) {
	int i;

	memset( &cg_buildState, 0, sizeof( cg_buildState ) );

	// Precache models and icons
	for ( i = 1; i < BUILD_NUM_TYPES; i++ ) {
		if ( cgBuildPieces[i].modelPath[0] ) {
			cg_buildState.previewModels[i] = trap_R_RegisterModel( cgBuildPieces[i].modelPath );
		}
		if ( cgBuildPieces[i].iconPath[0] ) {
			cg_buildState.pieceIcons[i] = trap_R_RegisterShader( cgBuildPieces[i].iconPath );
		}
	}

	CG_Printf( "QuakeNite client building system initialized\n" );
}

// ============================================================================
// CG_SnapToGrid - Snap position to building grid
// ============================================================================
static void CG_SnapToGrid( vec3_t origin, float gridSize ) {
	origin[0] = floor( origin[0] / gridSize + 0.5f ) * gridSize;
	origin[1] = floor( origin[1] / gridSize + 0.5f ) * gridSize;
	origin[2] = floor( origin[2] / gridSize + 0.5f ) * gridSize;
}

// ============================================================================
// CG_UpdateBuildPreview - Called each frame to update preview position
// ============================================================================
void CG_UpdateBuildPreview( void ) {
	trace_t tr;
	vec3_t forward, end, start;

	if ( !cg_buildState.active ) {
		return;
	}

	// Trace from view
	AngleVectors( cg.refdefViewAngles, forward, NULL, NULL );
	VectorCopy( cg.refdef.vieworg, start );
	VectorMA( start, BUILD_PREVIEW_RANGE, forward, end );

	CG_Trace( &tr, start, NULL, NULL, end, cg.predictedPlayerState.clientNum, MASK_SOLID );

	// Snap to grid
	VectorCopy( tr.endpos, cg_buildState.previewOrigin );
	CG_SnapToGrid( cg_buildState.previewOrigin, BUILD_GRID_SIZE );

	VectorSet( cg_buildState.previewAngles, 0, cg_buildState.rotation, 0 );

	// Check if placement is valid (simplified client-side check)
	cg_buildState.canPlace = ( tr.fraction < 1.0f && !tr.startsolid );
}

// ============================================================================
// CG_DrawBuildPreview - Render the ghost preview
// ============================================================================
void CG_DrawBuildPreview( void ) {
	refEntity_t ent;
	cgBuildPieceDef_t *def;

	if ( !cg_buildState.active || cg_buildState.selectedType <= 0 ) {
		return;
	}

	if ( cg_buildState.selectedType >= BUILD_NUM_TYPES ) {
		return;
	}

	def = &cgBuildPieces[cg_buildState.selectedType];

	memset( &ent, 0, sizeof( ent ) );

	VectorCopy( cg_buildState.previewOrigin, ent.origin );
	AnglesToAxis( cg_buildState.previewAngles, ent.axis );

	ent.hModel = cg_buildState.previewModels[cg_buildState.selectedType];
	if ( !ent.hModel ) {
		// Model not loaded, use a fallback or skip
		return;
	}

	ent.renderfx = RF_TRANSLUCENT;

	// Color based on can place
	if ( cg_buildState.canPlace ) {
		ent.shaderRGBA[0] = 0;
		ent.shaderRGBA[1] = 255;
		ent.shaderRGBA[2] = 0;
		ent.shaderRGBA[3] = 128;
	} else {
		ent.shaderRGBA[0] = 255;
		ent.shaderRGBA[1] = 0;
		ent.shaderRGBA[2] = 0;
		ent.shaderRGBA[3] = 128;
	}

	trap_R_AddRefEntityToScene( &ent );
}

// ============================================================================
// CG_DrawBuildHUD - Draw building mode UI elements
// ============================================================================
void CG_DrawBuildHUD( void ) {
	int x, y, i;
	int materials;
	vec4_t color;
	char *text;

	if ( !cg_buildState.active ) {
		return;
	}

	// Get material count from player state
	materials = cg.predictedPlayerState.stats[STAT_QN_MATERIALS];

	// Draw "BUILD MODE" header
	x = 320 - 50;
	y = 380;
	CG_DrawStringExt( x, y, "BUILD MODE", colorYellow, qfalse, qtrue, 10, 14, 0 );

	// Draw material count
	y += 20;
	text = va( "Materials: %d", materials );
	CG_DrawStringExt( x, y, text, colorWhite, qfalse, qtrue, 8, 12, 0 );

	// Draw piece selection bar
	x = 320 - ( ( BUILD_NUM_TYPES - 1 ) * 20 );
	y = 420;

	for ( i = 1; i < BUILD_NUM_TYPES; i++ ) {
		// Highlight selected
		if ( i == cg_buildState.selectedType ) {
			Vector4Set( color, 1, 1, 1, 1 );
			// Draw selection highlight
			CG_FillRect( x - 2, y - 2, 36, 36, colorYellow );
		} else {
			Vector4Set( color, 0.5, 0.5, 0.5, 1 );
		}

		trap_R_SetColor( color );
		if ( cg_buildState.pieceIcons[i] ) {
			CG_DrawPic( x, y, 32, 32, cg_buildState.pieceIcons[i] );
		} else {
			// No icon loaded - draw placeholder
			CG_FillRect( x, y, 32, 32, colorGray );
		}
		trap_R_SetColor( NULL );

		// Draw piece number
		CG_DrawStringExt( x + 12, y + 34, va( "%d", i ), colorWhite, qfalse, qtrue, 8, 10, 0 );

		x += 40;
	}

	// Draw selected piece name
	if ( cg_buildState.selectedType > 0 && cg_buildState.selectedType < BUILD_NUM_TYPES ) {
		text = va( "Selected: %s", cgBuildPieces[cg_buildState.selectedType].name );
		CG_DrawStringExt( 320 - 40, 460, text, colorWhite, qfalse, qtrue, 8, 12, 0 );
	}
}

// ============================================================================
// CG_Buildable - Render a buildable entity
// ============================================================================
void CG_Buildable( centity_t *cent ) {
	refEntity_t ent;
	entityState_t *s1;

	s1 = &cent->currentState;

	memset( &ent, 0, sizeof( ent ) );

	VectorCopy( cent->lerpOrigin, ent.origin );
	VectorCopy( cent->lerpOrigin, ent.oldorigin );
	AnglesToAxis( cent->lerpAngles, ent.axis );

	ent.hModel = cgs.gameModels[s1->modelindex];
	if ( !ent.hModel ) {
		return;
	}

	ent.renderfx = RF_NOSHADOW;

	trap_R_AddRefEntityToScene( &ent );

	// Store for other systems
	memcpy( &cent->refEnt, &ent, sizeof( refEntity_t ) );
}

// ============================================================================
// Command handlers (called from cg_consolecmds.c)
// ============================================================================

void CG_BuildMode_f( void ) {
	cg_buildState.active = !cg_buildState.active;
	if ( cg_buildState.active ) {
		cg_buildState.selectedType = BUILD_WALL;
		cg_buildState.rotation = 0;
	}
	// Also send to server
	trap_SendClientCommand( "buildmode" );
}

void CG_BuildSelect_f( void ) {
	char arg[MAX_TOKEN_CHARS];
	int type;

	trap_Argv( 1, arg, sizeof( arg ) );
	type = atoi( arg );

	if ( type > 0 && type < BUILD_NUM_TYPES ) {
		cg_buildState.selectedType = type;
		trap_SendClientCommand( va( "buildselect %d", type ) );
	}
}

void CG_BuildRotate_f( void ) {
	cg_buildState.rotation = ( cg_buildState.rotation + 90 ) % 360;
	trap_SendClientCommand( "buildrotate" );
}

void CG_BuildPlace_f( void ) {
	if ( cg_buildState.active && cg_buildState.canPlace ) {
		trap_SendClientCommand( "buildplace" );
	}
}
