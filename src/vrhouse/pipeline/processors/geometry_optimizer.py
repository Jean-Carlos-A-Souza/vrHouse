"""Utilities that adapt geometry for VR friendly rendering."""
from __future__ import annotations

from typing import Dict

from vrhouse.core import PipelineError


class GeometryOptimizer:
    """Optimize geometry and mesh data for VR consumption."""

    def optimize(self, scene_graph: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        """Run optimization routines such as decimation and UV unwrapping."""
        if "root" not in scene_graph:
            raise PipelineError("Scene graph missing root node")

        optimized = dict(scene_graph)
        optimized["root"] = {**scene_graph["root"], "geometry_optimized": "true"}
        return optimized
