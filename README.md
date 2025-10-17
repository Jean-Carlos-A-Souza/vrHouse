# vrHouse
<<<<<<< HEAD

Plataforma para converter projetos residenciais 3D em experiências de realidade virtual com física e realismo gerados por IA.

## Visão geral

A estrutura proposta organiza o projeto em estágios claros de ingestão, processamento, inferência e exportação. Ela facilita a criação de pipelines automatizados que:

1. Importam plantas/modelos (IFC, FBX, OBJ, GLTF/GLB e Revit RVT).
2. Otimizam a geometria e refinam materiais para VR.
3. Aplicam modelos de IA para simular física e realismo.
4. Empacotam os dados em experiências VR prontas para engines como Unity, Unreal ou WebXR.

## Estrutura de diretórios

```
vrHouse/
├── assets/                # Texturas, HDRIs e outros recursos compartilhados
├── config/                # Arquivos de configuração (YAML, JSON)
├── docs/                  # Documentação técnica e guias
├── examples/              # Exemplos de uso e cenas de demonstração
├── src/                   # Código-fonte principal da aplicação
│   └── vrhouse/
│       ├── core.py        # Modelos de dados e exceções base
│       ├── cli.py         # Interface de linha de comando
│       └── pipeline/
│           ├── ai/        # Modelos e serviços de IA
│           ├── exporters/ # Empacotamento e exportação para VR
│           ├── importers/ # Conversores de formatos de entrada (IFC, OBJ, etc.)
│           └── processors/# Otimizações geométricas, materiais, iluminação
├── tests/                 # Futuras suítes automatizadas
└── README.md
```

## Interface gráfica inicial

Usuários não técnicos podem executar o aplicativo desktop (Tkinter) com:

```bash
python -m vrhouse.ui.app
```

Na tela inicial é possível:

- Selecionar o arquivo da planta em um dos formatos suportados.
- Escolher a pasta de saída e o nome do projeto.
- Ativar ou desativar física e realismo por IA.
- Gerar ou informar uma chave própria para criptografia.
- Acompanhar o progresso da conversão em tempo real.
- Visualizar um preview descriptivo do pacote gerado (após informar a chave correta).

## Conversão via linha de comando

```bash
python -m vrhouse.cli ./modelos/casa.ifc "Casa dos Santos" ./build
```

Ao final da execução, o sistema gera um pacote criptografado (`.vrpkg`) e informa a chave utilizada. Guarde essa chave com segurança: apenas os aplicativos oficiais de desktop ou VR conseguem abrir o conteúdo.

## Próximos passos sugeridos

- Integrar bibliotecas de parsing (ex.: IfcOpenShell, trimesh) nas classes de importação.
- Implementar otimização real de malhas e UVs (ex.: Blender Python API, assimp).
- Conectar modelos de IA para textura procedimental e simulação física.
- Desenvolver exportação direta para motores VR e WebXR.
- Adicionar testes automatizados e pipelines CI/CD.
=======
App de conversão de projetos 3D para o VR
>>>>>>> f80fce9f40bb59927adf5c58fd3ac0fcd8542a66
