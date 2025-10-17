# Arquitetura inicial do vrHouse

## Objetivo

Transformar plantas arquitetônicas (IFC, FBX, OBJ, GLTF/GLB, RVT) em experiências VR com física e realismo assistidos por IA, entregues em pacotes criptografados exclusivos.

## Pipeline de alto nível

1. **Ingestão**
   - Importadores específicos por formato.
   - Validação de arquivos e extração de metadados.
2. **Processamento**
   - Otimização de geometria (decimação, LOD, UVs).
   - Enriquecimento de materiais e iluminação.
3. **IA aplicada**
   - Modelos que inferem propriedades físicas (massa, fricção, densidade).
   - Geração procedural de texturas e materiais compatíveis com PBR.
4. **Exportação**
   - Construção de cena VR (Unity/Unreal/WebXR).
   - Empacotamento e deploy para dispositivos.

## Componentes chave

- `core.SceneSpecification`: descreve o projeto a ser convertido.
- `pipeline.importers.MultiFormatImporter`: roteia automaticamente entre os formatos IFC, FBX, OBJ, GLTF/GLB e RVT.
- `pipeline.processors.GeometryOptimizer`: otimiza malhas para VR.
- `pipeline.processors.MaterialEnhancer`: adiciona materiais realistas via IA.
- `pipeline.ai.PhysicsInferenceModel`: gera perfis físicos simulados.
- `pipeline.exporters.VRSceneBuilder`: monta o resultado final, criptografa e exporta.
- `pipeline.runner.run_conversion`: orquestra o pipeline reportando progresso.
- `ui.app.VRHouseApp`: interface desktop em Tkinter para usuários leigos acompanharem a conversão.

## Roadmap técnico

- Suporte a múltiplos formatos de importação (IFC, FBX, OBJ, GLTF, Revit) com parsing real.
- Integração com motores (Unity, Unreal) via APIs ou arquivos intermediários.
- Treinamento/uso de modelos IA para sugestões de layout, iluminação, materiais.
- Painel web para visualização de status e gerenciamento de projetos.
- Automatização CI/CD e suporte a plugins.
