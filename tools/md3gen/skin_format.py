#!/usr/bin/env python3
"""
Skin file generator for id Tech 3 player models.

Skin files are text files that map surface names to texture paths:
    surface_name,texture_path

Example:
    h_head,models/players/chef/head.tga
    u_torso,models/players/chef/upper.tga
    tag_head,
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SkinMapping:
    """Surface to texture mapping."""
    surface: str
    texture: str


def write_skin_file(filepath: Path, mappings: List[SkinMapping]):
    """Write a .skin file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        for m in mappings:
            f.write(f"{m.surface},{m.texture}\n")


def read_skin_file(filepath: Path) -> List[SkinMapping]:
    """Read a .skin file."""
    mappings = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            parts = line.split(',', 1)
            if len(parts) == 2:
                mappings.append(SkinMapping(surface=parts[0], texture=parts[1]))
            elif len(parts) == 1:
                mappings.append(SkinMapping(surface=parts[0], texture=''))
    return mappings


# =============================================================================
# Standard Player Model Surfaces
# =============================================================================

# Standard Q3/RTCW player model surfaces
STANDARD_SURFACES = {
    # Head
    "h_head": "head",
    "h_helmet": "head",
    # Upper body (torso)
    "u_torso": "upper",
    "u_arms": "upper",
    "u_chest": "upper",
    # Lower body (legs)
    "l_legs": "lower",
    "l_waist": "lower",
    "l_skirt": "lower",
}

# Standard tags (attachment points, no texture)
STANDARD_TAGS = [
    "tag_head",
    "tag_torso",
    "tag_weapon",
]


def generate_player_skins(
    character: str,
    surfaces: Optional[Dict[str, str]] = None,
    tags: Optional[List[str]] = None,
    output_dir: Optional[Path] = None,
    variants: Optional[Dict[str, str]] = None
) -> Dict[str, Path]:
    """
    Generate skin files for a character with team variants.

    Args:
        character: Character folder name (e.g., "chef")
        surfaces: Dict mapping surface names to body parts (e.g., {"h_head": "head"})
        tags: List of tag names (no texture)
        output_dir: Output directory for skin files
        variants: Dict mapping variant name to texture suffix (e.g., {"red": "_red"})

    Returns:
        Dict mapping variant names to generated file paths
    """
    if surfaces is None:
        surfaces = STANDARD_SURFACES
    if tags is None:
        tags = STANDARD_TAGS
    if output_dir is None:
        output_dir = Path(f"models/players/{character}")
    if variants is None:
        variants = {
            "default": "",
            "red": "_red",
            "blue": "_blue"
        }

    base_tex_path = f"models/players/{character}"
    generated_files = {}

    for variant_name, suffix in variants.items():
        mappings = []

        # Surface to texture mappings
        for surface, body_part in surfaces.items():
            texture = f"{base_tex_path}/{body_part}{suffix}.tga"
            mappings.append(SkinMapping(surface=surface, texture=texture))

        # Tags (empty texture path)
        for tag in tags:
            mappings.append(SkinMapping(surface=tag, texture=""))

        filepath = output_dir / f"{variant_name}.skin"
        write_skin_file(filepath, mappings)
        generated_files[variant_name] = filepath

    return generated_files


def generate_simple_skin(
    surface_name: str,
    texture_path: str,
    output_path: Path
):
    """Generate a simple single-surface skin file."""
    mappings = [SkinMapping(surface=surface_name, texture=texture_path)]
    write_skin_file(output_path, mappings)


if __name__ == "__main__":
    # Generate test skin files
    output_dir = Path("test_skins")

    # Generate skins for test character
    files = generate_player_skins(
        character="test_char",
        output_dir=output_dir / "test_char"
    )

    for variant, path in files.items():
        print(f"Generated {path}")

    # Show example content
    print("\nExample default.skin content:")
    with open(files["default"], 'r') as f:
        print(f.read())
