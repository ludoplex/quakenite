/*
===========================================================================
QuakeNite Building System - Shared Header

Shared definitions for building types and constants used by both
the server (game) and client (cgame) modules.
===========================================================================
*/

#ifndef BG_BUILDING_H
#define BG_BUILDING_H

// ============================================================================
// Building Structure Types (shared client/server)
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
// Building Constants (shared client/server)
// ============================================================================
#define BUILD_GRID_SIZE         64.0f
#define BUILD_PREVIEW_RANGE     256.0f
#define BUILD_COOLDOWN_MS       100     // 100ms between placements
#define BUILD_MAX_STRUCTURES    256     // Max buildables per map
#define BUILD_DEFAULT_HEALTH    150     // Default structure health

#endif // BG_BUILDING_H
