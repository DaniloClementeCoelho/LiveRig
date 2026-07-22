# LiveRig Video

Tela web para projetar videos, imagens e cues visuais no telao da casa.

## Como testar

1. Inicie o LiveRig:

```powershell
python apps\liverig\main.py
```

2. Selecione a pasta de musicas do repertorio.
3. Abra no navegador ou no computador ligado ao telao:

```text
http://127.0.0.1:8080/video
```

4. Toque uma musica no LiveRig. A tela deve acompanhar a posicao do REAPER e exibir midias configuradas.

## Dados

A tela consome o payload de sincronizacao exposto pelo LiveRig em:

```text
/api/songs/{song_id}/sync
```

As midias sao servidas por:

```text
/api/songs/{song_id}/media/{arquivo}
```
