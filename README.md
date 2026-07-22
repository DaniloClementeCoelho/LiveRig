# LiveRig

Ecossistema para preparar projetos do REAPER, tocar shows ao vivo com sincronismo e criar/operar recursos visuais.
para Executar no terminal :  python ".\apps\liverig\main.py" 

## Componentes

- `apps/liverig`: programa principal usado na performance.


- `apps/rpp-preparer`: preparador/importador de projetos de audio para o formato do LiveRig.


- `apps/visual-studio`: superficies web de teleprompt e video, studio visual e scripts de geracao. consultar 
        D:\Projetos AI\LiveRig\apps\visual-studio\teleprompt e 
        D:\Projetos AI\LiveRig\apps\visual-studio\video

- `packaging`: build, PyInstaller, instalador Windows e controle de versao de release.

- `docs`: documentacao geral do projeto.

- `tests`: testes automatizados compartilhados.

## Desenvolvimento

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python apps\liverig\main.py
```

## Testes

```powershell
python -m unittest discover -s tests
```

## Release

```powershell
python packaging\build.py
```

O build gera os artefatos em `release/`. Os executaveis finais devem ser publicados no GitHub Releases, enquanto o repositorio guarda o codigo-fonte e os scripts para recriar a release.

## Git

Use `main` como linha estavel. Para mudancas de funcionalidade ou organizacao, crie branches como `feature/...`, `fix/...` ou `refactor/...`. Versoes publicadas devem receber tags como `v1.2.0`.
