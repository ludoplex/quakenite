#!/usr/bin/env python3
"""
MD3 file format reader/writer for id Tech 3 models.

Based on the MD3 specification:
- Magic: IDP3 (0x33504449)
- Version: 15
- Vertex positions scaled by 64
- Normals encoded as lat/lng bytes
"""

import struct
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional


# Constants
MD3_IDENT = 0x33504449  # "IDP3"
MD3_VERSION = 15
MD3_XYZ_SCALE = 1.0 / 64.0
MD3_MAX_FRAMES = 1024
MD3_MAX_TAGS = 16
MD3_MAX_SURFACES = 32
MD3_MAX_VERTS = 4096
MD3_MAX_TRIANGLES = 8192


@dataclass
class Vec3:
    """3D vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, i):
        return [self.x, self.y, self.z][i]


@dataclass
class MD3Frame:
    """Animation frame bounds."""
    min_bounds: Vec3 = field(default_factory=Vec3)
    max_bounds: Vec3 = field(default_factory=Vec3)
    local_origin: Vec3 = field(default_factory=Vec3)
    radius: float = 0.0
    name: str = ""


@dataclass
class MD3Tag:
    """Attachment point for other models."""
    name: str = ""
    origin: Vec3 = field(default_factory=Vec3)
    axis: List[Vec3] = field(default_factory=lambda: [Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1)])


@dataclass
class MD3Shader:
    """Surface shader/texture reference."""
    name: str = ""
    shader_index: int = 0


@dataclass
class MD3Triangle:
    """Triangle face indices."""
    indices: Tuple[int, int, int] = (0, 0, 0)


@dataclass
class MD3TexCoord:
    """UV texture coordinate."""
    s: float = 0.0
    t: float = 0.0


@dataclass
class MD3Vertex:
    """Vertex with position and normal."""
    position: Vec3 = field(default_factory=Vec3)
    normal: Vec3 = field(default_factory=Vec3)


@dataclass
class MD3Surface:
    """Mesh surface with geometry and textures."""
    name: str = ""
    flags: int = 0
    num_frames: int = 1
    shaders: List[MD3Shader] = field(default_factory=list)
    triangles: List[MD3Triangle] = field(default_factory=list)
    tex_coords: List[MD3TexCoord] = field(default_factory=list)
    vertices: List[List[MD3Vertex]] = field(default_factory=list)  # [frame][vertex]


@dataclass
class MD3Model:
    """Complete MD3 model."""
    name: str = ""
    flags: int = 0
    frames: List[MD3Frame] = field(default_factory=list)
    tags: List[List[MD3Tag]] = field(default_factory=list)  # [frame][tag]
    surfaces: List[MD3Surface] = field(default_factory=list)


def decode_normal(zenith: int, azimuth: int) -> Vec3:
    """Decode compressed normal from lat/lng bytes."""
    lat = zenith * (2.0 * math.pi) / 255.0
    lng = azimuth * (2.0 * math.pi) / 255.0

    return Vec3(
        x=math.cos(lat) * math.sin(lng),
        y=math.sin(lat) * math.sin(lng),
        z=math.cos(lng)
    )


def encode_normal(nx: float, ny: float, nz: float) -> Tuple[int, int]:
    """Encode normal to lat/lng bytes."""
    # Handle edge cases
    length = math.sqrt(nx*nx + ny*ny + nz*nz)
    if length < 0.001:
        return (0, 0)

    nx, ny, nz = nx/length, ny/length, nz/length
    nz = max(-1.0, min(1.0, nz))

    lng = math.acos(nz)
    lat = math.atan2(ny, nx)

    if lat < 0:
        lat += 2.0 * math.pi

    zenith = int(lat * 255.0 / (2.0 * math.pi)) & 0xFF
    azimuth = int(lng * 255.0 / (2.0 * math.pi)) & 0xFF

    return (zenith, azimuth)


def _read_string(data: bytes, offset: int, max_len: int) -> str:
    """Read null-terminated string from buffer."""
    end = offset + max_len
    raw = data[offset:end]
    null_pos = raw.find(b'\x00')
    if null_pos != -1:
        raw = raw[:null_pos]
    return raw.decode('ascii', errors='replace')


def _write_string(s: str, max_len: int) -> bytes:
    """Write null-padded string to buffer."""
    encoded = s.encode('ascii', errors='replace')[:max_len - 1]
    return encoded.ljust(max_len, b'\x00')


def read_md3(filepath: Path) -> MD3Model:
    """Read and parse an MD3 file."""
    with open(filepath, 'rb') as f:
        data = f.read()

    model = MD3Model()

    # Parse header
    ident, version = struct.unpack_from('<2i', data, 0)

    if ident != MD3_IDENT:
        raise ValueError(f"Invalid MD3 ident: {ident:#x}, expected {MD3_IDENT:#x}")
    if version != MD3_VERSION:
        raise ValueError(f"Invalid MD3 version: {version}, expected {MD3_VERSION}")

    model.name = _read_string(data, 8, 64)

    (
        model.flags, num_frames, num_tags, num_surfaces, num_skins,
        ofs_frames, ofs_tags, ofs_surfaces, ofs_end
    ) = struct.unpack_from('<9i', data, 72)

    # Parse frames
    offset = ofs_frames
    for _ in range(num_frames):
        frame = MD3Frame()
        floats = struct.unpack_from('<10f', data, offset)
        frame.min_bounds = Vec3(*floats[0:3])
        frame.max_bounds = Vec3(*floats[3:6])
        frame.local_origin = Vec3(*floats[6:9])
        frame.radius = floats[9]
        frame.name = _read_string(data, offset + 40, 16)
        model.frames.append(frame)
        offset += 56

    # Parse tags (num_tags per frame)
    offset = ofs_tags
    for frame_idx in range(num_frames):
        frame_tags = []
        for _ in range(num_tags):
            tag = MD3Tag()
            tag.name = _read_string(data, offset, 64)
            floats = struct.unpack_from('<12f', data, offset + 64)
            tag.origin = Vec3(*floats[0:3])
            tag.axis = [
                Vec3(*floats[3:6]),
                Vec3(*floats[6:9]),
                Vec3(*floats[9:12])
            ]
            frame_tags.append(tag)
            offset += 112
        model.tags.append(frame_tags)

    # Parse surfaces
    surf_offset = ofs_surfaces
    for _ in range(num_surfaces):
        surf = MD3Surface()

        # Surface header
        surf_ident, = struct.unpack_from('<i', surf_offset, 0)
        if surf_ident != MD3_IDENT:
            # Try reading from data instead
            surf_ident, = struct.unpack_from('<i', data, surf_offset)

        surf.name = _read_string(data, surf_offset + 4, 64)

        (
            surf.flags, surf.num_frames, num_shaders, num_verts, num_tris,
            ofs_tris, ofs_shaders, ofs_st, ofs_xyz, ofs_end
        ) = struct.unpack_from('<10i', data, surf_offset + 68)

        # Shaders
        offset = surf_offset + ofs_shaders
        for _ in range(num_shaders):
            shader = MD3Shader()
            shader.name = _read_string(data, offset, 64)
            shader.shader_index, = struct.unpack_from('<i', data, offset + 64)
            surf.shaders.append(shader)
            offset += 68

        # Triangles
        offset = surf_offset + ofs_tris
        for _ in range(num_tris):
            indices = struct.unpack_from('<3i', data, offset)
            surf.triangles.append(MD3Triangle(indices=indices))
            offset += 12

        # Texture coordinates
        offset = surf_offset + ofs_st
        for _ in range(num_verts):
            s, t = struct.unpack_from('<2f', data, offset)
            surf.tex_coords.append(MD3TexCoord(s=s, t=t))
            offset += 8

        # Vertices (per frame)
        offset = surf_offset + ofs_xyz
        for frame_idx in range(surf.num_frames):
            frame_verts = []
            for _ in range(num_verts):
                xyz = struct.unpack_from('<3h', data, offset)
                normal_bytes = struct.unpack_from('<2B', data, offset + 6)

                vert = MD3Vertex()
                vert.position = Vec3(
                    x=xyz[0] * MD3_XYZ_SCALE,
                    y=xyz[1] * MD3_XYZ_SCALE,
                    z=xyz[2] * MD3_XYZ_SCALE
                )
                vert.normal = decode_normal(normal_bytes[0], normal_bytes[1])
                frame_verts.append(vert)
                offset += 8
            surf.vertices.append(frame_verts)

        model.surfaces.append(surf)
        surf_offset += ofs_end

    return model


def write_md3(model: MD3Model, filepath: Path):
    """Write an MD3 model to file."""
    num_frames = len(model.frames) if model.frames else 1
    num_tags = len(model.tags[0]) if model.tags and model.tags[0] else 0
    num_surfaces = len(model.surfaces)

    # Calculate offsets
    header_size = 108
    frame_size = 56
    tag_size = 112

    ofs_frames = header_size
    ofs_tags = ofs_frames + (frame_size * num_frames)
    ofs_surfaces = ofs_tags + (tag_size * num_tags * num_frames)

    # Build output buffer
    output = bytearray()

    # Write header (placeholder for ofs_end)
    output.extend(struct.pack('<2i', MD3_IDENT, MD3_VERSION))
    output.extend(_write_string(model.name, 64))
    output.extend(struct.pack(
        '<9i',
        model.flags, num_frames, num_tags, num_surfaces, 0,
        ofs_frames, ofs_tags, ofs_surfaces, 0  # ofs_end placeholder
    ))

    # Write frames
    for frame in model.frames:
        output.extend(struct.pack(
            '<10f',
            frame.min_bounds.x, frame.min_bounds.y, frame.min_bounds.z,
            frame.max_bounds.x, frame.max_bounds.y, frame.max_bounds.z,
            frame.local_origin.x, frame.local_origin.y, frame.local_origin.z,
            frame.radius
        ))
        output.extend(_write_string(frame.name, 16))

    # Write tags
    for frame_tags in model.tags:
        for tag in frame_tags:
            output.extend(_write_string(tag.name, 64))
            output.extend(struct.pack('<3f', tag.origin.x, tag.origin.y, tag.origin.z))
            for axis in tag.axis:
                output.extend(struct.pack('<3f', axis.x, axis.y, axis.z))

    # Write surfaces
    for surf in model.surfaces:
        surf_start = len(output)

        num_shaders = len(surf.shaders)
        num_tris = len(surf.triangles)
        num_verts = len(surf.tex_coords)
        surf_num_frames = len(surf.vertices) if surf.vertices else 1

        # Calculate surface-relative offsets
        surface_header_size = 108
        shader_size = 68
        triangle_size = 12
        texcoord_size = 8
        vertex_size = 8

        ofs_shaders = surface_header_size
        ofs_tris = ofs_shaders + (shader_size * num_shaders)
        ofs_st = ofs_tris + (triangle_size * num_tris)
        ofs_xyz = ofs_st + (texcoord_size * num_verts)
        ofs_end = ofs_xyz + (vertex_size * num_verts * surf_num_frames)

        # Surface header
        output.extend(struct.pack('<i', MD3_IDENT))
        output.extend(_write_string(surf.name, 64))
        output.extend(struct.pack(
            '<10i',
            surf.flags, surf_num_frames, num_shaders, num_verts, num_tris,
            ofs_tris, ofs_shaders, ofs_st, ofs_xyz, ofs_end
        ))

        # Shaders
        for shader in surf.shaders:
            output.extend(_write_string(shader.name, 64))
            output.extend(struct.pack('<i', shader.shader_index))

        # Triangles
        for tri in surf.triangles:
            output.extend(struct.pack('<3i', *tri.indices))

        # Texture coordinates
        for tc in surf.tex_coords:
            output.extend(struct.pack('<2f', tc.s, tc.t))

        # Vertices
        for frame_verts in surf.vertices:
            for vert in frame_verts:
                xyz = (
                    int(vert.position.x / MD3_XYZ_SCALE),
                    int(vert.position.y / MD3_XYZ_SCALE),
                    int(vert.position.z / MD3_XYZ_SCALE)
                )
                # Clamp to 16-bit signed range
                xyz = tuple(max(-32768, min(32767, v)) for v in xyz)
                normal = encode_normal(vert.normal.x, vert.normal.y, vert.normal.z)
                output.extend(struct.pack('<3h2B', *xyz, *normal))

    # Update ofs_end in header
    ofs_end = len(output)
    struct.pack_into('<i', output, 104, ofs_end)

    # Write to file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(output)


def print_md3_info(model: MD3Model):
    """Print summary of MD3 model."""
    print(f"MD3 Model: {model.name}")
    print(f"  Frames: {len(model.frames)}")
    print(f"  Tags: {len(model.tags[0]) if model.tags else 0}")
    print(f"  Surfaces: {len(model.surfaces)}")
    print()

    if model.tags and model.tags[0]:
        print("  Tags (frame 0):")
        for tag in model.tags[0]:
            print(f"    - {tag.name}: origin=({tag.origin.x:.2f}, {tag.origin.y:.2f}, {tag.origin.z:.2f})")
        print()

    for i, surf in enumerate(model.surfaces):
        print(f"  Surface {i}: {surf.name}")
        print(f"    Shaders: {[s.name for s in surf.shaders]}")
        print(f"    Triangles: {len(surf.triangles)}")
        print(f"    Vertices: {len(surf.tex_coords)}")
        print(f"    Frames: {len(surf.vertices)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <model.md3>")
        sys.exit(1)

    model = read_md3(Path(sys.argv[1]))
    print_md3_info(model)
