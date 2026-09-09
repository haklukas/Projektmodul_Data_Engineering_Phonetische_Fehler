const express = require("express");
const app = express();
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const namesFile = path.join(__dirname, "participant_names.jsonl");

app.use(express.json());
app.use(require("cors")());
app.use(express.static(__dirname));

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

app.listen(5000, () => console.log("Server running on port 5000"));
