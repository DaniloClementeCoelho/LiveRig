const manifestPath = "../projects/a-little-respect/orquestrador.json";
const liveRigBaseUrl = "http://127.0.0.1:8080";
const liveRigWebSocketUrl = "ws://127.0.0.1:8080/ws";

const stage = document.querySelector("#stage");
const visualLayer = document.querySelector("#visualLayer");
const songTitle = document.querySelector("#songTitle");
const sceneName = document.querySelector("#sceneName");
const timecode = document.querySelector("#timecode");
const syncStatus = document.querySelector("#syncStatus");
const playButton = document.querySelector("#playButton");
const pauseButton = document.querySelector("#pauseButton");
const stopButton = document.querySelector("#stopButton");

let manifest = null;
let isPlaying = false;
let isLiveRigConnected = false;
let startedAt = 0;
let pausedAtMs = 0;
let animationFrame = null;
let currentSceneId = null;
let totalDurationMs = 0;
let liveRigSocket = null;
let loadedSongId = null;

function formatTime(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  const millis = Math.floor(ms % 1000).toString().padStart(3, "0");
  return `${minutes}:${seconds}.${millis}`;
}

function setSyncStatus(text) {
  syncStatus.textContent = text;
}

function normalizeManifest(rawManifest) {
  rawManifest.scenes = rawManifest.scenes
    .map((scene) => ({
      ...scene,
      start_ms: Number(scene.start_ms),
      duration_ms: Number(scene.duration_ms),
    }))
    .sort((a, b) => a.start_ms - b.start_ms);

  return rawManifest;
}

function setManifest(nextManifest) {
  manifest = normalizeManifest(nextManifest);
  totalDurationMs = manifest.scenes.reduce((endMs, scene) => {
    return Math.max(endMs, scene.start_ms + scene.duration_ms);
  }, 0);

  songTitle.textContent = `${manifest.song.title} - ${manifest.song.artist}`;
  currentSceneId = null;
  renderAt(0);
}

function findScene(elapsedMs) {
  return manifest.scenes.find((scene) => {
    const start = Number(scene.start_ms);
    const end = Number(scene.start_ms) + Number(scene.duration_ms);
    return elapsedMs >= start && elapsedMs < end;
  });
}

function renderScene(scene, elapsedMs) {
  timecode.textContent = formatTime(elapsedMs);

  if (!scene) {
    sceneName.textContent = "Fim";
    visualLayer.innerHTML = "";
    return;
  }

  if (scene.id === currentSceneId) {
    return;
  }

  currentSceneId = scene.id;
  sceneName.textContent = scene.id;

  if (scene.type === "color") {
    visualLayer.innerHTML = "";
    stage.style.backgroundColor = scene.color;
    return;
  }

  if (scene.type === "image") {
    stage.style.backgroundColor = scene.background_color || "#05070a";
    visualLayer.innerHTML = "";

    const image = document.createElement("img");
    image.src = scene.src;
    image.alt = scene.alt || scene.id;
    image.className = "scene-image";
    visualLayer.appendChild(image);
    return;
  }

  if (scene.type === "video") {
    stage.style.backgroundColor = scene.background_color || "#05070a";
    visualLayer.innerHTML = "";

    const video = document.createElement("video");
    video.src = scene.src;
    video.className = "scene-video";
    video.muted = scene.muted !== false;
    video.loop = scene.loop !== false;
    video.playsInline = true;
    video.autoplay = true;
    visualLayer.appendChild(video);

    video.play().catch(() => {
      sceneName.textContent = `${scene.id} (aguardando play do navegador)`;
    });
  }
}

function renderAt(elapsedMs) {
  const boundedElapsedMs = Math.max(0, Math.min(elapsedMs, totalDurationMs));

  if (boundedElapsedMs >= totalDurationMs) {
    currentSceneId = null;
    renderScene(null, totalDurationMs);
    return;
  }

  const scene = findScene(boundedElapsedMs);
  renderScene(scene, boundedElapsedMs);
}

function tick() {
  if (!isPlaying) {
    return;
  }

  const elapsedMs = performance.now() - startedAt;

  if (elapsedMs >= totalDurationMs) {
    isPlaying = false;
    pausedAtMs = 0;
    currentSceneId = null;
    renderScene(null, totalDurationMs);
    return;
  }

  renderAt(elapsedMs);

  animationFrame = window.requestAnimationFrame(tick);
}

function play() {
  if (isLiveRigConnected || isPlaying || !manifest) {
    return;
  }

  if (pausedAtMs >= totalDurationMs) {
    pausedAtMs = 0;
    currentSceneId = null;
  }

  isPlaying = true;
  startedAt = performance.now() - pausedAtMs;
  animationFrame = window.requestAnimationFrame(tick);
}

function pause() {
  if (isLiveRigConnected || !isPlaying) {
    return;
  }

  isPlaying = false;
  pausedAtMs = performance.now() - startedAt;
  window.cancelAnimationFrame(animationFrame);
}

function stop() {
  if (isLiveRigConnected) {
    return;
  }

  isPlaying = false;
  pausedAtMs = 0;
  currentSceneId = null;
  window.cancelAnimationFrame(animationFrame);
  renderAt(0);
}

async function loadManifestFromPath(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`Falha ao carregar manifesto: ${response.status}`);
  }

  setManifest(await response.json());
}

async function loadLiveRigManifest(songId) {
  if (!songId || songId === loadedSongId) {
    return;
  }

  const syncUrl = `${liveRigBaseUrl}/api/songs/${encodeURIComponent(songId)}/sync`;
  const response = await fetch(syncUrl);

  if (!response.ok) {
    return;
  }

  const payload = await response.json();
  const manifestSrc = payload.visual && payload.visual.manifest ? payload.visual.manifest.src : null;

  if (!manifestSrc) {
    return;
  }

  await loadManifestFromPath(`${liveRigBaseUrl}${manifestSrc}`);
  loadedSongId = songId;
}

function applyLiveRigPlaybackState(payload) {
  if (!payload) {
    return;
  }

  loadLiveRigManifest(payload.current_song_id).catch(() => {
    setSyncStatus("LiveRig conectado");
  });

  if (!manifest) {
    return;
  }

  const positionSeconds = Number(payload.position || 0);
  const elapsedMs = positionSeconds * 1000;

  isPlaying = Boolean(payload.playing);
  pausedAtMs = Math.max(0, elapsedMs);
  window.cancelAnimationFrame(animationFrame);
  renderAt(elapsedMs);
}

function connectLiveRig() {
  try {
    liveRigSocket = new WebSocket(liveRigWebSocketUrl);
  } catch (error) {
    return;
  }

  liveRigSocket.addEventListener("open", () => {
    isLiveRigConnected = true;
    setSyncStatus("LiveRig conectado");
  });

  liveRigSocket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);

    if (message.type === "playback_state") {
      applyLiveRigPlaybackState(message.payload);
    }
  });

  liveRigSocket.addEventListener("close", () => {
    isLiveRigConnected = false;
    liveRigSocket = null;
    setSyncStatus("Modo local");
  });

  liveRigSocket.addEventListener("error", () => {
    isLiveRigConnected = false;
    setSyncStatus("Modo local");
  });
}

async function loadManifest() {
  await loadManifestFromPath(manifestPath);
  connectLiveRig();
}

playButton.addEventListener("click", play);
pauseButton.addEventListener("click", pause);
stopButton.addEventListener("click", stop);

loadManifest().catch((error) => {
  songTitle.textContent = "Erro ao carregar manifesto";
  sceneName.textContent = error.message;
});
