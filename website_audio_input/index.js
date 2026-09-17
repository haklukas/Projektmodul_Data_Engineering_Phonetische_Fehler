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
const participantDetails = [
  participantName,
  document.getElementById("nativeLanguage"),
  document.getElementById("countryOfOrigin"),
  document.getElementById("participantAge"),
  document.getElementById("englishKnowledge")
];
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
  nameSubmit.disabled = participantDetails.some(input => !input.checkValidity() || input.value.trim() === "");
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

function restoreParticipantProfile() {
  try {
    const profile = JSON.parse(localStorage.getItem("participantProfile") || "null");
    if (!profile) return;

    participantName.value = profile.name || "";
    document.getElementById("nativeLanguage").value = profile.nativeLanguage || "";
    document.getElementById("countryOfOrigin").value = profile.countryOfOrigin || "";
    document.getElementById("participantAge").value = profile.age || "";
    document.getElementById("englishKnowledge").value = profile.englishKnowledge || "";
  } catch (error) {
    console.warn("Saved participant data could not be restored.", error);
  }
}

participantDetails.forEach(input => input.addEventListener("input", updateNameSubmitState));
participantDetails.forEach(input => input.addEventListener("change", updateNameSubmitState));
navigationLinks.forEach(link => {
  link.addEventListener("click", event => {
    if (link.dataset.navigationEnabled !== "true") event.preventDefault();
  });
});
restoreParticipantProfile();
updateNameSubmitState();
setNavigationEnabled(
  localStorage.getItem(`nameSavedForUser:${userId}`) === "true" &&
  participantDetails.every(input => input.checkValidity() && input.value.trim() !== "")
);

nameForm.addEventListener("submit", async event => {
  event.preventDefault();
  nameSubmit.disabled = true;
  nameStatus.textContent = "Saving...";

  try {
    const response = await fetch(nameUploadUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        userId,
        name: participantName.value.trim(),
        nativeLanguage: document.getElementById("nativeLanguage").value.trim(),
        countryOfOrigin: document.getElementById("countryOfOrigin").value.trim(),
        age: document.getElementById("participantAge").value,
        englishKnowledge: document.getElementById("englishKnowledge").value
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not save your data");
    nameStatus.className = "saveSuccess";
    nameStatus.textContent = "Your data was saved successfully.";
    setNavigationEnabled(true);
    try {
      localStorage.setItem(`nameSavedForUser:${userId}`, "true");
      localStorage.setItem("participantProfile", JSON.stringify({
        name: participantName.value.trim(),
        nativeLanguage: document.getElementById("nativeLanguage").value.trim(),
        countryOfOrigin: document.getElementById("countryOfOrigin").value.trim(),
        age: document.getElementById("participantAge").value,
        englishKnowledge: document.getElementById("englishKnowledge").value
      }));
    } catch (storageError) {
      console.warn("Participant data was saved, but browser storage is unavailable.", storageError);
    }
  } catch (error) {
    nameStatus.className = "saveError";
    nameStatus.textContent = `Could not save data: ${error.message}`;
    updateNameSubmitState();
  }
});
}
