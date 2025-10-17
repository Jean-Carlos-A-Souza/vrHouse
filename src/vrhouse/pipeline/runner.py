"""High level helpers to execute the conversion pipeline with progress reporting."""
from __future__ import annotations

from typing import Callable, Dict, Optional

from vrhouse.core import SceneSpecification
from vrhouse.pipeline.ai.physics_model import PhysicsInferenceModel
from vrhouse.pipeline.exporters.vr_scene_builder import VRSceneBuilder
from vrhouse.pipeline.importers.multi_importer import MultiFormatImporter, validate_source_path
from vrhouse.pipeline.processors.geometry_optimizer import GeometryOptimizer
from vrhouse.pipeline.processors.material_enhancer import MaterialEnhancer

ProgressCallback = Callable[[float, str], None]


def run_conversion(
    specification: SceneSpecification,
    output_directory,
    *,
    progress_callback: Optional[ProgressCallback] = None,
) -> Dict[str, object]:
    """Execute the conversion pipeline and export the encrypted package."""
    def emit(progress: float, message: str) -> None:
        if progress_callback:
            progress_callback(progress, message)

    importer = MultiFormatImporter()
    optimizer = GeometryOptimizer()
    enhancer = MaterialEnhancer()
    physics_model = PhysicsInferenceModel()
    exporter = VRSceneBuilder()

    emit(0.05, "Validando arquivo de origem")
    validate_source_path(specification.source_file)

    emit(0.2, "Carregando geometria base")
    scene_graph = importer.load(specification)

    emit(0.35, "Otimizando geometria e malhas")
    scene_graph = optimizer.optimize(scene_graph)

    if specification.enable_ai_realism:
        emit(0.5, "Aplicando IA para realismo de materiais")
        scene_graph = enhancer.enhance(scene_graph)

    physics_profile: Dict[str, float] = {}
    if specification.enable_physics:
        emit(0.65, "Gerando perfil de física")
        physics_profile = physics_model.predict(specification)

    emit(0.8, "Compondo cena VR criptografada")
    scene = exporter.build(specification, scene_graph, physics_profile)

    emit(0.95, "Exportando pacote protegido")
    package_path, encryption_key = exporter.export_package(scene, output_directory)

    emit(1.0, "Conversão concluída")
    return {
        "scene": scene,
        "package_path": package_path,
        "encryption_key": encryption_key,
    }


__all__ = ["run_conversion", "ProgressCallback"]
