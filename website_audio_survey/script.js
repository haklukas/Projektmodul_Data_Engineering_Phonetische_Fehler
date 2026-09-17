function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function sanitizeInput(str) {
  return str.replace(/[&<>"'\/]/g, function (s) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
      "/": "&#47;"
    }[s];
  });
}

async function loadAudioMetadata(endpoint, errorMessage) {
  const metadataUrl = window.location.port === "5000"
    ? `/${endpoint}`
    : `http://localhost:5000/${endpoint}`;
  const response = await fetch(metadataUrl);
  if (!response.ok) throw new Error(errorMessage);
  return response.json();
}

class SurveyTab {
  constructor(panel, tabName, audioItems) {
    this.panel = panel;
    this.tabName = tabName;
    this.randomized = shuffle([...audioItems]);
    this.results = [];
    this.index = 0;
    this.currentFile = null;
    this.currentAudioText = "";
    this.uploadGeneration = 0;
    this.status = panel.querySelector('[data-role="status"]');
    this.player = panel.querySelector('[data-role="player"]');
    this.surveyInputs = panel.querySelector('[data-role="surveyInputs"]');
    this.sourceInputs = [...panel.querySelectorAll('[data-role="source"]')];
    this.humanCloseness = panel.querySelector('[data-role="humanCloseness"]');
    this.humanClosenessValue = panel.querySelector('[data-role="humanClosenessValue"]');
    this.userInput = panel.querySelector('[data-role="userInput"]');
    this.misheardSection = panel.querySelector('[data-role="misheardSection"]');
    this.misheardText = panel.querySelector('[data-role="misheardText"]');
    this.misinterpretationLikelihood = panel.querySelector('[data-role="misinterpretationLikelihood"]');
    this.misinterpretationLikelihoodValue = panel.querySelector('[data-role="misinterpretationLikelihoodValue"]');
    this.originalAudioSection = panel.querySelector('[data-role="originalAudioSection"]');
    this.originalAudioText = panel.querySelector('[data-role="originalAudioText"]');
    this.originalAudioRealism = panel.querySelector('[data-role="originalAudioRealism"]');
    this.originalAudioRealismValue = panel.querySelector('[data-role="originalAudioRealismValue"]');
    this.submitButton = panel.querySelector('[data-role="submit"]');
    this.skipButton = panel.querySelector('[data-role="skip"]');
    this.resetButton = panel.querySelector('[data-role="reset"]');
    this.finishedMessage = panel.querySelector('[data-role="finishedMessage"]');
    this.attachListeners();
    this.nextSound();
  }

  attachListeners() {
    this.sourceInputs.forEach(input => input.addEventListener("change", () => {
      this.sourceInputs.forEach(otherInput => {
        otherInput.checked = otherInput === input;
      });
      this.updateFormState();
    }));

    this.humanCloseness.addEventListener("input", () => {
      this.humanCloseness.dataset.touched = "true";
      this.humanClosenessValue.textContent = this.humanCloseness.value;
      this.updateFormState();
    });

    this.misinterpretationLikelihood.addEventListener("input", () => {
      this.misinterpretationLikelihood.dataset.touched = "true";
      this.misinterpretationLikelihoodValue.textContent = this.misinterpretationLikelihood.value;
      this.updateFormState();
    });

    this.originalAudioRealism.addEventListener("input", () => {
      this.originalAudioRealism.dataset.touched = "true";
      this.originalAudioRealismValue.textContent = this.originalAudioRealism.value;
      this.updateFormState();
    });

    this.userInput.addEventListener("input", () => this.updateFormState());
    this.submitButton.addEventListener("click", () => this.submitCurrent());
    this.skipButton.addEventListener("click", () => {
      this.clearCurrentInputs();
      this.nextSound();
    });
    this.resetButton.addEventListener("click", () => this.reset());
  }

  selectedSource() {
    return this.sourceInputs.find(input => input.checked)?.value || "";
  }

  updateFormState() {
    const firstStageComplete = Boolean(this.selectedSource()) &&
      this.humanCloseness.dataset.touched === "true" &&
      this.userInput.value.trim() !== "";
    const secondStageComplete = this.misinterpretationLikelihood.dataset.touched === "true";

    this.misheardSection.hidden = !firstStageComplete;
    this.originalAudioSection.hidden = !secondStageComplete;
    this.submitButton.disabled = !firstStageComplete || !secondStageComplete || this.originalAudioRealism.dataset.touched !== "true";
  }

