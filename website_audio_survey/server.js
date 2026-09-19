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
const cleanSurveyDirectory = path.join(__dirname, "audio_clean");
const dirtySurveyDirectory = path.join(__dirname, "audio_dirty");
const cleanResultsFile = path.join(__dirname, "clean_audio_results.csv");
const dirtyResultsFile = path.join(__dirname, "dirty_audio_results.csv");

app.use(express.json());
app.use(require("cors")());
app.use(express.static(__dirname));

function sanitize(str) {
  return String(str).replace(/[^\w\s.,!?-]/g, "");
}

function sanitizeFilename(value) {
  const filename = String(value).split(/[\\/]/).pop();
  return filename.replace(/[^\w\s.,!?-]/g, "");
}

function csvValue(value) {
  return `"${String(value ?? "").replace(/"/g, '""')}"`;
}

function appendResults(file, userId, results, callback) {
  const headers = [
    "userId",
    "file",
    "source",
    "humanCloseness",
    "heardText",
    "misheardText",
    "misinterpretationLikelihood",
    "originalAudioText",
    "originalAudioRealism",
    "submittedAt"
  ];
  const rows = results.map(result => [
    userId,
    result.file,
    result.source,
    result.humanCloseness,
    result.heardText,
    result.misheardText,
    result.misinterpretationLikelihood,
    result.originalAudioText,
    result.originalAudioRealism,
    new Date().toISOString()
  ].map(csvValue).join(","));
  const content = `${rows.join("\n")}\n`;
  const fileContent = fs.existsSync(file) ? content : `${headers.map(csvValue).join(",")}\n${content}`;

  fs.appendFile(file, fileContent, callback);
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

function readAudioMetadata(config) {
  const sttPromise = config.sttFile
    ? new Promise((resolve, reject) => {
      fs.readFile(config.sttFile, "utf8", (error, csv) => {
        if (error) return reject(error);
        const rows = parseCsv(csv);
        const headers = rows.shift() || [];
        const filenameIndex = headers.indexOf("filename");
        const textIndex = headers.indexOf("stt_text");
        if (filenameIndex === -1 || textIndex === -1) {
          return reject(new Error("STT metadata is missing filename or stt_text columns"));
        }
        const sttByFilename = new Map(rows
          .filter(row => row[filenameIndex])
          .map(row => [path.basename(row[filenameIndex].replace(/\\/g, "/")), row[textIndex] || ""]));
        resolve(sttByFilename);
      });
    })
    : Promise.resolve(new Map());

  return Promise.all([
    new Promise((resolve, reject) => {
      fs.readFile(config.metadataFile, "utf8", (error, csv) => {
      if (error) return reject(error);

      const rows = parseCsv(csv);
      const headers = rows.shift() || [];
      const filenameIndex = headers.indexOf("filename");
      const textIndex = headers.indexOf("text");
      const misheardTextIndex = config.misheardColumn
        ? headers.indexOf(config.misheardColumn)
        : -1;
      if (filenameIndex === -1 || textIndex === -1) {
        return reject(new Error("Audio metadata is missing a filename or text column"));
      }

      resolve({ rows, filenameIndex, textIndex, misheardTextIndex });
      });
    }),
    sttPromise
  ]).then(([metadata, sttByFilename]) => {
      const { rows, filenameIndex, textIndex, misheardTextIndex } = metadata;
      const audio = rows
        .filter(row => row[filenameIndex])
        .map(row => {
          const relativeFilename = row[filenameIndex].replace(/\\/g, "/");
          const filename = path.basename(relativeFilename).replace(/\.opus$/i, ".wav");
          return {
            filename,
            fileDirectory: path.join(config.rootDirectory, config.audioDirectory || path.dirname(relativeFilename)),
            audioPrefix: config.audioPrefix,
            text: row[textIndex] || "",
            misheardText: misheardTextIndex === -1
              ? sttByFilename.get(filename) || ""
              : row[misheardTextIndex] || ""
          };
        })
        .filter(entry => fs.existsSync(path.join(entry.fileDirectory, entry.filename)))
        .map(entry => ({
          file: `${entry.audioPrefix}/${path.relative(config.rootDirectory, entry.fileDirectory).replace(/\\/g, "/")}/${entry.filename}`,
          text: entry.text,
          misheardText: entry.misheardText
        }));

      return audio;
    });
}

function getAudioMetadata(configs, res, errorMessage) {
  Promise.all(configs.map(readAudioMetadata))
    .then(audio => res.json(audio.flat()))
    .catch(error => {
      console.error(error);
      res.status(500).json({ error: errorMessage });
    });
}

app.get("/clean_audio_metadata", (req, res) => {
  getAudioMetadata([
    {
      metadataFile: path.join(__dirname, "audio_clean", "survey_metadata_human.csv"),
      rootDirectory: path.join(__dirname, "audio_clean"),
      audioPrefix: "audio_clean",
      audioDirectory: "audios",
      sttFile: path.join(__dirname, "audio_clean", "stt_results.csv"),
      misheardColumn: null
    },
    {
      metadataFile: path.join(__dirname, "audio_clean", "survey_data_clean.csv"),
      rootDirectory: cleanSurveyDirectory,
      audioPrefix: "audio_clean",
      misheardColumn: "clean_text"
    },
    {
      metadataFile: path.join(__dirname, "audio_clean", "survey_data_clean_ncvoter.csv"),
      rootDirectory: cleanSurveyDirectory,
      audioPrefix: "audio_clean",
      misheardColumn: "clean_text"
    }
  ], res, "Clean audio metadata could not be loaded");
});

app.get("/dirty_audio_metadata", (req, res) => {
  getAudioMetadata([
    {
      metadataFile: dirtyMetadataFile,
      rootDirectory: path.join(__dirname, "audio_dirty"),
      audioPrefix: "audio_dirty",
      audioDirectory: "audios",
      sttFile: path.join(__dirname, "audio_dirty", "stt_results.csv"),
      misheardColumn: null
    },
    {
      metadataFile: path.join(__dirname, "audio_dirty", "survey_data_noisy.csv"),
      rootDirectory: dirtySurveyDirectory,
      audioPrefix: "audio_dirty",
      misheardColumn: "noisy_text"
    },
    {
      metadataFile: path.join(__dirname, "audio_dirty", "survey_data_noisy_ncvoter.csv"),
      rootDirectory: dirtySurveyDirectory,
      audioPrefix: "audio_dirty",
      misheardColumn: "noisy_text"
    }
  ], res, "Dirty audio metadata could not be loaded");
});

app.post("/survey_upload", (req, res) => {
  if (!Array.isArray(req.body.data)) {
    return res.status(400).json({ error: "Survey data must be an array" });
  }
  const userId = String(req.body.userId || "").trim();
  if (!userId) return res.status(400).json({ error: "User ID is required" });

  const cleanData = req.body.data.map(entry => ({
    tab: sanitize(entry.tab),
    file: sanitizeFilename(entry.file),
    source: sanitize(entry.source),
    humanCloseness: Number(entry.humanCloseness),
    heardText: sanitize(entry.heardText),
    misheardText: sanitize(entry.misheardText),
    misinterpretationLikelihood: Number(entry.misinterpretationLikelihood),
    originalAudioText: sanitize(entry.originalAudioText),
    originalAudioRealism: Number(entry.originalAudioRealism)
  }));

  const tab = cleanData[0]?.tab;
  const resultsFile = tab === "Clean Audio"
    ? cleanResultsFile
    : tab === "Dirty Audio"
      ? dirtyResultsFile
      : null;
  if (!resultsFile || cleanData.some(entry => entry.tab !== tab)) {
    return res.status(400).json({ error: "Invalid or mixed audio tab results" });
  }

  appendResults(resultsFile, userId, cleanData, error => {
    if (error) {
      console.error(error);
      return res.status(500).json({ error: "Survey results could not be saved" });
    }
    res.json({ status: "ok" });
  });
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
