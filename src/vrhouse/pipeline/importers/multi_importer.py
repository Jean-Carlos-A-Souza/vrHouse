"""Import 3D architectural plans from the most common exchange formats."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Protocol

from vrhouse.core import SceneSpecification


class ImporterError(RuntimeError):
    """Raised when an importer cannot handle the requested format."""


class FormatImporter(Protocol):
    """Interface implemented by concrete format importers."""

    supported_suffixes: tuple[str, ...]

    def load(self, specification: SceneSpecification) -> Dict[str, Dict[str, str]]:
        ...


@dataclass
class StubImporter:
    """Utility base class shared by the placeholder importers."""

    supported_suffixes: tuple[str, ...]
    format_name: str

    def load(self, specification: SceneSpecification) -> Dict[str, Dict[str, str]]:
        if not specification.source_file.exists():
            raise FileNotFoundError(f"Source file not found: {specification.source_file}")

        return {
            "root": {
                "type": "scene",
                "origin_file": str(specification.source_file),
                "format": self.format_name,
                "required_assets": self._infer_required_assets(specification.source_file),
            }
        }

    def _infer_required_assets(self, source: Path) -> List[str]:
        """Provide a list of placeholder assets to mimic texture/geometry needs."""

        if source.suffix.lower() == ".gltf":
            return ["gltf-binary", "pbr-textures"]
        if source.suffix.lower() == ".glb":
            return ["embedded-binary", "compressed-textures"]
        if source.suffix.lower() == ".fbx":
            return ["fbx-materials", "animation-curves"]
        if source.suffix.lower() == ".obj":
            return ["mtl-materials", "uv-coordinates"]
        if source.suffix.lower() == ".ifc":
            return ["ifc-structure", "bim-properties"]
        if source.suffix.lower() == ".rvt":
            return ["revit-metadata", "autodesk-materials"]
        return ["generic-assets"]


IFCImporter = StubImporter(supported_suffixes=(".ifc",), format_name="ifc")
FBXImporter = StubImporter(supported_suffixes=(".fbx",), format_name="fbx")
OBJImporter = StubImporter(supported_suffixes=(".obj",), format_name="obj")
GLTFImporter = StubImporter(supported_suffixes=(".gltf", ".glb"), format_name="gltf")
RVTImporter = StubImporter(supported_suffixes=(".rvt",), format_name="revit")

SUPPORTED_IMPORTERS: tuple[StubImporter, ...] = (
    IFCImporter,
    FBXImporter,
    OBJImporter,
    GLTFImporter,
    RVTImporter,
)


def iter_supported_suffixes() -> Iterable[str]:
    for importer in SUPPORTED_IMPORTERS:
        yield from importer.supported_suffixes


class MultiFormatImporter:
    """Dispatcher that selects the appropriate importer for the source file."""

    def __init__(self, importers: Iterable[FormatImporter] | None = None) -> None:
        self._importers: List[FormatImporter] = list(importers) if importers else list(SUPPORTED_IMPORTERS)

    def load(self, specification: SceneSpecification) -> Dict[str, Dict[str, str]]:
        importer = self._select_importer(specification.source_file)
        return importer.load(specification)

    def validate_source_path(self, path: Path) -> None:
        self._select_importer(path)

    def _select_importer(self, path: Path) -> FormatImporter:
        suffix = path.suffix.lower()
        if not suffix:
            raise ImporterError("Source file must have an extension identifying its format")

        for importer in self._importers:
            if suffix in importer.supported_suffixes:
                return importer

        supported = ", ".join(iter_supported_suffixes())
        raise ImporterError(f"Unsupported file type: {suffix}. Supported extensions: {supported}")


def validate_source_path(path: Path) -> None:
    """Public helper mirroring the classic validation API used by the CLI."""

    MultiFormatImporter().validate_source_path(path)


__all__ = [
    "MultiFormatImporter",
    "validate_source_path",
    "iter_supported_suffixes",
]
