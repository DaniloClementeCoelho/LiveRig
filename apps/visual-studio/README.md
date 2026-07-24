# LiveRig Visual Studio

pasta importantes de sub projetos
/teleprompt : funcionalidade de mostrar a letra
/video:  projetar videoclipes sincronizados





Modulo de criacao visual para o LiveRig.

O objetivo do projeto e preparar conteudo visual por musica: manifestos de cenas, assets gerados/importados, workflows de IA e pacotes futuros para reproducao no palco.

## Estado atual

O MVP inicial ja possui:

- player web local em `player/`;
- teleprompt web em `teleprompt/`;
- tela de video/telao em `video/`;
- renderizacao de cenas do tipo `color`, `image` e `video`;
- manifesto piloto em `projects/a-little-respect/orquestrador.json`;
- sincronizacao opcional com o LiveRig via `ws://127.0.0.1:8090/ws`;
- API FastAPI local em `api/main.py`;
- integracao inicial com ComfyUI em `http://192.168.15.9:8188`;
- workflow SDXL Turbo API em `workflows/sdxlturbo_api.json`;
- geracao de imagem via ComfyUI;
- consulta de historico e proxy de imagem gerada;
- registro de imagem remota gerada no HomeLab sem download automatico;
- registro de imagem gerada como asset em `projects/{project_id}/assets.json`;
- interface grafica simples em `studio/` para gerar imagens no HomeLab por musica.

## Executando a API

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Suba a API:

```powershell
uvicorn api.main:app --reload
```

Endpoints principais:

```text
GET  /health
GET  /comfyui/status
POST /comfyui/generate-image
POST /comfyui/generate-image-and-wait
GET  /comfyui/history/{prompt_id}
GET  /comfyui/image
POST /api/studio/generate-image
POST /projects/{project_id}/generate-remote-image-asset
POST /projects/{project_id}/generate-image-asset
```

## Executando a interface de criacao

Com a API rodando, suba tambem o servidor web local:

```powershell
uvicorn api.main:app --reload
```

Abra:

```text
http://127.0.0.1:8000/studio/index.html
```

Tambem e possivel iniciar a interface pelo arquivo:

```text
LiveRIg_gerador-de-imagens.bat
```

A interface envia nome da musica, prompt positivo e prompt negativo para o ComfyUI.
O arquivo gerado fica no servidor em:

```text
~/homelab/compose/comfyui/output/[nome-da-musica]
```

O fluxo recomendado e gerar e manter rascunhos no HomeLab:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/projects/a-little-respect/generate-remote-image-asset" `
  -ContentType "application/json" `
  -Body '{
    "prompt": "neon retro synthpop stage visuals, glowing geometric city, magenta and cyan lights, cinematic, high detail",
    "negative_prompt": "blurry, low quality, text, watermark",
    "seed": 789
  }'
```

Esse endpoint registra a imagem em `assets.json`, mas nao baixa o arquivo para o Windows.

## Executando o player

Em outro terminal:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Abra:

```text
http://127.0.0.1:8000/player/index.html
```

Sem o LiveRig aberto, o player funciona em modo local. Com o LiveRig aberto, ele tenta sincronizar pelo WebSocket local do LiveRig.

## Executando teleprompt e telao

Com o LiveRig aberto, acesse:

```text
http://127.0.0.1:8090/
http://127.0.0.1:8090/teleprompt
http://127.0.0.1:8090/video
```

Em outro computador, celular ou projetor na mesma rede Wi-Fi, troque
`127.0.0.1` pelo IP local do computador que roda o LiveRig:

```text
http://SEU_IP_LOCAL:8090/
http://SEU_IP_LOCAL:8090/teleprompt
http://SEU_IP_LOCAL:8090/video
```

O teleprompt mostra letra atual, proxima linha e progresso. A tela de video mostra midias e cues visuais para o telao.

## Projeto piloto

Projeto atual:

```text
projects/a-little-respect/
```

Arquivos principais:

```text
orquestrador.json
assets.json
assets/images/
```

## Gerando video aleatorio no HomeLab

No servidor, copie ou use o script:

```text
scripts/gerar_video_aleatorio.py
```

Ele le PNGs e MP4s de:

```text
~/homelab/compose/comfyui/output/a-lot-of-respect
```

E grava o video final em:

```text
~/homelab/compose/comfyui/output/a-lot-of-respect/videos
```

Comando:

```bash
python3 scripts/gerar_video_aleatorio.py
```

No Windows, para executar o processamento no HomeLab via SSH:

```powershell
python scripts\gerar_video_aleatorio_remoto.py
```

## Gerando video completo a partir de audio

Para gerar 15 imagens no ComfyUI e montar um video no HomeLab com a mesma duracao do WAV:

```powershell
python scripts\gerar_video_para_audio_remoto.py
```

Por padrao, esse fluxo usa:

```text
workflow: lowvram-ksampler
checkpoint: v1-5-pruned-emaonly.safetensors
resolucao: 512x512
```

O checkpoint precisa existir no ComfyUI. Para usar outro modelo instalado:

```powershell
python scripts\gerar_video_para_audio_remoto.py --checkpoint nome_do_modelo.safetensors
```

Para voltar ao workflow SDXL Turbo:

```powershell
python scripts\gerar_video_para_audio_remoto.py --workflow sdxlturbo --checkpoint sd_xl_turbo_1.0_fp16.safetensors
```

Com plano opcional de sincronizacao:

```powershell
python scripts\gerar_video_para_audio_remoto.py --sync-plan scripts\sync_plan_exemplo_comfortably_numb.json
```
