# LiveRig Teleprompt

Tela web para o vocalista acompanhar a letra sincronizada com o REAPER.

## Como testar

1. Inicie o LiveRig:

```powershell
python apps\liverig\main.py
```

2. Selecione a pasta de musicas do repertorio.
3. Abra no navegador do proprio computador:

```text
http://127.0.0.1:8080/
```

Tambem existe a rota explicita:

```text
http://127.0.0.1:8080/teleprompt
```

Para acessar de outro computador ou celular na mesma rede Wi-Fi, use o IP local
do computador que esta rodando o LiveRig:

```text
http://SEU_IP_LOCAL:8080/
http://SEU_IP_LOCAL:8080/teleprompt
```

Exemplo:

```text
http://192.168.0.25:8080/teleprompt
```

4. Toque uma musica no LiveRig. A tela deve mostrar a letra atual, a proxima linha e o progresso.

## Dados

As letras sao lidas da track `Lyrics` dentro do `project.rpp` de cada musica.
