/*
===========================================================================
QuakeNite Building System - Client Header

Client-side building preview, HUD, and rendering definitions.
===========================================================================
*/

#ifndef CG_BUILDING_H
#define CG_BUILDING_H

// ============================================================================
// Building Types (must match server g_building.h)
// ============================================================================
#define BUILD_NONE      0
#define BUILD_WALL      1
#define BUILD_FLOOR     2
#define BUILD_RAMP      3
#define BUILD_ROOF      4
#define BUILD_NUM_TYPES 5

// ============================================================================
// Constants
// ============================================================================
#define BUILD_GRID_SIZE         64.0f
#define BUILD_PREVIEW_RANGE     256.0f
#define STAT_QN_MATERIALS       25

// ============================================================================
// Client-side Build Preview State
// ============================================================================
typedef struct {
	qboolean    active;
	int         selectedType;
	int         rotation;
	vec3_t      previewOrigin;
	vec3_t      previewAngles;
	qboolean    canPlace;
	qhandle_t   previewModels[BUILD_NUM_TYPES];
	qhandle_t   pieceIcons[BUILD_NUM_TYPES];
} cgBuildState_t;

// ============================================================================
// Function Declarations
// ============================================================================

// Initialization
void CG_InitBuildingSystem( void );

// Per-frame updates
void CG_UpdateBuildPreview( void );

// Rendering
void CG_DrawBuildPreview( void );
void CG_DrawBuildHUD( void );
void CG_Buildable( centity_t *cent );

// Commands (called from cg_consolecmds.c)
void CG_BuildMode_f( void );
void CG_BuildSelect_f( void );
void CG_BuildRotate_f( void );
void CG_BuildPlace_f( void );

// External state
extern cgBuildState_t cg_buildState;

#endif // CG_BUILDING_H
