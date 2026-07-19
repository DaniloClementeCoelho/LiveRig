# LiveRig

Aplicativo desktop para conducao de shows ao vivo utilizando o **REAPER**.

O LiveRig organiza bibliotecas de musicas, monta playlists, controla a reproducao do REAPER, exibe letras sincronizadas, publica estado em tempo real para o navegador e centraliza informacoes uteis durante uma apresentacao.

---

# Funcionalidades

- Biblioteca de musicas
- Busca instantanea
- Playlists
- Reproducao integrada ao REAPER
- Letras sincronizadas no app desktop
- Teleprompt web de letras sincronizadas
- Projecao web de imagens e videos sincronizados
- Midias automaticas por pasta `Media`
- Cues visuais por trecho da musica
- Notas da musica
- Exibicao de capa
- Comunicacao com o REAPER
- Servidor HTTP local
- WebSocket para sincronizacao em tempo real
- Integracao OSC (macOS)
- Importador automatico de projetos `.RPP`

---

# Requisitos para desenvolvimento

- Python 3.12+
- REAPER instalado
- Git

As dependencias Python encontram-se em:

```text
requirements.txt
```

---

# Configuracao do ambiente

## Windows

```powershell
git clone <repositorio>

cd LiveRig

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## macOS / Linux

```bash
git clone <repositorio>

cd LiveRig

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

---

# Executando

Com o ambiente virtual ativo:

```bash
python main.py
```

Na primeira execucao selecione a pasta **shows** contendo as musicas do repertorio.

---

# Visual Sync

Ao iniciar o LiveRig, tambem e iniciado um servidor HTTP local em:

```text
http://127.0.0.1:8080
```

## Teleprompt

O endereco principal exibe o teleprompt de letras sincronizadas:

```text
http://127.0.0.1:8080/
```

O teleprompt usa o estado de playback do REAPER, preserva quebras de linha vindas da track `Lyrics` e mostra:

- letra atual
- proxima letra
- titulo e artista
- barra de progresso

## Projecao de video

A tela de projecao visual fica em:

```text
http://127.0.0.1:8080/video
```

Ela suporta:

- tela cheia pelo botao `FS`
- fallback com `pano_de_fundo.jpg`
- imagens e videos aleatorios da pasta `Media`
- videos fixos por trecho usando `videos`
- cues visuais por trecho usando `visual_cues`

Quando nao ha video ativo, a tela mostra:

```text
pano_de_fundo.jpg
```

## Midia automatica

Para ativar midia automatica em uma musica, coloque arquivos dentro da pasta `Media` do pacote:

```text
Minha Musica/
+-- config.json
+-- project.rpp
`-- Media/
    +-- foto1.jpg
    +-- foto2.png
    +-- loop1.mp4
    `-- loop2.mp4
```

Formatos reconhecidos:

- Imagens: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
- Videos: `.mp4`, `.webm`, `.mov`, `.m4v`

O intervalo padrao de troca e de 12 segundos. Ele pode ser ajustado no `config.json`:

```json
{
    "visual": {
        "shuffle_interval": 12
    }
}
```

## Videos fixos por trecho

Para forcar um video em um trecho especifico:

```json
{
    "videos": [
        {
            "start": 0,
            "end": 30,
            "file": "Media/intro.mp4"
        }
    ]
}
```

Enquanto um item de `videos` estiver ativo, ele tem prioridade sobre a midia automatica.

## Cues visuais

Os cues visuais permitem forcar mensagens, letras ou midias em trechos especificos:

```json
{
    "visual_cues": [
        {
            "start": 58.5,
            "end": 74.0,
            "type": "message",
            "text": "CANTA COM A GENTE"
        },
        {
            "start": 74.0,
            "end": 90.0,
            "type": "lyrics"
        },
        {
            "start": 120.0,
            "end": 128.0,
            "type": "media",
            "file": "Media/ponte.mp4"
        }
    ]
}
```

Tambem e possivel usar uma imagem ou video como fundo de uma mensagem ou letra:

```json
{
    "visual_cues": [
        {
            "start": 58.5,
            "end": 74.0,
            "type": "message",
            "text": "CANTA COM A GENTE",
            "background": "Media/refrao.mp4"
        }
    ]
}
```

Tipos disponiveis:

- `message`: exibe texto grande na tela
- `lyrics`: exibe a letra atual em tamanho grande
- `media`: exibe uma imagem ou video especifico

Prioridade da tela `/video`:

1. `visual_cues`
2. `videos`
3. midia automatica da pasta `Media`
4. `pano_de_fundo.jpg`

## API local

Endpoints principais:

```text
GET /api/playback
GET /api/songs/{song_id}/sync
GET /api/songs/{song_id}/media/{media_path}
GET /pano_de_fundo.jpg
```

