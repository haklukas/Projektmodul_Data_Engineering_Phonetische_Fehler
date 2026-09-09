const stopButton = document.getElementById('stopButton');
const submitBtn = document.getElementById('submitBtn');
const datasetTables = document.getElementById('datasetTables');
const rowStatus = document.getElementById('rowStatus');
const recordingStatus = document.getElementById('recordingStatus');

const datasets = [
  { key: 'ncvoters', label: 'North Carolina Persons', url: 'parsed_ncvoter_subset.csv' },
  { key: 'books', label: 'Books', url: 'oclc_library_100.csv' }
];
const uploadUrl = window.location.port === '5000'
  ? '/audio_upload'
  : 'http://localhost:5000/audio_upload';
let datasetRows = [];
let currentRowIndex = Number.parseInt(localStorage.getItem('currentRowIndex') || '0', 10);
let currentRowRecordings = {};
let currentRowMetadata = {};
let mediaStream;
let mediaRecorder;
let chunks = [];

function parseCsv(text) {
  const records = [];
  let record = [];
  let value = '';
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    const nextCharacter = text[index + 1];
    if (character === '"' && quoted && nextCharacter === '"') {
      value += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === ',' && !quoted) {
      record.push(value.trim());
      value = '';
    } else if ((character === '\n' || character === '\r') && !quoted) {
      if (character === '\r' && nextCharacter === '\n') index += 1;
      record.push(value.trim());
      if (record.some(cell => cell !== '')) records.push(record);
      record = [];
      value = '';
    } else {
      value += character;
    }
}

  if (value || record.length) {
    record.push(value.trim());
    if (record.some(cell => cell !== '')) records.push(record);
  }

  const headers = records.shift().map(header => header.toLowerCase());
  return {
    headers,
    rows: records.map(record => Object.fromEntries(
      headers.map((header, index) => [header, record[index] || ''])
    )).filter(row => headers.every(header => row[header]))
  };
}

function renderRow() {
  if (currentRowIndex >= datasetRows[0].rows.length) {
    document.getElementById('recordingDiv').hidden = true;
    document.getElementById('completionDiv').hidden = false;
    return;
  }

  currentRowRecordings = {};
  currentRowMetadata = {};
  const recordingKeys = [];
  rowStatus.textContent = `Row ${currentRowIndex + 1} of ${datasetRows[0].rows.length}`;
  datasetTables.innerHTML = datasetRows.map(dataset => {
    const row = dataset.rows[currentRowIndex];
    return `<section class="datasetSection">
      <h3>${dataset.label}</h3>
      <div class="tableScroll" role="region" aria-label="${dataset.label} fields" tabindex="0">
        <table class="fieldTable">
          <thead><tr>${dataset.headers.map(field => `<th scope="col">${field}</th>`).join('')}</tr></thead>
          <tbody><tr>${dataset.headers.map(field => {
      const value = row[field];
      const recordingKey = `${dataset.key}_${field}`;
      recordingKeys.push(recordingKey);
      currentRowMetadata[recordingKey] = { columnName: field, text: value };
      return `
        <td>
          <p class="fieldText">${value}</p>
          <label class="backgroundNoiseLabel" for="backgroundNoise-${recordingKey}">Background Noise:</label>
          <input id="backgroundNoise-${recordingKey}" class="backgroundNoiseInput" type="text" placeholder="None">
          <button class="recordFieldButton" data-recording-key="${recordingKey}" data-field="${field}" data-row-label="${dataset.label}">Record</button>
          <audio class="fieldAudio" data-recording-key="${recordingKey}" controls hidden></audio>
          <span class="fieldStatus" data-recording-key="${recordingKey}"></span>
        </td>`;
          }).join('')}</tr></tbody>
        </table>
      </div>
    </section>`;
  }).join('');
  datasetTables.dataset.recordingKeys = JSON.stringify(recordingKeys);

  document.querySelectorAll('.recordFieldButton').forEach(button => {
    button.addEventListener('click', () => recordField(
      button.dataset.recordingKey,
      `${button.dataset.rowLabel} ${button.dataset.field}`
    ));
  });
  submitBtn.disabled = true;
}

