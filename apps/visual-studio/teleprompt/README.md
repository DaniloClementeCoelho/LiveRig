# LiveRig Teleprompt

Tela web para o vocalista acompanhar a letra sincronizada com o REAPER.

## Como testar

1. Inicie o LiveRig:

```powershell
python apps\liverig\main.py
```

2. Selecione a pasta de musicas do repertorio.
3. Abra no navegador:

```text
http://127.0.0.1:8080/
```

Tambem existe a rota explicita:

```text
http://127.0.0.1:8080/teleprompt
```

4. Toque uma musica no LiveRig. A tela deve mostrar a letra atual, a proxima linha e o progresso.

## Dados

As letras sao lidas da track `Lyrics` dentro do `project.rpp` de cada musica.
