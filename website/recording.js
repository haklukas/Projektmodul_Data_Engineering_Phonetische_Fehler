const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const audioPlayerDiv = document.getElementById('audioPlaybackDiv');
const audioPlayer = document.getElementById('audioPlayback');
const submitBtn = document.getElementById('submitBtn');

const words = [
  "Bosnien und Herzegowina",
  "L'arc de Triomphe",
  "Samsung",
  "19543",
  "a warm evening with ice cream",
  "Maria Sklodowska-Curie"
];

audioBlob = null;

stopButton.disabled = true;
submitBtn.disabled = true;
audioPlayerDiv.hidden = true;

currentWordIndex = 0;
document.getElementById('nextWord').textContent = words[currentWordIndex];

if (navigator.mediaDevices.getUserMedia) {
  console.log("The mediaDevices.getUserMedia() method is supported.");

  const constraints = { audio: true };
  let chunks = [];

  let onSuccess = function (stream) {
    const mediaRecorder = new MediaRecorder(stream);

    startButton.onclick = function () {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("Recorder started.");
      startButton.style.background = "red";
      stopButton.style.background = "green";

      stopButton.disabled = false;
      startButton.disabled = true;
      audioPlayerDiv.hidden = true;
      submitBtn.disabled = true;
    };

    stopButton.onclick = function () {
      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("Recorder stopped.");
      startButton.style.background = "";
      startButton.style.color = "";
      stopButton.style.background = "";

      stopButton.disabled = true;
      startButton.disabled = false;
    };

    mediaRecorder.onstop = function (e) {
      console.log("Last data to read (after MediaRecorder.stopButton() called).");

      audioBlob = new Blob(chunks, { type: 'audio/wav' });
      chunks = [];
      const audioURL = window.URL.createObjectURL(audioBlob);
      audioPlayer.src = audioURL;
      audioPlayerDiv.hidden = false;
      submitBtn.disabled = false;
      console.log("recorder stopped");
    };

    mediaRecorder.ondataavailable = function (e) {
      chunks.push(e.data);
    };
  };

  let onError = function (err) {
    console.log("The following error occured: " + err);
  };

  navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);
} else {
  console.log("MediaDevices.getUserMedia() not supported on your browser!");
}

submitBtn.onclick = async function () {

  currentWordIndex = currentWordIndex + 1;
  if (currentWordIndex >= words.length) {
    document.getElementById('recordingDiv').hidden = true;
    document.getElementById('completionDiv').hidden = false;
  }
  document.getElementById('nextWord').textContent = words[currentWordIndex];
  audioPlayerDiv.hidden = true

  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.wav");

  const response = await fetch("/audio_upload", {
    method: "POST",
    body: formData
  });

  const result = await response.json();
  console.log(result);
}
