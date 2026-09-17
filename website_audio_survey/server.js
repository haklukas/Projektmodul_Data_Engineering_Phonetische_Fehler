const express = require("express");
const app = express();
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const participantFile = path.join(__dirname, "participant_data.jsonl");
const cleanMetadataFile = path.join(__dirname, "audio_clean", "audio_metadata.csv");
const cleanAudioDirectory = path.join(__dirname, "audio_clean", "audios");
const dirtyMetadataFile = path.join(__dirname, "audio_dirty", "audio_metadata.csv");
const dirtyAudioDirectory = path.join(__dirname, "audio_dirty", "audios");

app.use(express.json());
app.use(require("cors")());
app.use(express.static(__dirname));

function sanitize(str) {
  return String(str).replace(/[^\w\s.,!?-]/g, "");
}

function parseCsv(csv) {
  const rows = [];
  let row = [];
  let value = "";
  let quoted = false;

  for (let position = 0; position < csv.length; position++) {
    const character = csv[position];
    const nextCharacter = csv[position + 1];

    if (character === '"' && quoted && nextCharacter === '"') {
      value += '"';
      position++;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === "," && !quoted) {
      row.push(value);
      value = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && nextCharacter === "\n") position++;
      row.push(value);
      rows.push(row);
      row = [];
      value = "";
    } else {
      value += character;
    }
  }

  if (value || row.length) {
    row.push(value);
    rows.push(row);
  }

  return rows;
}

function getAudioMetadata(metadataFile, audioDirectory, audioPrefix, res) {
  fs.readFile(metadataFile, "utf8", (error, csv) => {
    if (error) return res.status(500).json({ error: "Clean audio metadata could not be loaded" });

    const rows = parseCsv(csv);
    const headers = rows.shift() || [];
    const filenameIndex = headers.indexOf("filename");
    const textIndex = headers.indexOf("text");
    if (filenameIndex === -1 || textIndex === -1) {
      return res.status(500).json({ error: "Clean audio metadata is missing filename or text columns" });
    }

    const audio = rows
      .filter(row => row[filenameIndex])
      .map(row => {
        const filename = row[filenameIndex].replace(/\.opus$/i, ".wav");
        return {
          filename,
          text: row[textIndex] || ""
        };
      })
      .filter(entry => fs.existsSync(path.join(audioDirectory, entry.filename)))
      .map(entry => ({
        file: `${audioPrefix}/audios/${entry.filename}`,
        text: entry.text
      }));

    res.json(audio);
  });
}

app.get("/clean_audio_metadata", (req, res) => {
  getAudioMetadata(cleanMetadataFile, cleanAudioDirectory, "audio_clean", res);
});

app.get("/dirty_audio_metadata", (req, res) => {
  getAudioMetadata(dirtyMetadataFile, dirtyAudioDirectory, "audio_dirty", res);
});

app.post("/survey_upload", (req, res) => {
  if (!Array.isArray(req.body.data)) {
    return res.status(400).json({ error: "Survey data must be an array" });
  }

  const cleanData = req.body.data.map(entry => ({
    tab: sanitize(entry.tab),
    file: sanitize(entry.file),
    source: sanitize(entry.source),
    humanCloseness: Number(entry.humanCloseness),
    heardText: sanitize(entry.heardText),
    misheardText: sanitize(entry.misheardText),
    misinterpretationLikelihood: Number(entry.misinterpretationLikelihood),
    originalAudioText: sanitize(entry.originalAudioText),
    originalAudioRealism: Number(entry.originalAudioRealism)
  }));

  console.log(cleanData);
  res.json({ status: "ok" });
});

app.post("/user_name", (req, res) => {
  const userId = String(req.body.userId || "").trim();
  const nativeLanguage = String(req.body.nativeLanguage || "").trim();
  const countryOfOrigin = String(req.body.countryOfOrigin || "").trim();
  const age = String(req.body.age || "").trim();
  const englishKnowledge = String(req.body.englishKnowledge || "").trim();

  if (!userId) return res.status(400).json({ error: "User ID is required" });
  if (!nativeLanguage || !countryOfOrigin || !age || !englishKnowledge) {
    return res.status(400).json({ error: "All participant details are required" });
  }

  const entry = JSON.stringify({
    userId,
    nativeLanguage,
    countryOfOrigin,
    age,
    englishKnowledge,
    submittedAt: new Date().toISOString()
  });

  fs.appendFile(participantFile, `${entry}\n`, error => {
    if (error) {
      console.error(error);
      return res.status(500).json({ error: "Participant data could not be saved" });
    }
    res.json({ status: "ok" });
  });
});

app.listen(5000, () => console.log("Server running on port 5000"));
