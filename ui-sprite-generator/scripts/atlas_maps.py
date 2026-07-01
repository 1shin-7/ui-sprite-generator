"""Helpers for legacy atlas maps and per-atlas crop maps."""

from pathlib import Path

from data_io import DataIOError, load_data


class AtlasMapError(Exception):
    pass


MAP_SUFFIXES = (".map.yaml", ".map.yml", ".map.json")


def is_per_atlas_map(path):
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in MAP_SUFFIXES)


def per_atlas_map_paths(atlas_dir):
    directory = Path(atlas_dir)
    if not directory.exists():
        raise AtlasMapError(f"atlas directory not found: {directory}")
    paths = sorted(path for path in directory.iterdir() if path.is_file() and is_per_atlas_map(path))
    if not paths:
        raise AtlasMapError(f"no per-atlas map files found in: {directory}")
    return paths


def resolve_path(base_dir, value):
    path = Path(value)
    if path.is_absolute():
        return path
    return base_dir / path


def load_data_or_error(path):
    try:
        return load_data(path)
    except DataIOError as exc:
        raise AtlasMapError(str(exc)) from exc


def normalize_legacy_atlas_map(atlas_map):
    return {
        "schema_version": atlas_map.get("schema_version", "1.0"),
        "atlases": list(atlas_map.get("atlases", [])),
        "sprites": list(atlas_map.get("sprites", [])),
    }


def load_legacy_atlas_map(map_path):
    return normalize_legacy_atlas_map(load_data_or_error(map_path))


def load_per_atlas_maps(atlas_dir, require_atlas_files=True):
    atlases = []
    sprites = []
    seen_atlas_ids = set()

    for map_path in per_atlas_map_paths(atlas_dir):
        data = load_data_or_error(map_path)
        atlas = data.get("atlas", {})
        atlas_id = atlas.get("id")
        atlas_file = atlas.get("file")
        if not atlas_id or not atlas_file:
            raise AtlasMapError(f"{map_path.name}: atlas.id and atlas.file are required")
        if atlas_id in seen_atlas_ids:
            raise AtlasMapError(f"duplicate atlas id: {atlas_id}")
        seen_atlas_ids.add(atlas_id)

        atlas_path = resolve_path(map_path.parent, atlas_file)
        if require_atlas_files and not atlas_path.exists():
            raise AtlasMapError(f"{map_path.name}: atlas file not found: {atlas_path}")
        atlases.append({"id": atlas_id, "file": str(atlas_path)})

        map_sprites = data.get("sprites", [])
        if not map_sprites:
            raise AtlasMapError(f"{map_path.name}: no sprites")
        for sprite in map_sprites:
            normalized = dict(sprite)
            sprite_atlas = normalized.get("atlas")
            if sprite_atlas and sprite_atlas != atlas_id:
                raise AtlasMapError(f"{map_path.name}: {normalized.get('id', '<unknown>')}: atlas must be {atlas_id}")
            normalized["atlas"] = atlas_id
            sprites.append(normalized)

    validate_sprite_assets(sprites)
    return {"schema_version": "1.0", "atlases": atlases, "sprites": sprites}


def validate_sprite_assets(sprites):
    seen_ids = set()
    seen_files = set()
    for sprite in sprites:
        sprite_id = sprite.get("id")
        filename = sprite.get("filename")
        if not sprite_id or not filename:
            raise AtlasMapError("atlas map sprites require id and filename")
        if sprite_id in seen_ids:
            raise AtlasMapError(f"duplicate sprite id: {sprite_id}")
        if filename in seen_files:
            raise AtlasMapError(f"duplicate output filename: {filename}")
        seen_ids.add(sprite_id)
        seen_files.add(filename)


def assets_by_id(sprites):
    validate_sprite_assets(sprites)
    return {sprite["id"]: sprite for sprite in sprites}
