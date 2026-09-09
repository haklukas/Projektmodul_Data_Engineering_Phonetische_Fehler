const express = require("express");
const app = express();
const multer = require("multer");
const upload = multer({ dest: "audio_upload/" });
const fs = require("fs");
const path = require("path");
const namesFile = path.join(__dirname, "participant_names.jsonl");
const metadataFile = path.join(__dirname, "audio_metadata.csv");
const audioDirectory = path.join(__dirname, "audio_upload");
let audioSaveQueue = Promise.resolve();

app.use(express.json());
app.use(require("cors")());
app.use(express.static(__dirname));
fs.mkdirSync(audioDirectory, { recursive: true });

function sanitize(str) {
  return String(str).replace(/[^\w\s.,!?-]/g, "");
}

app.post("/user_name", (req, res) => {
  const name = String(req.body.name || "").trim();
  const userId = String(req.body.userId || "").trim();

  if (!name) return res.status(400).json({ error: "Name is required" });
  if (!userId) return res.status(400).json({ error: "User ID is required" });

  const entry = JSON.stringify({
    userId,
    name,
    submittedAt: new Date().toISOString()
  });

  fs.appendFile(namesFile, `${entry}\n`, error => {
    if (error) {
      console.error(error);
      return res.status(500).json({ error: "Name could not be saved" });
    }
    res.json({ status: "ok" });
  });
});

/*app.post("/audio_upload", upload.single("audio"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  } else {
    console.log(`Received file: ${req.file.originalname}, (${req.file.mimetype}, ${req.file.size} bytes)`);
    res.json({ status: "ok" });
  }
}); */

app.post("/audio_upload", upload.any(), (req, res) => {
  let recordingKeys;
  let metadata;
  try {
    recordingKeys = JSON.parse(req.body.recordingKeys || "[]");
    metadata = JSON.parse(req.body.metadata || "[]");
  } catch {
    return res.status(400).json({ error: "Invalid recording metadata" });
  }

  if (!Array.isArray(recordingKeys) || !Array.isArray(metadata) || metadata.length !== recordingKeys.length) {
    return res.status(400).json({ error: "Invalid recording metadata" });
  }

  const uploadedFiles = new Map((req.files || []).map(file => [file.fieldname, file]));
  const missingField = recordingKeys.find(key => !uploadedFiles.has(key));
  if (missingField) return res.status(400).json({ error: `Missing recording: ${missingField}` });

  const userId = String(req.body.user || "anonymous").trim();
  const safeUser = userId.replace(/[^a-z0-9_-]/gi, "_");
  const safeRowIndex = String(req.body.rowIndex || "0").replace(/[^0-9_-]/g, "_");

  const saveOperation = audioSaveQueue.then(async () => {
    const existingFiles = await fs.promises.readdir(audioDirectory);
    const filenamePattern = new RegExp(`^${escapeRegExp(safeUser)}_(\\d+)\\.opus$`);
    let nextSampleNumber = existingFiles.reduce((highest, filename) => {
      const match = filename.match(filenamePattern);
      return match ? Math.max(highest, Number(match[1])) : highest;
    }, 0) + 1;

    const files = recordingKeys.map((recordingKey, index) => {
      const filename = `${safeUser}_${nextSampleNumber + index}.opus`;
      return {
        source: uploadedFiles.get(recordingKey).path,
        filename,
        metadata: metadata[index]
      };
    });

    await Promise.all(files.map(file => fs.promises.rename(
      file.source,
      path.join(audioDirectory, file.filename)
    )));

    const csvRows = files.map(file => [
      userId,
      file.metadata.columnName,
      file.metadata.text,
      file.metadata.backgroundNoise || "None",
      file.filename
    ].map(csvEscape).join(",")).join("\n");
    await appendMetadata(csvRows);
    console.log(`Saved row ${safeRowIndex} for ${userId}`);
    res.json({ status: "ok" });
  });
  audioSaveQueue = saveOperation.catch(() => {});
  saveOperation.catch(error => {
    console.error(error);
    res.status(500).json({ error: "File rename failed" });
  });
});

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

async function appendMetadata(rows) {
  try {
    await fs.promises.access(metadataFile);
  } catch {
    await fs.promises.writeFile(metadataFile, "user_id,column_name,text,background_noise,filename\n");
  }
  await fs.promises.appendFile(metadataFile, `${rows}\n`);
}

app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    return res.status(400).json({ error: `Upload error: ${error.message}` });
  }
  if (error) {
    console.error(error);
    return res.status(500).json({ error: "Audio upload failed" });
  }
  return next();
});

app.listen(5000, () => console.log("Server running on port 5000"));
