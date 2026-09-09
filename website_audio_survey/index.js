function getUserId() {
  let id = localStorage.getItem("userId");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("userId", id);
  }
  return id;
}

const userId = getUserId();
console.log("User ID:", userId);

const nameForm = document.getElementById("nameForm");
if (!nameForm) {
  // The general landing page has unrestricted activity links.
} else {
const participantName = document.getElementById("participantName");
const nameStatus = document.getElementById("nameStatus");
const nameSubmit = document.getElementById("nameSubmit");
const navigationLinks = [
  document.getElementById("activityLink"),
  document.getElementById("audioInputLink"),
  document.getElementById("audioSurveyLink")
].filter(Boolean);
const nameUploadUrl = window.location.port === "5000"
  ? "/user_name"
  : "http://localhost:5000/user_name";

function updateNameSubmitState() {
  nameSubmit.disabled = participantName.value.trim() === "";
}

function setNavigationEnabled(enabled) {
  navigationLinks.forEach(link => {
    link.dataset.navigationEnabled = String(enabled);
    if (enabled) {
      link.removeAttribute("aria-disabled");
    } else {
      link.setAttribute("aria-disabled", "true");
    }
    link.classList.toggle("inactiveLink", !enabled);
  });
}

participantName.addEventListener("input", updateNameSubmitState);
navigationLinks.forEach(link => {
  link.addEventListener("click", event => {
    if (link.dataset.navigationEnabled !== "true") event.preventDefault();
  });
});
updateNameSubmitState();
setNavigationEnabled(localStorage.getItem(`nameSavedForUser:${userId}`) === "true");

nameForm.addEventListener("submit", async event => {
  event.preventDefault();
  nameSubmit.disabled = true;
  nameStatus.textContent = "Saving...";

  try {
    const response = await fetch(nameUploadUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, name: participantName.value.trim() })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not save your name");
    nameStatus.className = "saveSuccess";
    nameStatus.textContent = "Your name was saved successfully.";
    localStorage.setItem(`nameSavedForUser:${userId}`, "true");
    setNavigationEnabled(true);
  } catch (error) {
    nameStatus.className = "saveError";
    nameStatus.textContent = `Could not save name: ${error.message}`;
    updateNameSubmitState();
  }
});
}
