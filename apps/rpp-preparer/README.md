# RPP Preparer

Ferramenta para preparar projetos `.rpp` do REAPER para uso no LiveRig.

## Executando

```powershell
python apps\rpp-preparer\main.py musica.rpp --output shows
```

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
