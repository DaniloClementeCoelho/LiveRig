# LiveRig

Aplicativo desktop para conduzir shows ao vivo com o REAPER. Organiza uma biblioteca de músicas, monta playlists, controla reprodução, exibe letras sincronizadas e abre projetos `.RPP` a partir de uma interface gráfica.

---

# Requisitos para desenvolvimento

- Python 3.10 ou superior
- REAPER instalado
- Dependências listadas em `requirements.txt`

---

# Instalação

## Windows

```powershell
cd LiveRig
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## macOS / Linux

```bash
cd LiveRig
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

# Executar

Com o ambiente virtual ativo:

```bash
python main.py
```

Na primeira execução, escolha a pasta **shows** que contém as músicas do seu set.

As preferências do usuário são armazenadas automaticamente na área de dados do sistema operacional.

No Windows:

```text
%APPDATA%\LiveRig\
```

Estrutura criada automaticamente:

```text
LiveRig
├── settings.json
├── logs/
├── runtime/
└── shows/
```

Essa separação permite atualizar o programa sem perder configurações, playlists ou dados do usuário.

---

# Distribuição para Windows

O projeto está preparado para ser empacotado utilizando o PyInstaller.

## Gerar o executável

```powershell
pyinstaller LiveRig.spec
```

Será criada a estrutura:

```text
dist/
└── LiveRig/
    ├── LiveRig.exe
    └── _internal/
```

O executável já contém:

- Interpretador Python
- Dependências Python
- Bibliotecas necessárias
- Script `LiveRigPosition.lua`

Não é necessário instalar Python na máquina onde o LiveRig será executado.

---

# Recursos da aplicação

Arquivos distribuídos juntamente com o executável (como o script Lua utilizado pelo REAPER) são acessados através do utilitário `resource_path.py`.

Isso garante compatibilidade entre:

- execução durante o desenvolvimento;
- executável gerado pelo PyInstaller.

---

# Importar projetos do REAPER

O `LiveRigImporter` prepara arquivos `.rpp` para o formato utilizado pelo LiveRig.

A pasta de saída pode ser definida por:

- argumento de linha de comando;
- variável de ambiente;
- arquivo de configuração local.

Exemplo:

```powershell
python -m LiveRigImporter.main caminho\musica.rpp --output caminho\da\saida
```

Ou utilizando `LiveRigImporter/config.local.json`:

```json
{
    "output_dir": "D:/Projetos AI/LiveRig/shows"
}
```

Também é possível utilizar a variável:

```text
LIVERIG_IMPORTER_OUTPUT_DIR
```

---

# Cursor / VS Code

O projeto inclui configurações para utilizar automaticamente o ambiente virtual.

Caso necessário, configure o interpretador:

Windows

```text
.venv/Scripts/python.exe
```

macOS / Linux

```text
.venv/bin/python
```

---

# Estrutura de uma música

Cada música fica em uma subpasta dentro de `shows`.

Exemplo:

```text
shows/
└── Minha Música/
    ├── config.json
    ├── projeto.RPP
    ├── letra.lrc
    ├── notas.txt
    └── capa.jpg
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

O campo `project` é obrigatório.

Todos os demais são opcionais.

---

# Funcionalidades

- Biblioteca de músicas
- Busca instantânea
- Playlist com drag-and-drop
- Reprodução integrada ao REAPER
- Letras sincronizadas
- Notas da música
- Exibição de capa
- Comunicação com REAPER
- Integração OSC (macOS)

---

# Arquitetura

```text
LiveRig/
├── main.py
├── config.py
├── resource_path.py
├── LiveRig.spec
├── reaper_controller.py
├── song_manager.py
├── playback_clock.py
├── controllers/
├── views/
├── widgets/
├── assets/
│   └── LiveRigPosition.lua
└── LiveRigImporter/
```

---

# Dependências

| Pacote | Finalidade |
|---------|------------|
| customtkinter | Interface gráfica |
| python-osc | Comunicação OSC |

---

# Roadmap

## Em andamento

- Empacotamento com PyInstaller
- Instalador Windows
- Automatização do processo de build

## Próximos passos

- `build.py` para geração automática
- Instalador Inno Setup
- Versionamento automático
- Atualizador automático
- GitHub Releases

---

# Licença

Uso interno / projeto pessoal.

Consulte o autor antes de redistribuir.