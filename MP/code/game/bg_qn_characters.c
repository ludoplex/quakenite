/*
===========================================================================
QuakeNite Character Roster System - Implementation

Contains the 9 character definitions and helper functions.
===========================================================================
*/

#include "../qcommon/q_shared.h"
#include "bg_public.h"
#include "bg_qn_characters.h"

// ============================================================================
// Character Roster Definitions
// ============================================================================
static const qnCharacterDef_t qn_characters[QN_NUM_CHARACTERS] = {
	// QN_CHAR_MISTER_CHEF - Master Chief parody
	{
		QN_CHAR_MISTER_CHEF,
		"Mister Chef",
		"chef",
		"Chef",
		"Supersoldier. Supercook. Superviolent.",
		1.1f
	},

	// QN_CHAR_BLITZ - Battletoads parody
	{
		QN_CHAR_BLITZ,
		"Blitz",
		"blitz",
		"Blitz",
		"The toad with the 'tude.",
		0.9f
	},

	// QN_CHAR_WILLY_LEE - Double Dragon parody
	{
		QN_CHAR_WILLY_LEE,
		"Willy Lee",
		"willylee",
		"Willy",
		"Streets taught him everything.",
		1.0f
	},

	// QN_CHAR_STEELHEIM - Stroheim/JoJo parody
	{
		QN_CHAR_STEELHEIM,
		"Steelheim",
		"steelheim",
		"Steelheim",
		"SCIENCE IS THE WORLD'S FINEST!",
		1.05f
	},

	// QN_CHAR_HOLSTER_COLT - Hol Horse/JoJo parody
	{
		QN_CHAR_HOLSTER_COLT,
		"Holster Colt",
		"holster",
		"Holster",
		"Fastest finger in the West.",
		1.0f
	},

	// QN_CHAR_NUMBER_SIX - Guido Mista/JoJo parody
	{
		QN_CHAR_NUMBER_SIX,
		"Number Six",
		"six",
		"Six",
		"Don't say that number.",
		1.0f
	},

	// QN_CHAR_SOLID_SERPENT - Metal Gear parody
	{
		QN_CHAR_SOLID_SERPENT,
		"Solid Serpent",
		"serpent",
		"Serpent",
		"Stealth is optional.",
		1.0f
	},

	// QN_CHAR_DUDE_BLASTEM - Duke Nukem/Doom parody
	{
		QN_CHAR_DUDE_BLASTEM,
		"Dude Blastem",
		"blastem",
		"Dude",
		"90s action hero energy, max volume.",
		1.1f
	},

	// QN_CHAR_SIR_MATTHIAS - Redwall parody
	{
		QN_CHAR_SIR_MATTHIAS,
		"Sir Matthias",
		"matthias",
		"Matthias",
		"Woodland knight in a gunfight.",
		0.85f
	}
};

// ============================================================================
// Public API Implementation
// ============================================================================

/*
==================
BG_QN_ClampCharacterId

Clamp an integer to valid character ID range [0, QN_NUM_CHARACTERS-1]
==================
*/
int BG_QN_ClampCharacterId( int id ) {
	if ( id < 0 ) {
		return 0;
	}
	if ( id >= QN_NUM_CHARACTERS ) {
		return QN_NUM_CHARACTERS - 1;
	}
	return id;
}

/*
==================
BG_QN_GetCharacterDef

Get the full character definition struct, or NULL if invalid
==================
*/
const qnCharacterDef_t *BG_QN_GetCharacterDef( int id ) {
	if ( id < 0 || id >= QN_NUM_CHARACTERS ) {
		return NULL;
	}
	return &qn_characters[id];
}

/*
==================
BG_QN_GetCharacterModelName

Returns the model folder name (e.g., "chef")
==================
*/
const char *BG_QN_GetCharacterModelName( int id ) {
	const qnCharacterDef_t *def = BG_QN_GetCharacterDef( id );
	if ( !def ) {
		return "chef";  // fallback to first character
	}
	return def->modelName;
}

/*
==================
BG_QN_GetCharacterDisplayName

Returns the display name (e.g., "Mister Chef")
==================
*/
const char *BG_QN_GetCharacterDisplayName( int id ) {
	const qnCharacterDef_t *def = BG_QN_GetCharacterDef( id );
	if ( !def ) {
		return "Mister Chef";
	}
	return def->displayName;
}

/*
==================
BG_QN_GetCharacterShortName

Returns the short name for kill feed (e.g., "Chef")
==================
*/
const char *BG_QN_GetCharacterShortName( int id ) {
	const qnCharacterDef_t *def = BG_QN_GetCharacterDef( id );
	if ( !def ) {
		return "Chef";
	}
	return def->shortName;
}

/*
==================
BG_QN_GetCharacterDescription

Returns the flavor text description
==================
*/
const char *BG_QN_GetCharacterDescription( int id ) {
	const qnCharacterDef_t *def = BG_QN_GetCharacterDef( id );
	if ( !def ) {
		return "";
	}
	return def->description;
}

/*
==================
BG_QN_GetCharacterIdByModelName

Get character ID from model name (e.g., "chef" -> QN_CHAR_MISTER_CHEF)
Returns -1 if not found
==================
*/
int BG_QN_GetCharacterIdByModelName( const char *modelName ) {
	int i;

	if ( !modelName || !modelName[0] ) {
		return -1;
	}

	for ( i = 0; i < QN_NUM_CHARACTERS; i++ ) {
		if ( Q_stricmp( modelName, qn_characters[i].modelName ) == 0 ) {
			return i;
		}
	}

	return -1;
}

/*
==================
BG_QN_BuildModelPath

Build a model path with team skin: "<modelName>/<skinName>"
Example: BG_QN_BuildModelPath(QN_CHAR_MISTER_CHEF, "red", buf, sizeof(buf))
         -> "chef/red"
==================
*/
void BG_QN_BuildModelPath( int characterId, const char *skinName, char *outPath, int outPathSize ) {
	const char *modelName;

	modelName = BG_QN_GetCharacterModelName( characterId );

	if ( !skinName || !skinName[0] ) {
		skinName = "default";
	}

	Com_sprintf( outPath, outPathSize, "%s/%s", modelName, skinName );
}
