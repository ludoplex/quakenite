#!/usr/bin/env python3
"""
Animation config (animation.cfg) generator for id Tech 3 player models.

Format:
    sex [m/f/n]
    footsteps [normal/boot/flesh/mech/energy]
    headoffset X Y Z
    ANIM_NAME first_frame num_frames looping_frames fps [// comment]
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class FootstepType(Enum):
    """Footstep sound type."""
    NORMAL = "normal"
    BOOT = "boot"
    FLESH = "flesh"
    MECH = "mech"
    ENERGY = "energy"


class Sex(Enum):
    """Voice type."""
    MALE = "m"
    FEMALE = "f"
    NEUTER = "n"


@dataclass
class Animation:
    """Single animation definition."""
    name: str
    first_frame: int
    num_frames: int
    looping_frames: int
    fps: int
    comment: str = ""


@dataclass
class AnimationConfig:
    """Complete animation configuration."""
    sex: Sex = Sex.MALE
    footsteps: FootstepType = FootstepType.BOOT
    head_offset: tuple = (0, 0, 0)
    animations: List[Animation] = field(default_factory=list)


def create_standard_animations(base_frame: int = 0) -> List[Animation]:
    """
    Create standard Q3/RTCW animation set.

    Standard animation indices:
    0-5: BOTH_DEATH1-3, DEAD1-3 (full body deaths)
    6-13: TORSO_* (upper body)
    14-30: LEGS_* (lower body)
    """
    frame = base_frame
    anims = []

    def add(name, num_frames, looping, fps, comment=""):
        nonlocal frame
        anims.append(Animation(name, frame, num_frames, looping, fps, comment))
        frame += num_frames

    # BOTH (death) animations - full body
    add("BOTH_DEATH1", 30, 0, 20, "Death forward")
    add("BOTH_DEAD1", 1, 0, 20, "Dead pose 1")
    add("BOTH_DEATH2", 30, 0, 20, "Death backward")
    add("BOTH_DEAD2", 1, 0, 20, "Dead pose 2")
    add("BOTH_DEATH3", 30, 0, 20, "Death spin")
    add("BOTH_DEAD3", 1, 0, 20, "Dead pose 3")

    # TORSO animations - upper body
    add("TORSO_GESTURE", 30, 0, 20, "Taunt")
    add("TORSO_ATTACK", 8, 0, 20, "Primary fire")
    add("TORSO_ATTACK2", 8, 0, 20, "Alt fire")
    add("TORSO_DROP", 5, 0, 20, "Lower weapon")
    add("TORSO_RAISE", 5, 0, 20, "Raise weapon")
    add("TORSO_STAND", 30, 30, 20, "Idle armed")
    add("TORSO_STAND2", 30, 30, 20, "Idle unarmed")

    # LEGS animations - lower body
    add("LEGS_WALKCR", 10, 10, 15, "Crouch walk")
    add("LEGS_WALK", 12, 12, 20, "Walk")
    add("LEGS_RUN", 10, 10, 24, "Run")
    add("LEGS_BACK", 10, 10, 20, "Backpedal")
    add("LEGS_SWIM", 10, 10, 20, "Swim")
    add("LEGS_JUMP", 8, 0, 20, "Jump")
    add("LEGS_LAND", 4, 0, 20, "Land")
    add("LEGS_JUMPB", 8, 0, 20, "Jump back")
    add("LEGS_LANDB", 4, 0, 20, "Land back")
    add("LEGS_IDLE", 30, 30, 20, "Idle")
    add("LEGS_IDLECR", 30, 30, 20, "Crouch idle")
    add("LEGS_TURN", 10, 10, 20, "Turn")

    return anims


def write_animation_cfg(config: AnimationConfig, filepath: Path):
    """Write animation.cfg file."""
    lines = [
        "// Animation config generated for id Tech 3",
        "// Format: ANIM_NAME first_frame num_frames looping_frames fps",
        "",
        f"sex {config.sex.value}",
        f"footsteps {config.footsteps.value}",
        f"headoffset {config.head_offset[0]} {config.head_offset[1]} {config.head_offset[2]}",
        ""
    ]

    current_prefix = None
    for anim in config.animations:
        # Add section comment when prefix changes
        prefix = anim.name.split('_')[0]
        if prefix != current_prefix:
            if current_prefix is not None:
                lines.append("")
            lines.append(f"// {prefix} animations")
            current_prefix = prefix

        comment = f"// {anim.comment}" if anim.comment else ""
        line = f"{anim.name:<20}{anim.first_frame:<8}{anim.num_frames:<8}{anim.looping_frames:<8}{anim.fps:<8}{comment}"
        lines.append(line.rstrip())

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def read_animation_cfg(filepath: Path) -> AnimationConfig:
    """Read an animation.cfg file."""
    config = AnimationConfig()

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue

            parts = line.split()
            if not parts:
                continue

            keyword = parts[0].lower()

            if keyword == 'sex':
                config.sex = Sex(parts[1])
            elif keyword == 'footsteps':
                config.footsteps = FootstepType(parts[1])
            elif keyword == 'headoffset':
                config.head_offset = (int(parts[1]), int(parts[2]), int(parts[3]))
            elif keyword.startswith(('both_', 'torso_', 'legs_')):
                # Animation line
                name = parts[0]
                first_frame = int(parts[1])
                num_frames = int(parts[2])
                looping_frames = int(parts[3])
                fps = int(parts[4])

                # Extract comment if present
                comment = ""
                if '//' in line:
                    comment = line.split('//', 1)[1].strip()

                config.animations.append(Animation(
                    name=name,
                    first_frame=first_frame,
                    num_frames=num_frames,
                    looping_frames=looping_frames,
                    fps=fps,
                    comment=comment
                ))

    return config


# =============================================================================
# Character-Specific Settings
# =============================================================================

CHARACTER_SETTINGS = {
    "chef": {"sex": Sex.MALE, "footsteps": FootstepType.BOOT},
    "blitz": {"sex": Sex.MALE, "footsteps": FootstepType.FLESH},
    "willylee": {"sex": Sex.MALE, "footsteps": FootstepType.NORMAL},
    "steelheim": {"sex": Sex.MALE, "footsteps": FootstepType.MECH},
    "holster": {"sex": Sex.MALE, "footsteps": FootstepType.BOOT},
    "six": {"sex": Sex.MALE, "footsteps": FootstepType.NORMAL},
    "serpent": {"sex": Sex.MALE, "footsteps": FootstepType.BOOT},
    "blastem": {"sex": Sex.MALE, "footsteps": FootstepType.BOOT},
    "matthias": {"sex": Sex.MALE, "footsteps": FootstepType.NORMAL},
}


def generate_character_animation_cfg(
    character: str,
    output_dir: Optional[Path] = None
) -> Path:
    """Generate animation.cfg for a QuakeNite character."""
    settings = CHARACTER_SETTINGS.get(character, {"sex": Sex.MALE, "footsteps": FootstepType.NORMAL})

    config = AnimationConfig(
        sex=settings["sex"],
        footsteps=settings["footsteps"],
        head_offset=(0, 0, 0),
        animations=create_standard_animations()
    )

    if output_dir is None:
        output_dir = Path(f"models/players/{character}")

    filepath = output_dir / "animation.cfg"
    write_animation_cfg(config, filepath)
    return filepath


if __name__ == "__main__":
    # Generate test animation config
    output_dir = Path("test_anims")

    for char in CHARACTER_SETTINGS.keys():
        filepath = generate_character_animation_cfg(char, output_dir / char)
        print(f"Generated {filepath}")

    # Show example content
    print("\nExample animation.cfg content:")
    with open(output_dir / "chef" / "animation.cfg", 'r') as f:
        print(f.read()[:1000] + "...")
