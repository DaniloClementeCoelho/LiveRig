# LiveRig

Aplicativo desktop para conduzir shows ao vivo com [REAPER](https://www.reaper.fm/). Organiza uma biblioteca de músicas, monta a playlist do set e controla reprodução, letras sincronizadas e projetos `.RPP` a partir de uma interface gráfica.

## Requisitos

- **Python** 3.10 ou superior
- **REAPER** instalado (Windows ou macOS)
- Dependências Python listadas em `requirements.txt`

## Instalação

Clone o repositório e crie o ambiente virtual na raiz do projeto:

```powershell
# Windows (PowerShell)
cd LiveRig
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# macOS / Linux
cd LiveRig
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

Com o ambiente virtual ativo:

```bash
python main.py
```

Na primeira execução, escolha a pasta **shows** que contém as músicas do set. A preferência fica salva em `settings.json`.

## Cursor / VS Code

O projeto inclui `.vscode/settings.json` para usar o interpretador do `.venv` e ativar o ambiente automaticamente em terminais novos.

No **macOS**, ajuste o caminho do interpretador se necessário:

- Windows: `.venv/Scripts/python.exe`
- macOS/Linux: `.venv/bin/python`

## Estrutura de uma música

Cada música fica em uma subpasta dentro de `shows/`, com um `config.json` apontando para os arquivos do pacote:

```
shows/
└── Minha Musica/
    ├── config.json
    ├── projeto.RPP
    ├── letra.lrc          # opcional
    ├── notas.txt          # opcional
    └── capa.jpg           # opcional
```

Exemplo de `config.json`:

```json
{
  "title": "Minha Música",
  "artist": "Artista",
  "project": "projeto.RPP",
  "lyrics": "letra.lrc",
  "notes": "notas.txt",
  "cover": "capa.jpg",
  "bpm": 120,
  "tuning": "EADGBE",
  "patch": 1
}
```

O campo `project` é obrigatório. Os demais são opcionais.

## Funcionalidades

- **Biblioteca** — lista todas as músicas da pasta shows, com busca instantânea
- **Playlist** — monte o set arrastando músicas da biblioteca; reordene com drag and drop
- **Player** — abre o projeto no REAPER, play/pause e exibe metadados, notas e letras
- **Letras sincronizadas** — acompanha a posição de reprodução via script Lua instalado no REAPER
- **Integração REAPER** — lança o REAPER, carrega projetos e envia ações (Windows nativo; macOS via OSC)

## Arquitetura

```
LiveRig/
├── main.py                 # ponto de entrada
├── reaper_controller.py    # comunicação com o REAPER
├── song_manager.py         # leitura dos pacotes de música
├── playback_clock.py       # posição de reprodução
├── views/                  # telas (biblioteca, playlist, player)
├── widgets/                # componentes reutilizáveis da UI
├── controllers/            # lógica de drag and drop
└── assets/                 # script Lua (LiveRigPosition.lua)
```

## Dependências

| Pacote        | Uso                          |
|---------------|------------------------------|
| customtkinter | interface gráfica            |
| python-osc    | comunicação OSC (macOS)      |

## Licença

Uso interno / projeto pessoal. Consulte o autor antes de redistribuir.
