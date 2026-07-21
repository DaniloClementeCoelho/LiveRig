# Roadmap — LiveRig Visual Studio

## Princípio de execução

O projeto será desenvolvido em etapas pequenas, cada uma com resultado observável e critério de aceite claro.

Não será adicionada complexidade antes de um teste demonstrar necessidade real.

## Fase 0 — Base documental

Objetivo: consolidar visão, arquitetura, stack e plano de execução.

Entregas:

- `00-VISAO.md`;
- `01-ARQUITETURA.md`;
- `02-ROADMAP.md`;
- `03-STACK.md`;
- `README.md`;
- `CHANGELOG.md`.

Critério de aceite:

- documentação suficiente para iniciar o MVP sem depender do histórico das conversas.

Status: em andamento.

## Fase 1 — Protótipo local mínimo

Objetivo: validar o fluxo básico com uma única música, sem IA e sem integração com o LiveRig.

Escopo:

- criar um projeto visual simples em JSON;
- carregar imagens e vídeos locais;
- definir uma sequência temporal manual;
- reproduzir a sequência em uma janela;
- executar tudo localmente no Windows de desenvolvimento.

Entregas:

- modelo inicial de manifesto;
- leitor de manifesto;
- player visual mínimo;
- projeto de exemplo para uma música.

Critério de aceite:

- abrir um manifesto e reproduzir uma sequência de imagens e vídeos na ordem definida.

Fora do escopo:

- geração por IA;
- ComfyUI;
- Docker;
- sincronização com REAPER;
- interface gráfica completa;
- banco de dados.

## Fase 2 — Integração básica com o LiveRig

Objetivo: validar que o player visual pode seguir os comandos principais do LiveRig.

Escopo:

- carregar automaticamente o projeto visual da música selecionada;
- receber play;
- receber pause;
- receber stop;
- receber posição temporal;
- recuperar sincronização após seek.

Protocolo inicial a testar:

1. WebSocket local;
2. OSC local como alternativa.

Critério de aceite:

- ao controlar a música no LiveRig, o player visual acompanha play, pause e posição sem interferir no áudio ou MIDI.

## Fase 3 — Pacote visual de palco

Objetivo: separar definitivamente criação e reprodução.

Escopo:

- criar estrutura de pacote autocontido;
- copiar apenas assets aprovados;
- validar arquivos ausentes;
- gerar checksums;
- registrar versão do formato;
- permitir reprodução offline.

Critério de aceite:

- copiar o pacote para o computador de palco e reproduzir sem acesso ao HomeLab ou à internet.

## Fase 4 — Biblioteca de assets

Objetivo: organizar imagens, vídeos, shaders e derivados de forma rastreável.

Escopo:

- cadastro de assets;
- identificação única;
- status: rascunho, aprovado ou descartado;
- associação com música;
- origem: importado, gerado ou derivado;
- metadados técnicos;
- thumbnails;
- proxies de baixa resolução.

Persistência inicial:

- arquivos JSON ou SQLite, conforme o teste de complexidade.

Critério de aceite:

- localizar, revisar e reutilizar assets sem depender da estrutura manual de pastas.

## Fase 5 — Processamento com FFmpeg

Objetivo: automatizar tarefas repetitivas de preparação de mídia.

Escopo:

- conversão de formatos;
- normalização de resolução;
- ajuste de frame rate;
- criação de loops;
- geração de thumbnails;
- criação de proxies;
- composição simples de imagens e vídeos;
- renderização final.

Critério de aceite:

- gerar automaticamente um vídeo de palco compatível a partir de assets heterogêneos.

## Fase 6 — Geração local de imagens

Objetivo: validar geração de imagens no HomeLab respeitando o limite de 4 GB de VRAM.

Escopo:

- instalar ou integrar ComfyUI;
- testar workflow leve;
- gerar imagens em resolução moderada;
- registrar prompt, modelo, seed e workflow;
- importar o resultado para a biblioteca.

Estratégia:

- começar com imagens estáticas;
- usar modelos compatíveis com baixa VRAM;
- evitar manter Ollama e modelos de imagem pesados carregados simultaneamente;
- executar um job por vez.

