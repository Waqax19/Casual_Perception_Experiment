let participantData = {};
let results = [];

// Handle form submission
document.getElementById("participant-form").addEventListener("submit", function (e) {
  e.preventDefault();
  participantData.name = document.getElementById("name").value;
  participantData.age = document.getElementById("age").value;
  participantData.gender = document.getElementById("gender").value;

  document.getElementById("form-section").style.display = "none";
  document.getElementById("experiment-section").style.display = "block";
  document.getElementById("welcome").innerText = `Welcome, ${participantData.name}!`;

  startExperiment();
});

// Simulated experiment logic
function startExperiment() {
  let totalTrials = 5; // demo
  let currentTrial = 0;

  function runTrial() {
    if (currentTrial < totalTrials) {
      showCountdown(() => {
        document.getElementById("trial-status").innerText = `Trial ${currentTrial + 1} of ${totalTrials}`;
        results.push({
          trial: currentTrial + 1,
          target1: "X",
          target2: "Y",
          response1: "O",
          response2: "P"
        });
        currentTrial++;
        setTimeout(runTrial, 1000); // simulate 1s per trial
      });
    } else {
      endExperiment();
    }
  }
  runTrial();
}

function showCountdown(callback) {
  const overlay = document.createElement("div");
  overlay.className = "countdown-overlay";
  document.body.appendChild(overlay);

  let count = 3;
  const text = document.createElement("div");
  text.className = "countdown-text";
  overlay.appendChild(text);

  function nextCount() {
    if (count > 0) {
      text.innerText = count;
      count--;
      setTimeout(nextCount, 1000);
    } else {
      text.innerText = "GO!";
      setTimeout(() => {
        document.body.removeChild(overlay);
        callback();
      }, 800);
    }
  }
  nextCount();
}

function endExperiment() {
  document.getElementById("experiment-section").style.display = "none";
  document.getElementById("download-section").style.display = "block";
}

// Download CSV
document.getElementById("download-btn").addEventListener("click", function () {
  downloadCSV();
  document.getElementById("download-section").innerHTML = "<h3>Thank you for participating! Your data has been saved.</h3>";
});

function downloadCSV() {
  let csv = "Trial,Target1,Target2,Response1,Response2\n";
  results.forEach(r => {
    csv += `${r.trial},${r.target1},${r.target2},${r.response1},${r.response2}\n`;
  });
  let blob = new Blob([csv], { type: 'text/csv' });
  let link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${participantData.name}_results.csv`;
  link.click();
}
