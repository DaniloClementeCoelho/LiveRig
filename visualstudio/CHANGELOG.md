# Changelog

## 2026-07-19

- Adicionado suporte a cenas de imagem no player web.
- Adicionado suporte inicial a cenas de video no player web.
- Adicionado endpoint para registrar imagem remota gerada no HomeLab sem download automatico.
- Adicionada interface grafica simples para gerar imagens no HomeLab por nome da musica e prompts.
- Adicionado endpoint `/api/studio/generate-image` salvando no output do ComfyUI por subpasta da musica.
- Adicionado atalho `LiveRIg_gerador-de-imagens.bat` para abrir a interface e iniciar a API.
- Adicionado script Python para gerar video aleatorio de 1 minuto com PNGs/MP4s no HomeLab.
- Adicionado wrapper Windows para executar a geracao de video no HomeLab via SSH.
- Adicionado orquestrador para gerar imagens pelo ComfyUI e montar video com a duracao de um WAV.
- Adicionado plano JSON opcional para trechos sincronizados com texto/arquivo especifico.
- Atualizado manifesto piloto para usar a primeira imagem gerada pelo ComfyUI.
- Criado player web minimo com troca de cenas por tempo.
- Adicionado manifesto piloto para `A Little Respect`.
- Adicionada sincronizacao opcional do player com o LiveRig via WebSocket.
- Integrado contrato visual com o LiveRig por manifesto referenciado no `config.json` da musica.
- Criada API FastAPI inicial do Visual Studio.
- Adicionada integracao com ComfyUI para status, geracao, historico e visualizacao de imagem.
- Adicionado workflow SDXL Turbo em formato API.
- Adicionado endpoint para gerar imagem e registrar como asset do projeto.