Critério de aceite:

- gerar uma imagem utilizável no HomeLab sem instabilidade do servidor.

## Fase 7 — Geração de loops e efeitos

Objetivo: transformar imagens e vídeos curtos em material visual dinâmico.

Escopo:

- zoom e pan;
- parallax simples;
- partículas;
- glitch;
- distorções;
- shaders;
- loops contínuos;
- transições sincronizáveis.

Critério de aceite:

- produzir um loop visual contínuo e adequado para projeção em show.

## Fase 8 — Interface de criação

Objetivo: reduzir a dependência de edição manual de JSON e comandos.

Escopo:

- criar projeto por música;
- importar assets;
- visualizar thumbnails;
- aprovar ou descartar;
- montar sequência;
- editar duração e transições;
- exportar pacote.

Critério de aceite:

- montar um projeto visual completo sem editar arquivos manualmente.

## Fase 9 — Workers e tarefas assíncronas

Objetivo: adicionar processamento em segundo plano somente quando o fluxo síncrono se tornar limitante.

Escopo possível:

- fila de tarefas;
- acompanhamento de progresso;
- cancelamento;
- repetição após erro;
- workers separados por função.

Critério para iniciar esta fase:

- jobs longos bloquearem a interface ou impedirem uso normal do sistema.

Critério de aceite:

- iniciar uma renderização longa e continuar usando a interface normalmente.

## Fase 10 — Distribuição no HomeLab

Objetivo: distribuir serviços conforme capacidade dos equipamentos disponíveis.

Possível divisão:

- `homelab-ai01`: IA e processamento acelerado por GPU;
- `homelab-srv01`: API, biblioteca e serviços auxiliares;
- Windows de desenvolvimento: interface e revisão;
- computador de palco: player leve e offline.

Critério para iniciar esta fase:

- o MVP local estar estável e a distribuição oferecer benefício mensurável.

## Fase 11 — Recursos avançados

Possibilidades futuras:

- análise automática de estrutura musical;
- leitura de regions e markers do REAPER;
- sugestões de cenas por trecho;
- geração de prompts baseada em letra e estilo;
- sincronização por eventos musicais;
- edição por timeline;
- pré-visualização remota;
- múltiplas saídas de vídeo;
- controle de projetor;
- integração com serviços externos de geração;
- renderização em hardware mais potente.

Esses recursos não fazem parte do MVP.

## Ordem imediata de implementação

Após concluir a documentação:

1. definir o manifesto mínimo;
2. criar um projeto de exemplo para uma música;
3. construir um player local mínimo;
4. validar imagens;
5. validar vídeos;
6. validar troca de cenas por tempo;
7. somente depois integrar com o LiveRig.

## Música piloto

O primeiro protótipo deverá usar apenas uma música.

Candidata inicial:

- `A Little Respect`.

Motivos:

- já faz parte do repertório;
- possui identidade visual clara;
- permite testar estética synthpop, neon, fotos da banda e loops;
- já foi usada como referência nas discussões do projeto.

## Regras de avanço

Uma fase somente será considerada concluída quando:

- existir um teste reproduzível;
- o resultado tiver sido validado;
- limitações e decisões estiverem documentadas;
- o código estiver versionado;
- o `CHANGELOG.md` estiver atualizado.

Falhas encontradas durante os testes devem ser tratadas antes de ampliar o escopo.
## Progresso registrado

Status em 2026-07-19:

- Fase 1 iniciada e validada parcialmente: manifesto piloto e player local funcionando.
- Fase 2 validada parcialmente: player seguindo estado do LiveRig por WebSocket.
- Fase 4 iniciada: `assets.json` criado sob demanda para registrar imagens geradas.
- Fase 6 iniciada e validada parcialmente: ComfyUI recebeu workflow SDXL Turbo, gerou imagem e retornou arquivo.

Proximo foco recomendado:

1. listar assets do projeto por endpoint;
2. exibir assets no player ou em uma tela simples de revisao;
3. permitir aprovar ou descartar assets;
4. usar assets aprovados no manifesto de cenas;
5. depois avancar para thumbnails, proxies e exportacao.
