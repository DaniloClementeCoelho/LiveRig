# Stack Tecnológica — LiveRig Visual Studio

## Objetivo

Definir uma stack simples, local-first e compatível com o hardware atual do HomeLab.

A prioridade inicial é validar o fluxo completo com uma única música, evitando componentes distribuídos antes de existir necessidade real.

## Restrições do ambiente

O servidor principal possui:

- Intel Core i7-1165G7;
- 16 GB de RAM;
- NVIDIA GTX 1650 Max-Q com 4 GB de VRAM;
- Ubuntu Server 26.04 LTS;
- Docker com suporte à GPU NVIDIA.

Consequências práticas:

- modelos de imagem devem começar pequenos e otimizados;
- geração de vídeo por IA será experimental e em baixa resolução;
- não manter vários modelos pesados carregados simultaneamente;
- edição deve usar proxies;
- renderização final pode ocorrer em etapas;
- a reprodução no palco não dependerá de IA, Docker ou internet.

## Decisões principais

| Camada | Tecnologia inicial | Decisão |
|---|---|---|
| Linguagem principal | Python 3.12 | Adotada |
| API | FastAPI | Adotada |
| Validação de dados | Pydantic | Adotada |
| Servidor ASGI | Uvicorn | Adotada |
| Interface inicial | Aplicação web local | Adotada |
| Front-end inicial | HTML, CSS e JavaScript simples | Adotada para o MVP |
| Geração visual | ComfyUI | Candidata principal |
| Processamento de mídia | FFmpeg | Adotada |
| Imagens auxiliares | Pillow | Adotada |
| Metadados | JSON em arquivos | Adotada para o MVP |
| Persistência futura | SQLite | Adiada |
| Comunicação com Player | WebSocket | Candidata principal |
| Comunicação alternativa | OSC | Mantida como opção |
| Containers | Docker Compose | Adotada no HomeLab |
| Configuração | `.env` | Adotada |
| Testes | pytest | Adotada |
| Formatação | Ruff | Adotada |
| Tipagem | mypy | Planejada |

## 1. Python

Versão inicial recomendada:

```text
Python 3.12
```

Motivos:

- compatibilidade ampla com bibliotecas de IA e mídia;
- estabilidade superior a versões muito recentes;
- integração natural com o LiveRig atual;
- bom suporte a FastAPI, Pydantic, Pillow e ferramentas de automação.

A versão deverá ser fixada no projeto para evitar diferenças entre Windows e Ubuntu.

## 2. API e orquestração

### FastAPI

Responsabilidades:

- criar e consultar projetos visuais;
- registrar assets;
- iniciar tarefas de geração ou processamento;
- consultar o andamento das tarefas;
- aprovar ou descartar resultados;
- exportar pacotes para o palco.

### Pydantic

Será usado para validar:

- manifestos de música;
- dados dos assets;
- configurações de geração;
- respostas da API;
- variáveis de ambiente.

### Uvicorn

Servidor inicial da API.

Comando de desenvolvimento esperado:

```bash
uvicorn visualstudio.api.main:app --reload
```

O caminho definitivo será confirmado quando o primeiro módulo Python for criado.

## 3. Interface

### Escolha para o MVP

Aplicação web local com:

- HTML;
- CSS;
- JavaScript simples;
- chamadas HTTP à API;
- WebSocket apenas quando houver necessidade de progresso em tempo real.

Motivos:

- menor complexidade inicial;
- funciona no Windows e no Ubuntu;
- não exige empacotamento de uma aplicação desktop no primeiro teste;
- permite evoluir depois para React, Vue ou outro framework sem alterar a API.

### O que não será adotado inicialmente

- React;
- Electron;
- Next.js;
- aplicação desktop nativa;
- framework de estado complexo.

Essas opções só serão reconsideradas se a interface simples se tornar limitante.

## 4. Geração de imagens e vídeos

### ComfyUI

Candidato principal para geração visual porque permite:

- workflows reproduzíveis;
- integração por API;
- uso local da GPU;
- versionamento dos workflows em JSON;
- troca de modelos sem alterar a API do Visual Studio.

O ComfyUI será tratado como engine externa. A API do Visual Studio não deverá depender diretamente da estrutura interna de um workflow específico.

### Estratégia inicial para a GTX 1650 4 GB

Começar por:

- geração de imagens, não vídeos longos;
- resoluções reduzidas;
- batch de uma imagem;
- modelos compactos;
- atenção às otimizações de memória;
- descarregamento de modelos entre tarefas, quando necessário.

A geração de vídeo por IA não será requisito para o primeiro MVP.

### Alternativas

Poderão ser avaliadas futuramente:

- APIs externas de geração;
- execução em uma GPU mais forte;
- geração em nuvem sob demanda;
- animação de imagens com FFmpeg e shaders;
- modelos locais mais leves.

Serviços externos serão opcionais e nunca necessários para o palco.

## 5. Processamento de mídia

### FFmpeg

Ferramenta central para:

- converter formatos;
- redimensionar vídeos;
- alterar bitrate e taxa de quadros;
- normalizar resolução;
- gerar thumbnails;
- criar proxies;
- concatenar trechos;
- aplicar fades e transições simples;
- gerar loops;
- extrair quadros;
- preparar o arquivo final para o Player.

O FFmpeg deverá ser chamado por comandos controlados pelo Python. Os parâmetros usados deverão ser registrados para permitir reprodução do resultado.

### Pillow

Usada para tarefas simples de imagem:

- redimensionamento;
- criação de thumbnails;
- composição básica;
- aplicação de texto ou molduras;
- leitura de metadados.

Efeitos complexos não deverão ser reimplementados em Python quando o FFmpeg ou o ComfyUI resolverem melhor.

## 6. Shaders

