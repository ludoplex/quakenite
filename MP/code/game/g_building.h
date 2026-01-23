/*
===========================================================================
QuakeNite Building System - Server Header

Defines building types, structures, and server-side API for
Fortnite-style building mechanics.
===========================================================================
*/

#ifndef G_BUILDING_H
#define G_BUILDING_H

#include "bg_building.h"  // Shared building types and constants

// ============================================================================
// Building Piece Definition (server-side only)
// ============================================================================
typedef struct {
	buildType_t type;
	const char  *name;          // "Wall", "Floor", etc.
	const char  *modelPath;     // "models/buildables/wall.md3"
	const char  *iconPath;      // "gfx/hud/build_wall.tga"
	vec3_t      mins;           // Collision box mins
	vec3_t      maxs;           // Collision box maxs
	int         health;         // Default health
	int         materialCost;   // Resources required to build
	float       gridSnap;       // Grid alignment (64.0)
} buildPieceDef_t;

// ============================================================================
// Build Mode State (per-client)
// ============================================================================
typedef struct {
	qboolean    active;             // Is build mode on?
	buildType_t selectedType;       // Currently selected piece
	int         rotation;           // 0, 90, 180, 270 degrees
	vec3_t      previewOrigin;      // Where ghost would be placed
	vec3_t      previewAngles;      // Ghost orientation
	qboolean    canPlace;           // Is current position valid?
	int         lastBuildTime;      // Cooldown between placements
} buildState_t;

// ============================================================================
// Server CVars (extern declarations)
// ============================================================================
extern vmCvar_t g_buildingEnabled;
extern vmCvar_t g_buildingStartMaterials;
extern vmCvar_t g_buildingMaxStructures;

// ============================================================================
// Function Declarations
// ============================================================================

// Initialization
void G_InitBuildingSystem( void );
void G_RegisterBuildingCvars( void );

// Piece definitions
const buildPieceDef_t *G_GetBuildPieceDef( buildType_t type );

// Spawning and validation
gentity_t *G_SpawnBuildable( buildType_t type, vec3_t origin, vec3_t angles, gentity_t *builder );
qboolean G_CanPlaceBuildable( buildType_t type, vec3_t origin, vec3_t angles, gentity_t *builder );
int G_CountBuildables( void );

// Think and damage
void G_BuildableThink( gentity_t *ent );
void G_BuildableDie( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int mod );
void G_BuildablePain( gentity_t *self, gentity_t *attacker, int damage, vec3_t point );

// Client commands
void Cmd_BuildMode_f( gentity_t *ent );
void Cmd_BuildSelect_f( gentity_t *ent );
void Cmd_BuildRotate_f( gentity_t *ent );
void Cmd_BuildPlace_f( gentity_t *ent );

// Player spawn hook (give starting materials)
void G_BuildingPlayerSpawn( gentity_t *ent );

#endif // G_BUILDING_H
