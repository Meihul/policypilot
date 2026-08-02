const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("pdfFile");
const selectedFile = document.getElementById("selectedFile");

const analyzeBtn = document.getElementById("analyzeBtn");
const languageSelect = document.getElementById("language");

const loading = document.getElementById("loading");
const results = document.getElementById("results");

const languageDetected = document.getElementById("languageDetected");
const keyPhrases = document.getElementById("keyPhrases");
const entities = document.getElementById("entities");
const translation = document.getElementById("translation");
const originalText = document.getElementById("originalText");

let selectedPDF = null;

/* ===============================
   Upload
================================ */

uploadArea.addEventListener("click", () => {

    fileInput.click();

});

fileInput.addEventListener("change", (event) => {

    if (event.target.files.length > 0) {

        selectedPDF = event.target.files[0];

        selectedFile.textContent =
            "Selected: " + selectedPDF.name;

    }

});

/* ===============================
   Analyze
================================ */

analyzeBtn.addEventListener("click", analyzeDocument);

async function analyzeDocument() {

    if (!selectedPDF) {
        showError("Please choose a PDF document first.");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    loading.classList.remove("hidden");
    results.classList.add("hidden");

    const formData = new FormData();
    formData.append("file", selectedPDF);

    try {

        const response = await fetch(
    `/upload?language=${languageSelect.value}`,
    {
        method: "POST",
        body: formData
    }
);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Unable to analyze document.");
        }

        displayResults(data);

    } catch (error) {

        console.error(error);
        showError(error.message || "Something went wrong.");

    } finally {

        loading.classList.add("hidden");
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Policy";

    }
}
/* ===============================
   Display Results
================================ */

function displayResults(data) {

    languageDetected.textContent =
        data.language_detected || "Not detected";

    translation.textContent =
        data.translated_text || "No translation available.";

    originalText.textContent =
        data.original_text || "";

    keyPhrases.innerHTML = "";

    entities.innerHTML = "";

    // Key Phrases
    if (data.key_phrases && data.key_phrases.length > 0) {

        data.key_phrases.forEach((phrase) => {

            const chip = document.createElement("span");

            chip.className = "tag";

            chip.textContent = phrase;

            keyPhrases.appendChild(chip);

        });

    } else {

        keyPhrases.innerHTML = "<p>No key phrases found.</p>";

    }

    // Entities
    if (data.entities && data.entities.length > 0) {

        data.entities.forEach((entity) => {

            const div = document.createElement("div");

            div.className = "entity";

            div.innerHTML = `
                <strong>${entity.text}</strong>
                <span>${entity.category}</span>
            `;

            entities.appendChild(div);

        });

    } else {

        entities.innerHTML = "<p>No entities found.</p>";

    }

    results.classList.remove("hidden");

    results.scrollIntoView({
        behavior: "smooth"
    });

}

/* ===============================
   Error Popup
================================ */

function showError(message) {

    const old = document.querySelector(".error-box");

    if (old) old.remove();

    const box = document.createElement("div");

    box.className = "error-box";

    box.textContent = message;

    document.body.appendChild(box);

    setTimeout(() => {

        box.remove();

    }, 3000);

}