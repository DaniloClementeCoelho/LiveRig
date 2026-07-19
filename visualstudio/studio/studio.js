const form = document.querySelector("#generateForm");
const songNameInput = document.querySelector("#songName");
const promptInput = document.querySelector("#prompt");
const negativePromptInput = document.querySelector("#negativePrompt");
const generateButton = document.querySelector("#generateButton");
const statusText = document.querySelector("#status");
const previewImage = document.querySelector("#previewImage");
const resultText = document.querySelector("#result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  generateButton.disabled = true;
  statusText.textContent = "Gerando imagem no HomeLab...";
  resultText.textContent = "";
  previewImage.style.display = "none";

  try {
    const response = await fetch("http://127.0.0.1:8000/api/studio/generate-image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        song_name: songNameInput.value,
        prompt: promptInput.value,
        negative_prompt: negativePromptInput.value,
        seed: 0,
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || `Erro HTTP ${response.status}`);
    }

    previewImage.src = `http://127.0.0.1:8000${payload.image.url}`;
    previewImage.style.display = "block";
    statusText.textContent = `Imagem salva em ${payload.server_output_folder}`;
    resultText.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    statusText.textContent = `Erro: ${error.message}`;
  } finally {
    generateButton.disabled = false;
  }
});
