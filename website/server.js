const express = require("express");
const app = express();
const multer = require("multer");
const upload = multer({ dest: "uploads/" });

app.use(express.json());
app.use(require("cors")());

function sanitize(str) {
  return String(str).replace(/[^\w\s.,!?-]/g, "");
}

app.post("/survey_upload", (req, res) => {
  const cleanData = req.body.data.map(entry => ({
    file: sanitize(entry.file),
    input: sanitize(entry.input)
  }));

  console.log(cleanData);
  res.json({ status: "ok" });
});

app.post("/audio_upload", upload.single("audio"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  } else {
    console.log(`Received file: ${req.file.originalname}`);
    res.json({ status: "ok" });
  }
});

app.listen(5000, () => console.log("Server running on port 5000"));
