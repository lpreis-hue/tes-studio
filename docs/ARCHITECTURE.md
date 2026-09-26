# Arquitetura do TeS Studio

## Objetivo desta etapa

Separar a evolução da interface e do empacotamento do núcleo científico. Os
módulos numéricos continuam com as mesmas funções e equações do TeS-IPOPT.

## Camadas

1. **Shell do aplicativo** — `main.py` controla janela, navegação e estado da
   página atual.
2. **Interface** — `app/screens/` contém os fluxos Gibbs e Entropia; `app/ui/`
   concentra o tema que não deve interferir nos estilos internos das telas.
3. **Orquestração** — `app/auxiliar_func/run_gibbs.py` e `run_entropy.py`
   percorrem as condições da simulação e alimentam o solver.
4. **Núcleo científico** — `app/gibbs.py`, `app/entropy.py` e auxiliares
   termodinâmicos implementam os modelos existentes.
5. **Empacotamento** — `tes.spec`, `packaging/` e `scripts/` produzem e validam
   a distribuição portátil.

## Regra de preservação do cálculo

`scripts/check_project.py` compara cada módulo numérico com o manifesto
`numerical_core.sha256.json`. Uma mudança deliberada na matemática deve ser
revisada separadamente e só então atualizar o manifesto. Refatorações visuais
não devem alterar esses arquivos.

## Próximas evoluções seguras

- Extrair elementos duplicados de `ming.py` e `maxs.py` para componentes de UI.
- Introduzir testes com conjuntos termodinâmicos de referência e tolerâncias
  numéricas documentadas.
- Padronizar o esquema dos arquivos de entrada e fornecer um exemplo mínimo.
- Adicionar relatório de execução com versão, parâmetros e status do IPOPT.
