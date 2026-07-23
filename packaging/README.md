# Packaging

Scripts de build e instalacao do LiveRig para Windows.

## Gerar release

    antes de rodar, altere a versão: apps/liverig/version.py
```powershell
python packaging\build.py
```

O processo remove `build/`, `dist/` e `release/`, executa o PyInstaller e gera o instalador com Inno Setup.

## Versao

A versao do aplicativo fica em:

```text
apps/liverig/version.py
```

## Arquivos

- `build.py`: orquestra o build completo.
- `LiveRig.spec`: configuracao do PyInstaller.
- `installer.iss`: configuracao do Inno Setup.
