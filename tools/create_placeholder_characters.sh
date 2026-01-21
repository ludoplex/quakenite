#!/bin/bash
#
# QuakeNite Placeholder Character Generator
#
# This script extracts the default RTCW multiplayer model and creates
# placeholder copies for all 9 QuakeNite characters, allowing the game
# to be tested before custom character models are created.
#
# Usage: ./create_placeholder_characters.sh /path/to/rtcw/main
#
# Requirements:
# - RTCW installed with pak0.pk3
# - unzip command available
#

set -e

# QuakeNite character model folder names (must match bg_qn_characters.c)
CHARACTERS=(
    "chef"        # Mister Chef
    "blitz"       # Blitz
    "willylee"    # Willy Lee
    "steelheim"   # Steelheim
    "holster"     # Holster Colt
    "six"         # Number Six
    "serpent"     # Solid Serpent
    "blastem"     # Dude Blastem
    "matthias"    # Sir Matthias
)

# Team skin colors
SKINS=("default" "red" "blue")

print_usage() {
    echo "Usage: $0 <rtcw_main_folder> [output_pk3]"
    echo ""
    echo "Arguments:"
    echo "  rtcw_main_folder  Path to RTCW's main/ folder containing pak0.pk3"
    echo "  output_pk3        Output pk3 filename (default: qn_placeholder_characters.pk3)"
    echo ""
    echo "Example:"
    echo "  $0 ~/.wolf/main"
    echo "  $0 /opt/rtcw/main qn_chars.pk3"
}

if [ $# -lt 1 ]; then
    print_usage
    exit 1
fi

RTCW_MAIN="$1"
OUTPUT_PK3="${2:-qn_placeholder_characters.pk3}"

# Verify pak0.pk3 exists
if [ ! -f "$RTCW_MAIN/pak0.pk3" ]; then
    echo "Error: pak0.pk3 not found in $RTCW_MAIN"
    echo "Make sure you have RTCW installed and point to its main/ folder."
    exit 1
fi

# Create temp working directory
WORKDIR=$(mktemp -d)
trap "rm -rf $WORKDIR" EXIT

echo "=== QuakeNite Placeholder Character Generator ==="
echo "RTCW main folder: $RTCW_MAIN"
echo "Output: $OUTPUT_PK3"
echo "Working directory: $WORKDIR"
echo ""

# Extract the multi model from pak0.pk3
echo "[1/4] Extracting base model from pak0.pk3..."
cd "$WORKDIR"
unzip -q "$RTCW_MAIN/pak0.pk3" "models/players/multi/*" 2>/dev/null || {
    # Try multi_axis if multi doesn't exist
    unzip -q "$RTCW_MAIN/pak0.pk3" "models/players/multi_axis/*" 2>/dev/null || {
        echo "Error: Could not find multiplayer model in pak0.pk3"
        exit 1
    }
    # Rename to multi for consistency
    mv models/players/multi_axis models/players/multi
}

echo "[2/4] Creating character folders..."
for char in "${CHARACTERS[@]}"; do
    echo "  - $char"
    mkdir -p "models/players/$char"

    # Copy all model files
    cp models/players/multi/*.md3 "models/players/$char/" 2>/dev/null || true
    cp models/players/multi/*.mdc "models/players/$char/" 2>/dev/null || true
    cp models/players/multi/*.cfg "models/players/$char/" 2>/dev/null || true
    cp models/players/multi/*.tga "models/players/$char/" 2>/dev/null || true
    cp models/players/multi/*.jpg "models/players/$char/" 2>/dev/null || true
done

echo "[3/4] Creating skin files..."
for char in "${CHARACTERS[@]}"; do
    for skin in "${SKINS[@]}"; do
        # Copy existing skin or create from default
        if [ -f "models/players/multi/${skin}.skin" ]; then
            cp "models/players/multi/${skin}.skin" "models/players/$char/${skin}.skin"
        elif [ -f "models/players/multi/default.skin" ]; then
            cp "models/players/multi/default.skin" "models/players/$char/${skin}.skin"
        fi
    done

    # Create icon if it doesn't exist
    if [ -f "models/players/multi/icon_default.tga" ]; then
        cp "models/players/multi/icon_default.tga" "models/players/$char/icon_default.tga"
    fi
done

# Remove the source multi folder (not needed in output)
rm -rf models/players/multi

echo "[4/4] Creating pk3 file..."
cd "$WORKDIR"
zip -r -q "$OUTPUT_PK3" models/

# Move to original directory
mv "$OUTPUT_PK3" "$OLDPWD/"
cd "$OLDPWD"

echo ""
echo "=== Done! ==="
echo "Created: $OUTPUT_PK3"
echo ""
echo "To use:"
echo "  1. Copy $OUTPUT_PK3 to your RTCW/main/ folder"
echo "  2. Run QuakeNite"
echo "  3. Set character with: /qn_char 0-8"
echo ""
echo "Characters:"
echo "  0 = Mister Chef     5 = Number Six"
echo "  1 = Blitz           6 = Solid Serpent"
echo "  2 = Willy Lee       7 = Dude Blastem"
echo "  3 = Steelheim       8 = Sir Matthias"
echo "  4 = Holster Colt"
