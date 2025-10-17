# Exemplo de execução

```bash
python -m vrhouse.cli ./modelos/casa.ifc "Casa Demo" ./build
```

Resultado esperado:
- Pacote criptografado `build/Casa Demo.vrpkg` pronto para ser consumido pelos players oficiais.
- Arquivo `build/Casa Demo.key` contendo a chave gerada (quando nenhuma é informada).
- Logs informando cada etapa do pipeline (importação, otimização, IA, exportação).

Para um fluxo assistido, execute:

```bash
python -m vrhouse.ui.app
```

Use a interface para acompanhar o progresso em tempo real e abrir um preview textual dos dados protegidos.