function setRecordingButtonsDisabled(disabled) {
  document.querySelectorAll('.recordFieldButton').forEach(button => {
    button.disabled = disabled;
  });
}

function recordField(recordingKey, fieldLabel) {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') return;

  chunks = [];
  mediaRecorder = new MediaRecorder(mediaStream);
  mediaRecorder.ondataavailable = event => chunks.push(event.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: mediaRecorder.mimeType || 'audio/webm' });
    currentRowRecordings[recordingKey] = blob;
    const audio = document.querySelector(`.fieldAudio[data-recording-key="${recordingKey}"]`);
    audio.src = URL.createObjectURL(blob);
    audio.hidden = false;
    document.querySelector(`.fieldStatus[data-recording-key="${recordingKey}"]`).textContent = 'Ready';
    recordingStatus.textContent = '';
    stopButton.disabled = true;
    setRecordingButtonsDisabled(false);
    const recordingKeys = JSON.parse(datasetTables.dataset.recordingKeys);
    submitBtn.disabled = !recordingKeys.every(key => currentRowRecordings[key]);
  };
  mediaRecorder.start();
  stopButton.disabled = false;
  setRecordingButtonsDisabled(true);
  document.querySelector(`.fieldStatus[data-recording-key="${recordingKey}"]`).textContent = 'Recording...';
  recordingStatus.textContent = `Recording ${fieldLabel}`;
}

stopButton.onclick = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
};

submitBtn.onclick = async () => {
  submitBtn.disabled = true;
  const recordingKeys = JSON.parse(datasetTables.dataset.recordingKeys);
  const formData = new FormData();
  const metadata = recordingKeys.map(recordingKey => ({
    userId: localStorage.getItem('userId') || 'anonymous',
    columnName: currentRowMetadata[recordingKey].columnName,
    text: currentRowMetadata[recordingKey].text,
    backgroundNoise: document.querySelector(
      `.backgroundNoiseInput[id="backgroundNoise-${recordingKey}"]`
    ).value.trim(),
    recordingKey
  }));
  recordingKeys.forEach(recordingKey => {
    formData.append(recordingKey, currentRowRecordings[recordingKey], `${recordingKey}.opus`);
  });
  formData.append('rowIndex', String(currentRowIndex));
  formData.append('rows', JSON.stringify(datasetRows.map(dataset => ({
    label: dataset.label,
    row: dataset.rows[currentRowIndex]
  }))));
  formData.append('recordingKeys', JSON.stringify(recordingKeys));
  formData.append('user', localStorage.getItem('userId') || 'anonymous');
  formData.append('metadata', JSON.stringify(metadata));

  try {
    const response = await fetch(uploadUrl, { method: 'POST', body: formData });
    const responseText = await response.text();
    let responseData = {};
    if (responseText) {
      try {
        responseData = JSON.parse(responseText);
      } catch {
        responseData = { error: responseText.replace(/<[^>]*>/g, '').trim() };
      }
    }
    if (!response.ok) throw new Error(responseData.error || `Upload failed (${response.status})`);
    currentRowIndex += 1;
    localStorage.setItem('currentRowIndex', String(currentRowIndex));
    renderRow();
  } catch (error) {
    submitBtn.disabled = false;
    recordingStatus.textContent = `Upload failed: ${error.message}`;
  }
};

document.getElementById('resetBtn').onclick = () => {
  localStorage.removeItem('currentRowIndex');
  window.location.reload();
};

async function initialise() {
  try {
    datasetRows = await Promise.all(datasets.map(async dataset => {
      const response = await fetch(dataset.url);
      if (!response.ok) throw new Error(`${dataset.label} CSV could not be loaded`);
      return { ...dataset, ...parseCsv(await response.text()) };
    }));
    const rowCount = Math.min(...datasetRows.map(dataset => dataset.rows.length));
    datasetRows = datasetRows.map(dataset => ({ ...dataset, rows: dataset.rows.slice(0, rowCount) }));
    currentRowIndex = Math.min(Math.max(currentRowIndex, 0), rowCount);
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('Audio recording is not supported by this browser');
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    renderRow();
  } catch (error) {
    rowStatus.textContent = error.message;
  }
}

initialise();
