/*
===========================================================================
QuakeNite Character Roster System

Defines the 9 playable characters for QuakeNite. Characters are purely
cosmetic - same hitbox, same stats, different model/skin/voice.

Asset layout expected:
  models/players/<modelName>/
    lower.md3, upper.md3, head.md3
    animation.cfg
    default.skin, red.skin, blue.skin, green.skin, yellow.skin
    icon_default.tga

  sound/player/<modelName>/
    spawn1.wav, frag1.wav, death1.wav, etc.
===========================================================================
*/

#ifndef BG_QN_CHARACTERS_H
#define BG_QN_CHARACTERS_H

// ============================================================================
// Character IDs - order matters for qn_char cvar values
// ============================================================================
typedef enum {
	QN_CHAR_MISTER_CHEF = 0,    // Master Chief parody - cooking supersoldier
	QN_CHAR_BLITZ,              // Battletoads parody - 80s cartoon toad
	QN_CHAR_WILLY_LEE,          // Double Dragon parody - 80s martial artist
	QN_CHAR_STEELHEIM,          // Stroheim/JoJo parody - bombastic cyborg
	QN_CHAR_HOLSTER_COLT,       // Hol Horse/JoJo parody - anime cowboy
	QN_CHAR_NUMBER_SIX,         // Guido Mista/JoJo parody - tetraphobic gunslinger
	QN_CHAR_SOLID_SERPENT,      // Metal Gear parody - tactical stealth operative
	QN_CHAR_DUDE_BLASTEM,       // Duke Nukem/Doom parody - 90s action hero
	QN_CHAR_SIR_MATTHIAS,       // Redwall parody - medieval warrior mouse

	QN_NUM_CHARACTERS
} qnCharacterId_t;

// ============================================================================
// Character Definition Structure
// ============================================================================
typedef struct {
	qnCharacterId_t id;
	const char      *displayName;   // Shown in UI: "Mister Chef"
	const char      *modelName;     // Folder under models/players/: "chef"
	const char      *shortName;     // For kill feed: "Chef"
	const char      *description;   // Flavor text for selection screen
	float           visualScale;    // Cosmetic only (0.85 - 1.1), hitbox unchanged
} qnCharacterDef_t;

// ============================================================================
// Public API
// ============================================================================

// Clamp an integer to valid character ID range [0, QN_NUM_CHARACTERS-1]
int BG_QN_ClampCharacterId( int id );

// Get the full character definition struct, or NULL if invalid
const qnCharacterDef_t *BG_QN_GetCharacterDef( int id );

// Convenience accessors
const char *BG_QN_GetCharacterModelName( int id );
const char *BG_QN_GetCharacterDisplayName( int id );
const char *BG_QN_GetCharacterShortName( int id );
const char *BG_QN_GetCharacterDescription( int id );

// Get character ID from model name (e.g., "chef" -> QN_CHAR_MISTER_CHEF)
// Returns -1 if not found
int BG_QN_GetCharacterIdByModelName( const char *modelName );

// Build a model path with team skin: "<modelName>/<skinName>"
// skinName should be "default", "red", "blue", "green", or "yellow"
void BG_QN_BuildModelPath( int characterId, const char *skinName, char *outPath, int outPathSize );

#endif // BG_QN_CHARACTERS_H