  updateStatus() {
    this.status.textContent = `Audio ${this.index + 1} of ${this.randomized.length}`;
  }

  nextSound() {
    if (this.index >= this.randomized.length) {
      this.sendResults();
      return;
    }

    this.updateStatus();
    const currentAudio = this.randomized[this.index];
    this.currentFile = currentAudio.file;
    this.currentAudioText = currentAudio.text;
    this.index++;
    this.player.src = this.currentFile;
    this.originalAudioText.textContent = this.currentAudioText;
  }

  clearCurrentInputs() {
    this.sourceInputs.forEach(input => {
      input.checked = false;
    });
    this.humanCloseness.dataset.touched = "false";
    this.misinterpretationLikelihood.dataset.touched = "false";
    this.originalAudioRealism.dataset.touched = "false";
    this.humanClosenessValue.textContent = "Select a rating";
    this.misinterpretationLikelihoodValue.textContent = "Select a rating";
    this.originalAudioRealismValue.textContent = "Select a rating";
    this.userInput.value = "";
    this.updateFormState();
  }

  submitCurrent() {
    this.results.push({
      tab: this.tabName,
      file: this.currentFile,
      source: this.selectedSource(),
      humanCloseness: Number(this.humanCloseness.value),
      heardText: sanitizeInput(this.userInput.value.trim()),
      misheardText: this.misheardText.textContent,
      misinterpretationLikelihood: Number(this.misinterpretationLikelihood.value),
      originalAudioText: this.currentAudioText,
      originalAudioRealism: Number(this.originalAudioRealism.value)
    });
    this.clearCurrentInputs();
    this.nextSound();
  }

  reset() {
    this.uploadGeneration++;
    this.index = 0;
    this.currentFile = null;
    this.currentAudioText = "";
    this.results.length = 0;
    this.status.hidden = false;
    this.player.hidden = false;
    this.surveyInputs.hidden = false;
    this.finishedMessage.hidden = true;
    this.skipButton.disabled = false;
    this.clearCurrentInputs();
    this.nextSound();
  }

  sendResults() {
    const uploadGeneration = ++this.uploadGeneration;
    this.skipButton.disabled = true;
    fetch("http://localhost:5000/survey_upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: this.results })
    })
      .then(response => response.json())
      .then(() => {
        if (uploadGeneration !== this.uploadGeneration) return;
        this.status.hidden = true;
        this.player.hidden = true;
        this.surveyInputs.hidden = true;
        this.finishedMessage.hidden = false;
      });
  }
}

async function initializeSurveys() {
  const cleanPanel = document.getElementById("cleanAudioPanel");
  const cleanStatus = cleanPanel.querySelector('[data-role="status"]');
  cleanStatus.textContent = "Loading clean audio...";

  const dirtyPanel = document.getElementById("dirtyAudioPanel");
  const dirtyStatus = dirtyPanel.querySelector('[data-role="status"]');
  dirtyStatus.textContent = "Loading dirty audio...";

  try {
    const dirtyAudio = await loadAudioMetadata(
      "dirty_audio_metadata",
      "Dirty audio metadata could not be loaded"
    );
    new SurveyTab(dirtyPanel, "Dirty Audio", dirtyAudio);
  } catch (error) {
    dirtyStatus.textContent = error.message;
  }

  try {
    const cleanAudio = await loadAudioMetadata(
      "clean_audio_metadata",
      "Clean audio metadata could not be loaded"
    );
    new SurveyTab(cleanPanel, "Clean Audio", cleanAudio);
  } catch (error) {
    cleanStatus.textContent = error.message;
  }
}

initializeSurveys();

const tabButtons = [...document.querySelectorAll('[role="tab"]')];
const tabPanels = [...document.querySelectorAll('[role="tabpanel"]')];
tabButtons.forEach(button => button.addEventListener("click", () => {
  tabButtons.forEach(tab => tab.setAttribute("aria-selected", String(tab === button)));
  tabPanels.forEach(panel => {
    panel.hidden = panel.id !== button.getAttribute("aria-controls");
  });
}));
