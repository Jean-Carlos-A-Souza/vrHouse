"""Core data models and utilities for the vrHouse pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AssetReference:
    """Metadata pointing to assets used in the VR experience."""

    name: str
    path: Path
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SceneSpecification:
    """High-level description of the target VR scene."""

    project_name: str
    source_file: Path
    assets: List[AssetReference] = field(default_factory=list)
    target_platforms: List[str] = field(default_factory=lambda: ["meta-quest", "htc-vive", "pimax"])
    enable_physics: bool = True
    enable_ai_realism: bool = True
    notes: Optional[str] = None
    output_encryption_key: Optional[str] = None


@dataclass
class VRScene:
    """Container for the fully baked VR experience."""

    specification: SceneSpecification
    scene_graph: Dict[str, Dict[str, str]]
    physics_profile: Dict[str, float]
    ai_metadata: Dict[str, str] = field(default_factory=dict)


class PipelineError(RuntimeError):
    """Raised when a pipeline stage fails."""

    pass
