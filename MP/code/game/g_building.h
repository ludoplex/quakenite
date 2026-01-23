/*
===========================================================================
QuakeNite Building System - Server Header

Defines building types, structures, and server-side API for
Fortnite-style building mechanics.
===========================================================================
*/

#ifndef G_BUILDING_H
#define G_BUILDING_H

// ============================================================================
// Building Structure Types
// ============================================================================
typedef enum {
	BUILD_NONE = 0,
	BUILD_WALL,         // Vertical 64x64x8 wall
	BUILD_FLOOR,        // Horizontal 64x64x8 platform
	BUILD_RAMP,         // 45-degree ramp, 64x64x64
	BUILD_ROOF,         // Angled roof piece
	BUILD_NUM_TYPES
} buildType_t;

// ============================================================================
// Building Piece Definition
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
// Constants
// ============================================================================
#define BUILD_GRID_SIZE         64.0f
#define BUILD_COOLDOWN_MS       100     // 100ms between placements
#define BUILD_PREVIEW_RANGE     256.0f  // Max placement distance
#define BUILD_MAX_STRUCTURES    256     // Max buildables per map
#define BUILD_DEFAULT_HEALTH    150     // Default structure health

// Material stat - using a high stat index to avoid conflicts
#define STAT_QN_MATERIALS       25

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
