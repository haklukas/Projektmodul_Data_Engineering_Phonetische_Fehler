const soundFiles = [
  "audio/audio1.wav",
  "audio/audio2.wav",
  "audio/audio3.wav"
];

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

const randomized = shuffle([...soundFiles]);
const player = document.getElementById("player");
const results = [];

let index = 0;
let currentFile = null;

function updateStatus() {
  const status = document.getElementById("status");
  status.textContent = `Audio ${index + 1} of ${randomized.length}`;
}

function sanitizeInput(str) {
  return str.replace(/[&<>"'\/]/g, function (s) {
    return ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
      "/": "&#47;"
    })[s];
  });
}

function nextSound() {
  if (index >= randomized.length) {
    sendResults();
    return;
  }

  updateStatus();

  currentFile = randomized[index];
  index++;
  player.src = currentFile;
}

document.getElementById("submitBtn").onclick = () => {
  const raw = document.getElementById("userInput").value;
  const input = sanitizeInput(raw);
  results.push({ file: currentFile, input });
  document.getElementById("userInput").value = "";
  nextSound();
};

function sendResults() {
  fetch("/survey_upload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data: results })
  })
  .then(r => r.json())
  .then(() => {
    document.getElementById("status").style.display = "none";
    document.getElementById("player").style.display = "none";
    document.getElementById("userInput").style.display = "none";
    document.getElementById("submitBtn").style.display = "none";

    document.getElementById("finishedMessage").style.display = "block";
  });
}

nextSound();
