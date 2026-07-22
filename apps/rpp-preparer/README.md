# RPP Preparer

## Executando

```powershell
python apps\rpp-preparer\main.py "D:\Projetos AI\teste audio\a little respect.wav" --output musicas_novas
```
Ele sempre pergunta no terminal o titulo e o artista para inserir a musica nova no banco de dados

## Configuracao

Use `config.example.json` como base para criar uma configuracao local. Tambem e possivel usar a variavel:

```text
LIVERIG_IMPORTER_OUTPUT_DIR
```

## Estrutura

```text
apps/rpp-preparer/
  main.py
  importer.py
  parser.py
  catalog.py
  models.py
  songs_db.json
```
