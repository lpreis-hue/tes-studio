# Repositório privado e build na nuvem

O projeto está pronto para um repositório privado no GitHub. O workflow
`.github/workflows/build-windows.yml` executa em uma máquina Windows x64 do
GitHub, instala IPOPT/cyipopt via Miniforge, valida a aplicação, gera o pacote
portátil e publica `TeS-Studio-Windows-x64.zip` como artefato privado.

## 1. Criar o repositório

No GitHub, selecione **New repository**, escolha um nome como `tes-studio` e
marque **Private**. Crie o repositório vazio, sem adicionar README, `.gitignore`
ou licença, pois esses arquivos já fazem parte do projeto.

## 2. Enviar os arquivos

Envie o conteúdo da pasta `TeS-Studio` para a raiz do novo repositório. A raiz
deve conter `main.py`, `environment.yml`, `tes.spec`, `app/` e `.github/`.

Se preferir usar Git no terminal:

```powershell
git init
git add .
git commit -m "Prepare TeS Studio cloud build"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/tes-studio.git
git push -u origin main
```

Substitua `SEU-USUARIO` pelo proprietário real do repositório.

## 3. Gerar o executável

1. Abra a aba **Actions** do repositório privado.
2. Selecione **Build Windows portable**.
3. Clique em **Run workflow** e confirme.
4. Aguarde o job **TeS Studio Windows x64** terminar.
5. Na página da execução, baixe o artefato **TeS-Studio-Windows-x64**.

O artefato contém o ZIP da pasta portátil. Extraia-o e abra
`TeS Studio/TeS Studio.exe`.

O workflow também roda quando uma tag começando com `v` é enviada, por exemplo:

```powershell
git tag v2.0.0-alpha.1
git push origin v2.0.0-alpha.1
```

## Privacidade e permissões

O workflow declara apenas permissão de leitura do conteúdo. O artefato fica na
execução do repositório privado e só pode ser baixado por pessoas com acesso ao
repositório. Nenhuma chave ou segredo adicional é necessário para este build.
