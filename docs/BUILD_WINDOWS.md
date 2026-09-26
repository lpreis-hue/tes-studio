# Build do TeS Studio para Windows

## Pré-requisitos

- Windows 10 ou 11, 64 bits.
- Miniforge, Miniconda ou Anaconda disponível no terminal.
- Espaço livre para o ambiente científico e a pasta portátil.

O Conda é usado porque entrega `cyipopt` junto com as bibliotecas nativas do
IPOPT. Isso evita depender de uma instalação manual do solver.

## Build automatizado

Na raiz do projeto, execute:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

O script cria ou atualiza o ambiente `tes-studio`, verifica sintaxe, recursos e
integridade do núcleo numérico, e então executa o PyInstaller.

O artefato final fica em:

```text
dist/
└── TeS Studio/
    ├── TeS Studio.exe
    └── _internal/
```

Distribua toda a pasta `TeS Studio`; copiar apenas o `.exe` remove as DLLs e os
recursos dos quais ele depende.

## Verificação antes da entrega

No ambiente Conda, execute:

```powershell
python scripts/check_project.py
python scripts/smoke_test.py
```

Depois do build, abra `TeS Studio.exe`, acesse os dois módulos e carregue um
arquivo de dados conhecido. A validação científica final deve comparar os
resultados com um caso de referência aprovado pelo projeto.

## Diagnóstico rápido

- **Conda não encontrado:** reabra o terminal após instalar Miniforge/Conda.
- **DLL do IPOPT ausente:** refaça o build no ambiente criado por
  `environment.yml`; não misture Python do sistema e Conda.
- **Imagem, PDF ou planilha ausente:** execute `scripts/check_project.py` e
  confirme que o build foi iniciado na raiz do projeto.
