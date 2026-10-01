# Changelog

## 2.0.0-alpha.1

- Novo shell do TeS Studio com navegação lateral e estado de página ativo.
- Nova visão geral com acesso direto aos módulos Gibbs e Entropia.
- Tema do shell isolado para não sobrescrever a legibilidade das telas legadas.
- Caminhos de recursos independentes do diretório de execução.
- Build portátil de Windows com recursos e DLLs do IPOPT.
- Ambiente Conda e script automatizado de build.
- Verificações de sintaxe, recursos, interface e integridade do núcleo numérico.
- Documentação de arquitetura e build.
- Workflow privado do GitHub Actions para gerar e publicar o ZIP Windows x64.
- Dependabot mensal para manter as ações de build atualizadas.
- Correção do pacote Conda da interface para `pyqt6`, disponível no Windows.
- PyQt6 movido para wheel oficial do Python no build Windows, evitando a falha
  conhecida do script `gdk-pixbuf` no Conda.
- Runtime C++ do PyQt6 unificado após o empacotamento para evitar a colisão
  entre `MSVCP140.dll` 14.26 e 14.51 no Windows.
- Simulações em malha agora reutilizam a solução convergida do ponto vizinho
  como estimativa inicial, reduzindo as iterações do IPOPT sem alterar as
  equações, os balanços ou as tolerâncias numéricas.
- Interface redesenhada no tema técnico escuro, com parâmetros agrupados,
  cálculo prévio do total de cenários, progresso com tempo estimado e áreas
  integradas para análises e resultados.
- Gráficos Matplotlib incorporados à interface, sem janelas externas.
- Gráficos e tabela completa de resultados exibidos lado a lado na mesma guia,
  com divisão redimensionável e exportação para Excel ou CSV preservada.

