/*
===========================================================================
QuakeNite Building System - Client Header

Client-side building preview, HUD, and rendering definitions.
===========================================================================
*/

#ifndef CG_BUILDING_H
#define CG_BUILDING_H

#include "../game/bg_building.h"  // Shared building types and constants
// Note: STAT_QN_MATERIALS is defined in bg_public.h

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
