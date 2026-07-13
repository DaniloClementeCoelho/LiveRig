# LiveRig

Aplicativo desktop para condução de shows ao vivo utilizando o **REAPER**.

O LiveRig organiza bibliotecas de músicas, monta playlists, controla a reprodução do REAPER, exibe letras sincronizadas e centraliza todas as informações necessárias durante uma apresentação.

---

# Funcionalidades

- Biblioteca de músicas
- Busca instantânea
- Playlists
- Reprodução integrada ao REAPER
- Letras sincronizadas
- Notas da música
- Exibição de capa
- Comunicação com o REAPER
- Integração OSC (macOS)
- Importador automático de projetos `.RPP`

---

# Requisitos para desenvolvimento

- Python 3.12+
- REAPER instalado
- Git

As dependências Python encontram-se em:

```text
requirements.txt
```

---

# Configuração do ambiente

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

Na primeira execução selecione a pasta **shows** contendo as músicas do repertório.

---

# Dados do usuário

O LiveRig nunca grava arquivos dentro da pasta do programa.

No Windows todos os dados ficam em:

```text
%APPDATA%\LiveRig
```

Estrutura:

```text
LiveRig
├── settings.json
├── logs
├── runtime
└── shows
```

Isso permite atualizar o programa sem perder:

- configurações
- playlists
- logs
- biblioteca

---

# Processo de Release

Todo o processo de geração de versões foi automatizado.

## Alterando a versão

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

## Gerando uma nova versão

Com o ambiente virtual ativo execute:

```powershell
python build.py
```

O processo realiza automaticamente:

- remove `build`
- remove `dist`
- remove `release`
- executa o PyInstaller
- copia o executável para `release`
- gera o instalador Windows com o Inno Setup

Ao final serão gerados:

```text
release/
│
├── LiveRig/
│   ├── LiveRig.exe
│   └── _internal/
│
└── LiveRigSetup-x.y.z.exe
```

Esse passa a ser o procedimento oficial para publicação de novas versões.

---

# Distribuição

O arquivo a ser distribuído é:

```text
release/
    LiveRigSetup-x.y.z.exe
```

O usuário não precisa instalar:

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
- Atalho na Área de Trabalho (opcional)

---

# Recursos da aplicação

Arquivos distribuídos juntamente com o executável são localizados através do utilitário:

```text
resource_path.py
```

Isso garante compatibilidade entre:

- desenvolvimento
- executável PyInstaller

Atualmente o principal recurso distribuído é:

```text
assets/
    LiveRigPosition.lua
```

---

# Importador de projetos

O módulo `LiveRigImporter` converte projetos do REAPER para o formato utilizado pelo LiveRig.

Exemplo:

```powershell
python -m LiveRigImporter.main musica.rpp --output shows
```

Também é possível configurar:

```text
LiveRigImporter/config.local.json
```

ou utilizar a variável de ambiente:

```text
LIVERIG_IMPORTER_OUTPUT_DIR
```

---

# Estrutura do projeto

```text
LiveRig/

├── assets/
├── controllers/
├── views/
├── widgets/
├── LiveRigImporter/

├── build.py
├── LiveRig.spec
├── config.py
├── main.py
├── playback_clock.py
├── reaper_controller.py
├── resource_path.py
├── song_manager.py
├── version.py
└── installer.iss
```

---

# Dependências

| Biblioteca | Finalidade |
|------------|------------|
| customtkinter | Interface gráfica |
| python-osc | Comunicação OSC |

---

# Roadmap

## Concluído

- Interface principal
- Biblioteca de músicas
- Playlists
- Integração com REAPER
- Importador de projetos
- Build automatizado
- Executável Windows
- Instalador Windows
- Versionamento centralizado

## Próximas funcionalidades

- Informações de versão nas propriedades do executável
- Atualizador automático
- GitHub Releases
- Assinatura digital do instalador
- Pipeline CI/CD

---

# Desenvolvimento

O fluxo recomendado é:

```text
Criar feature

↓

Testar

↓

Commit

↓

Atualizar APP_VERSION

↓

python build.py

↓

Distribuir LiveRigSetup-x.y.z.exe
```

---

# Licença

Projeto de uso privado.

Todos os direitos reservados.