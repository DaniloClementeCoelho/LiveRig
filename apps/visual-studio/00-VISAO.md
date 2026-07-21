# Visão — LiveRig Visual Studio

## Objetivo

O LiveRig Visual Studio será o módulo responsável por criar, organizar e preparar conteúdo visual sincronizado com músicas executadas pelo LiveRig.

O sistema deverá permitir gerar e reutilizar imagens, vídeos curtos, loops, shaders e outros elementos visuais que possam ser exibidos durante apresentações ao vivo.

## Problema

Atualmente, o LiveRig controla áudio, letras e comandos MIDI, mas não possui uma solução integrada para conteúdo visual.

A preparação manual de vídeos para cada música exige tempo, ferramentas diferentes e organização externa. Além disso, vídeos tradicionais podem consumir muito armazenamento e dificultar alterações rápidas.

O LiveRig Visual Studio deverá reduzir esse trabalho por meio de geração assistida, reutilização de assets e automação.

## Usuário principal

O usuário principal será o músico ou responsável pela preparação do show.

Inicialmente, o sistema será desenvolvido para uso da banda Firebird e integrado ao fluxo atual do LiveRig.

## Funcionalidades previstas

O sistema deverá permitir:

- associar conteúdo visual a uma música;
- importar imagens e vídeos existentes;
- gerar imagens e loops a partir de prompts;
- criar variações visuais usando IA;
- combinar fotos da banda com conteúdo gerado;
- utilizar shaders e efeitos procedurais;
- organizar uma biblioteca de assets reutilizáveis;
- gerar arquivos finais compatíveis com o módulo de reprodução;
- registrar prompts, modelos e workflows utilizados;
- permitir futura sincronização com a linha do tempo da música.

## Integração com o LiveRig

O Visual Studio será responsável pela preparação do conteúdo.

A reprodução durante o show será responsabilidade de um módulo separado e leve, integrado ao LiveRig.

Fluxo previsto:

```text
Música
  ↓
LiveRig Visual Studio
  ↓
Imagens, vídeos, shaders e metadados
  ↓
Biblioteca visual
  ↓
Módulo de reprodução do LiveRig
  ↓
Projetor ou tela externa
```

O REAPER continuará responsável pelo áudio. O processamento visual não deverá competir com ele durante o show.

## Uso de inteligência artificial

A inteligência artificial poderá ser usada para:

- interpretar o tema e a atmosfera de uma música;
- sugerir conceitos visuais;
- gerar prompts;
- gerar imagens;
- gerar pequenos loops de vídeo;
- criar variações de assets;
- classificar e organizar conteúdo.

A geração poderá ocorrer no HomeLab ou em serviços externos, dependendo da capacidade necessária.

O servidor atual possui uma NVIDIA GTX 1650 Max-Q com 4 GB de VRAM. Portanto, o projeto deverá priorizar modelos leves, geração em baixa resolução, processamento em etapas e uso de ferramentas procedurais.

## Princípios

- O LiveRig usado no palco deve permanecer leve e estável.
- Geração e reprodução devem ser componentes separados.
- Assets devem ser reutilizáveis.
- Todo conteúdo deve possuir metadados.
- Workflows e prompts importantes devem ser versionados.
- O sistema deve funcionar mesmo sem conexão com a internet durante o show.
- A arquitetura não deve depender exclusivamente de uma ferramenta específica.
- Vídeos grandes devem ser evitados quando efeitos em tempo real ou loops menores forem suficientes.

## Fora do escopo inicial

Na primeira versão, o sistema não deverá:

- gerar vídeos longos completos;
- editar áudio;
- substituir o REAPER;
- processar IA durante uma apresentação;
- controlar iluminação de palco;
- funcionar como editor profissional de vídeo;
- depender de geração em tempo real;
- sincronizar automaticamente cada batida da música.

## Primeira entrega

A primeira entrega funcional deverá permitir:

1. selecionar uma música;
2. definir um conceito visual;
3. gerar ou importar um pequeno conjunto de assets;
4. criar um loop de vídeo curto;
5. exportar o resultado em formato compatível com o futuro módulo de reprodução do LiveRig.

## Evolução futura

Após a validação da primeira versão, o sistema poderá incluir:

- análise automática de estrutura musical;
- timeline visual;
- sincronização por seções da música;
- transições controladas pelo LiveRig;
- múltiplas telas;
- geração procedural em tempo real;
- integração com MIDI;
- integração com OSC;
- integração com iluminação;
- biblioteca compartilhada entre músicas;
- sugestões automáticas de identidade visual para cada show.
