# LiveRig

Aplicativo principal para conducao de shows ao vivo com REAPER.

## Executando

```powershell
python apps\liverig\main.py
```

Na primeira execucao, selecione a pasta `shows` contendo as musicas do repertorio.

## Recursos principais

- Biblioteca de musicas e playlists.
- Controle de reproducao integrado ao REAPER.
- Letras sincronizadas no desktop e no teleprompt web em `/` ou `/teleprompt`.
- Projecao web em `/video` com imagens, videos e cues visuais.
- Servidor HTTP local e WebSocket para sincronizacao em tempo real.

As telas web ficam em `apps/visual-studio/teleprompt/` e `apps/visual-studio/video/`.

## Estrutura

```text
apps/liverig/
  assets/
  controllers/
  network/
  playback/
  views/
  visual_sync/
  widgets/
  main.py
  reaper_controller.py
  song_manager.py
  version.py
```

## Dados do usuario

No Windows, os dados ficam em `%APPDATA%\LiveRig`, incluindo configuracoes, logs, runtime e biblioteca de shows.