O WebSocket de tempo real fica em:

```text
ws://127.0.0.1:8080/ws
```

---

# Dados do usuario

O LiveRig nunca grava arquivos dentro da pasta do programa.

No Windows todos os dados ficam em:

```text
%APPDATA%\LiveRig
```

Estrutura:

```text
LiveRig
+-- settings.json
+-- logs
+-- runtime
`-- shows
```

Isso permite atualizar o programa sem perder:

- configuracoes
- playlists
- logs
- biblioteca

---

# Processo de Release

Todo o processo de geracao de versoes foi automatizado.

## Alterando a versao

Edite apenas:

```python
version.py
```

Exemplo:

```python
APP_VERSION = "1.2.0"
```

Nenhum outro arquivo precisa ser alterado.

---

## Gerando uma nova versao

Com o ambiente virtual ativo execute:

```powershell
python build.py
```

O processo realiza automaticamente:

- remove `build`
- remove `dist`
- remove `release`
- executa o PyInstaller
- copia o executavel para `release`
- gera o instalador Windows com o Inno Setup

Ao final serao gerados:

```text
release/
|
+-- LiveRig/
|   +-- LiveRig.exe
|   `-- _internal/
|
`-- LiveRigSetup-x.y.z.exe
```

Esse passa a ser o procedimento oficial para publicacao de novas versoes.

---

# Distribuicao

O arquivo a ser distribuido e:

```text
release/
    LiveRigSetup-x.y.z.exe
```

O usuario nao precisa instalar:

- Python
- bibliotecas Python
- PyInstaller

O instalador instala automaticamente o LiveRig em:

```text
C:\Program Files\LiveRig
```

Criando:

- Menu Iniciar
- Desinstalador
- Atalho na Area de Trabalho (opcional)

---

# Recursos da aplicacao

Arquivos distribuidos juntamente com o executavel sao localizados atraves do utilitario:

```text
resource_path.py
```

Isso garante compatibilidade entre:

- desenvolvimento
- executavel PyInstaller

Recursos atuais:

```text
assets/
    LiveRigPosition.lua
web/
    index.html
    video.html
pano_de_fundo.jpg
```

---

# Importador de projetos

O modulo `LiveRigImporter` converte projetos do REAPER para o formato utilizado pelo LiveRig.

Exemplo:

```powershell
python -m LiveRigImporter.main musica.rpp --output shows
```

Tambem e possivel configurar:

```text
LiveRigImporter/config.local.json
```

ou utilizar a variavel de ambiente:

```text
LIVERIG_IMPORTER_OUTPUT_DIR
```

---

# Estrutura do projeto

```text
LiveRig/

+-- assets/
+-- controllers/
+-- network/
+-- playback/
+-- views/
+-- visual_sync/
+-- web/
+-- widgets/
+-- LiveRigImporter/
+-- tests/

+-- build.py
+-- LiveRig.spec
+-- config.py
+-- main.py
+-- playback_clock.py
+-- reaper_controller.py
+-- resource_path.py
+-- song_manager.py
+-- version.py
`-- installer.iss
```

---

# Dependencias

| Biblioteca | Finalidade |
|------------|------------|
| customtkinter | Interface grafica |
| python-osc | Comunicacao OSC |
| fastapi | Servidor HTTP e WebSocket local |
| uvicorn | Execucao do servidor HTTP |
| Pillow | Manipulacao/exibicao de imagens |

---

# Testes

Os testes automatizados usam `unittest`:

```powershell
python -m unittest discover -s tests
```

---

# Roadmap

## Concluido

- Interface principal
- Biblioteca de musicas
- Playlists
- Integracao com REAPER
- Letras sincronizadas no app desktop
- Teleprompt web sincronizado
- Projecao web de videos e imagens
- Midia automatica por pasta `Media`
- Cues visuais por trecho
- Fallback visual com `pano_de_fundo.jpg`
- API local de sync
- WebSocket em tempo real
- Importador de projetos
- Build automatizado
- Executavel Windows
- Instalador Windows
- Versionamento centralizado

## Proximas funcionalidades

- Interface grafica para editar `visual_cues`
- Garantir inclusao de `web/` e `pano_de_fundo.jpg` no build final
- Informacoes de versao nas propriedades do executavel
- Atualizador automatico
- GitHub Releases
- Assinatura digital do instalador
- Pipeline CI/CD

---

# Desenvolvimento

O fluxo recomendado e:

```text
Criar feature

v

Testar

v

Commit

v

Atualizar APP_VERSION

v

python build.py

v

Distribuir LiveRigSetup-x.y.z.exe
```

---

# Licenca

Projeto de uso privado.

Todos os direitos reservados.
