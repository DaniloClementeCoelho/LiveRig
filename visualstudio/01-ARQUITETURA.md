# Arquitetura — LiveRig Visual Studio

## Objetivo arquitetural

Separar claramente a preparação visual da reprodução durante o show.

O ambiente de criação poderá usar IA, geração de imagens, renderização e processamento pesado. O ambiente de palco deverá apenas reproduzir conteúdo pronto, com baixo consumo e alta previsibilidade.

## Visão geral

```text
Usuário
  ↓
Interface do Visual Studio
  ↓
API de orquestração
  ├── Biblioteca de assets
  ├── Gerador de prompts
  ├── Workflows de imagem e vídeo
  ├── Processamento e conversão
  └── Metadados do projeto
        ↓
Pacote visual exportado
        ↓
LiveRig Player
        ↓
Projetor ou segunda tela
```

## Componentes

### 1. Interface do Visual Studio

Responsável por:

- selecionar a música;
- definir conceito, estilo e referências;
- importar fotos, vídeos e shaders;
- iniciar gerações;
- visualizar resultados;
- aprovar assets;
- montar a sequência visual;
- exportar o pacote final.

A interface não deverá conter lógica específica de modelos de IA.

### 2. API de orquestração

Camada central responsável por:

- receber solicitações da interface;
- validar parâmetros;
- criar e acompanhar tarefas;
- chamar workers especializados;
- registrar resultados e erros;
- controlar o estado de cada projeto visual.

A API deverá abstrair as ferramentas utilizadas. Assim, ComfyUI ou outro gerador poderá ser substituído sem alterar a interface.

### 3. Workers

Processos especializados para tarefas potencialmente demoradas:

- geração de imagens;
- geração de loops curtos;
- aplicação de efeitos;
- criação de proxies de baixa resolução;
- conversão de formatos;
- composição com fotos da banda;
- criação de thumbnails;
- renderização final.

Inicialmente, os workers poderão operar de forma síncrona e simples. Uma fila de tarefas somente será adicionada quando houver necessidade real.

### 4. Biblioteca de assets

Cada asset deverá possuir:

- identificador único;
- tipo: imagem, vídeo, áudio auxiliar ou shader;
- arquivo original;
- arquivo otimizado, quando aplicável;
- origem: importado, gerado ou derivado;
- prompt e prompt negativo;
- modelo e workflow utilizados;
- resolução, duração e formato;
- música e projeto relacionados;
- status: rascunho, aprovado ou descartado.

Os arquivos grandes não deverão ser armazenados diretamente no Git. O repositório manterá apenas código, documentação, prompts, workflows e exemplos pequenos.

### 5. Projeto visual por música

Cada música terá um manifesto próprio descrevendo:

- identidade da música;
- conceito visual;
- assets aprovados;
- ordem de reprodução;
- duração e repetição;
- transições;
- pontos futuros de sincronização;
- configuração de exportação.

Formato inicial sugerido: JSON.

Exemplo conceitual:

```json
{
  "song_id": "a-little-respect",
  "title": "A Little Respect",
  "concept": "neon retro synthpop",
  "scenes": [
    {
      "asset": "intro-loop.mp4",
      "start_ms": 0,
      "loop": true
    }
  ]
}
```

### 6. Exportador

Responsável por criar um pacote autocontido para o palco contendo:

- manifesto validado;
- vídeos e imagens otimizados;
- thumbnails, quando necessários;
- checksums dos arquivos;
- versão do formato do pacote.

O pacote não deverá depender do HomeLab nem da internet para ser reproduzido.

### 7. LiveRig Player

Componente futuro, separado do Visual Studio.

Responsabilidades:

- carregar o pacote visual;
- pré-carregar os próximos assets;
- reproduzir em tela cheia;
- receber comandos do LiveRig;
- manter sincronização básica;
- registrar erros sem interromper áudio ou MIDI.

O Player não executará modelos de IA nem renderizações pesadas durante o show.

## Fluxos principais

### Criação

```text
Criar projeto da música
  ↓
Definir conceito
  ↓
Importar ou gerar assets
  ↓
Revisar e aprovar
  ↓
Montar sequência
  ↓
Gerar pacote de palco
```

### Reprodução

```text
LiveRig abre a música
  ↓
Player carrega o pacote correspondente
  ↓
LiveRig envia play, pause e posição
  ↓
Player apresenta o conteúdo visual
```

## Comunicação entre LiveRig e Player

A primeira versão deverá priorizar um protocolo local simples.

Opções compatíveis com a arquitetura atual:

1. WebSocket local;
2. OSC local;
3. HTTP local para comandos administrativos.

A decisão final será validada após um protótipo. WebSocket é o candidato principal para estado e posição contínua; OSC poderá ser mantido como alternativa por já existir no ecossistema do LiveRig e REAPER.

## Execução no HomeLab

O servidor principal possui:

- Intel Core i7-1165G7;
- 16 GB de RAM;
- NVIDIA GTX 1650 Max-Q com 4 GB de VRAM;
- Ubuntu Server e Docker.

Essas limitações determinam que:

- geração local deve começar com imagens e modelos leves;
- vídeo por IA deverá usar resolução e duração reduzidas;
- modelos grandes não poderão permanecer carregados simultaneamente;
- proxies deverão ser usados durante a edição;
- renderizações pesadas poderão ser executadas em etapas;
- serviços externos deverão permanecer como opção, não dependência.

## Implantação inicial

Primeiro estágio:

```text
Windows de desenvolvimento
  ├── interface
  ├── API
  └── edição e revisão

HomeLab Ubuntu
  ├── geração local
  ├── processamento em containers
  └── armazenamento de assets

Computador de palco
  ├── LiveRig
  └── Player visual leve
```

Durante o MVP, a API também poderá rodar integralmente no Windows para simplificar os primeiros testes.

## Organização do código

```text
visualstudio/
├── api/          # endpoints e orquestração
├── workers/      # geração e processamento
├── src/          # domínio e serviços compartilhados
├── workflows/    # workflows versionados
├── prompts/      # templates de prompts
├── docker/       # containers e compose
└── assets/       # somente exemplos e arquivos locais ignorados pelo Git
```

## Decisões iniciais

- criação e reprodução serão separadas;
- o palco funcionará offline;
- IA não será executada durante o show;
- a API esconderá detalhes dos geradores;
- cada música terá manifesto próprio;
- assets grandes ficarão fora do Git;
- o MVP evitará filas, bancos complexos e microsserviços;
- o primeiro protótipo será validado com uma única música.

## Pontos ainda não decididos

- tecnologia da interface;
- formato definitivo do manifesto;
- banco de metadados;
- ferramenta principal de geração;
- protocolo definitivo entre LiveRig e Player;
- formato de vídeo otimizado para o computador de palco;
- local definitivo de armazenamento dos assets.

Esses itens serão definidos em `03-STACK.md` e confirmados por testes pequenos antes da implementação completa.