Shaders poderão ser usados para efeitos leves e em tempo real no Player, desde que não comprometam a estabilidade do palco.

Tecnologias candidatas:

- GLSL;
- WebGL;
- shaders executados em um player web local.

No MVP, shaders serão tratados como assets opcionais. A primeira validação poderá usar apenas imagens e vídeos pré-renderizados.

## 7. Metadados e persistência

### MVP: arquivos JSON

Cada projeto de música terá um manifesto JSON.

Vantagens:

- leitura simples;
- fácil inspeção manual;
- versionamento possível;
- ausência de migrações de banco;
- menor esforço para o primeiro protótipo.

Estrutura conceitual:

```text
projects/
└── a-little-respect/
    ├── project.json
    ├── assets.json
    └── exports/
```

Os arquivos grandes não serão versionados no Git.

### Futuro: SQLite

SQLite será considerado quando existir necessidade de:

- pesquisa por muitos assets;
- filtros e tags;
- histórico de tarefas;
- controle mais robusto de estados;
- concorrência entre processos.

Não será introduzido antes desses requisitos aparecerem.

## 8. Tarefas e workers

### MVP

Execução direta por processos Python, com estado simples em memória ou JSON.

Fluxo:

```text
API recebe solicitação
  ↓
serviço executa tarefa
  ↓
resultado é salvo
  ↓
manifesto é atualizado
```

### Evolução futura

Uma fila poderá ser adicionada quando houver:

- várias tarefas simultâneas;
- necessidade de retomar tarefas após reinicialização;
- workers em computadores diferentes;
- controle de prioridade;
- agendamento.

Tecnologias futuras possíveis:

- Redis;
- RQ;
- Celery;
- Dramatiq.

Nenhuma delas será usada no primeiro protótipo.

## 9. Comunicação com o LiveRig Player

### WebSocket

Candidato principal para:

- play;
- pause;
- stop;
- posição atual;
- troca de música;
- estado do Player;
- mensagens de erro.

Motivos:

- comunicação bidirecional;
- implementação simples em aplicações web;
- adequado para atualizações frequentes de posição;
- funciona localmente sem internet.

### OSC

Será mantido como alternativa porque já faz parte do ecossistema atual do LiveRig e do REAPER.

A decisão será tomada após um protótipo medir:

- estabilidade;
- latência;
- facilidade de integração;
- comportamento após perda e recuperação da conexão.

## 10. Player de palco

O Player deverá ser leve e independente do ambiente de criação.

Stack candidata inicial:

- aplicação web local;
- HTML, CSS e JavaScript;
- reprodução por elemento de vídeo do navegador;
- WebSocket para receber comandos;
- modo tela cheia;
- cache e pré-carregamento dos próximos assets.

Alternativas futuras:

- Python com VLC ou mpv;
- aplicação Electron;
- player nativo.

A escolha definitiva dependerá de testes no computador de palco, especialmente no macOS High Sierra.

## 11. Docker

Docker será usado no HomeLab para serviços como:

- API;
- ComfyUI;
- workers;
- ferramentas auxiliares.

Durante o MVP, a aplicação também poderá rodar diretamente no Windows para reduzir variáveis durante o desenvolvimento.

Estrutura prevista:

```text
visualstudio/docker/
├── docker-compose.yml
├── Dockerfile.api
└── .env.example
```

Não será criado um container separado para cada módulo sem necessidade operacional.

## 12. Configuração

Configurações sensíveis ou específicas de ambiente ficarão em `.env`.

Exemplo:

```dotenv
VISUALSTUDIO_HOST=127.0.0.1
VISUALSTUDIO_PORT=8000
COMFYUI_URL=http://192.168.15.9:8188
ASSETS_ROOT=D:/LiveRigVisualStudio/assets
FFMPEG_PATH=ffmpeg
```

O repositório deverá conter apenas `.env.example`.

## 13. Organização de arquivos

```text
visualstudio/
├── api/          # FastAPI e endpoints
├── src/          # domínio, modelos e serviços
├── workers/      # geração e processamento
├── workflows/    # workflows do ComfyUI
├── prompts/      # templates de prompts
├── assets/       # arquivos locais ignorados pelo Git
├── docker/       # Dockerfiles e Compose
└── tests/        # testes automatizados futuros
```

A pasta `tests/` será criada quando o primeiro módulo executável for implementado.

## 14. Qualidade e testes

### pytest

Será usado para:

- validação de manifestos;
- testes da API;
- geração de comandos FFmpeg;
- criação e exportação de pacotes;
- comportamento dos serviços sem depender da GPU.

### Ruff

Será usado inicialmente para:

- lint;
- organização de imports;
- formatação.

### mypy

Será introduzido gradualmente após os modelos principais estarem estabilizados.

## 15. Dependências iniciais previstas

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
httpx
python-multipart
pillow
pytest
ruff
```

Dependências de IA não serão adicionadas à API principal quando puderem permanecer isoladas no ComfyUI ou em workers específicos.

## 16. Decisões adiadas

Ainda dependem de testes:

- modelo inicial de geração de imagens;
- instalação e parâmetros do ComfyUI;
- formato final do Player;
- codec e resolução ideais para o computador de palco;
- WebSocket ou OSC como protocolo principal;
- armazenamento definitivo dos assets;
- uso futuro de SQLite;
- necessidade real de fila de tarefas.

## 17. Critério para o primeiro protótipo

A stack será considerada validada quando conseguir:

1. criar um projeto para uma música;
2. importar uma imagem ou vídeo;
3. gerar um proxy;
4. registrar o asset em JSON;
5. montar uma sequência simples;
6. exportar um pacote;
7. reproduzir o pacote localmente em tela cheia.

A geração por IA será adicionada depois que esse fluxo básico estiver funcionando de ponta a ponta.
