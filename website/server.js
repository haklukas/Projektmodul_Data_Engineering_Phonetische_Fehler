const express = require("express");
const app = express();

app.use(express.json());
app.use(require("cors")());

function sanitize(str) {
  return String(str).replace(/[^\w\s.,!?-]/g, "");
}

app.post("/save", (req, res) => {
  const cleanData = req.body.data.map(entry => ({
    file: sanitize(entry.file),
    input: sanitize(entry.input)
  }));

  console.log(cleanData);
  res.json({ status: "ok" });
});


app.listen(5000, () => console.log("Server running on port 5000"));
