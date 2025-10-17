"""Compose the final VR scene assets and package them for consumption."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Tuple

from cryptography.fernet import Fernet

from vrhouse.core import SceneSpecification, VRScene


def _ensure_key_bytes(key: str | bytes) -> Tuple[str, bytes]:
    if isinstance(key, bytes):
        return key.decode("utf-8"), key
    return key, key.encode("utf-8")


class VRSceneBuilder:
    """Assemble a VR-ready scene from processed data and physics metadata."""

    def __init__(self, key_factory: Callable[[], bytes] | None = None) -> None:
        self._key_factory = key_factory or Fernet.generate_key

    def build(
        self,
        specification: SceneSpecification,
        scene_graph: Dict[str, Dict[str, str]],
        physics_profile: Dict[str, float],
    ) -> VRScene:
        """Create a ``VRScene`` object ready to be exported to engines such as Unity or Unreal."""
        output = {
            "scene_graph": scene_graph,
            "physics_profile": physics_profile,
            "metadata": {
                "exporter": "vr-scene-builder",
                "project": specification.project_name,
            },
        }
        return VRScene(
            specification=specification,
            scene_graph=output["scene_graph"],
            physics_profile=output["physics_profile"],
            ai_metadata=output["metadata"],
        )

    def export_package(self, scene: VRScene, target_directory: Path) -> tuple[Path, str]:
        """Persist the VR scene metadata to disk using symmetric encryption."""

        target_directory.mkdir(parents=True, exist_ok=True)

        key = scene.specification.output_encryption_key
        if key is None:
            key = self._key_factory().decode("utf-8")

        key_as_string, key_bytes = (key, key.encode("utf-8"))
        fernet = Fernet(key_bytes)

        payload = {
            "project": scene.specification.project_name,
            "scene_graph": scene.scene_graph,
            "physics_profile": scene.physics_profile,
            "ai_metadata": scene.ai_metadata,
        }

        encrypted_payload = fernet.encrypt(json.dumps(payload, indent=2).encode("utf-8"))

        output_file = target_directory / f"{scene.specification.project_name}.vrpkg"
        output_file.write_bytes(encrypted_payload)

        key_file = target_directory / f"{scene.specification.project_name}.key"
        if scene.specification.output_encryption_key is None:
            key_file.write_text(key_as_string, encoding="utf-8")

        return output_file, key_as_string
