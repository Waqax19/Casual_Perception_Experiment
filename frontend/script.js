// Store participant and trial data
let participantData = {};
let trialResults = [];

// Handle form submission
document.getElementById("participant-form").addEventListener("submit", function (e) {
  e.preventDefault(); // Prevent page refresh

  // Collect participant info
  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();
  const gender = document.getElementById("gender").value;

  participantData = { name, age, gender, startTime: new Date().toISOString() };

  // Show experiment section
  document.getElementById("form-section").style.display = "none";
  document.getElementById("experiment-section").style.display = "block";

  document.getElementById("welcome").textContent = `Welcome, ${name}! The experiment will now begin.`;

  // Start dummy experiment (5 trials)
  runExperiment();
});

// Simulate experiment trials (placeholder for now)
function runExperiment() {
  let currentTrial = 0;
  const totalTrials = 5;

  const trialStatus = document.getElementById("trial-status");
  trialStatus.textContent = `Trial 1 of ${totalTrials}`;

  const trialInterval = setInterval(() => {
    currentTrial++;
    trialResults.push({
      trial: currentTrial,
      timestamp: new Date().toISOString(),
      result: `Dummy result ${currentTrial}`
    });

    trialStatus.textContent = `Trial ${currentTrial} of ${totalTrials}`;

    if (currentTrial >= totalTrials) {
      clearInterval(trialInterval);
      endExperiment();
    }
  }, 1000);
}

// End experiment and show download option
function endExperiment() {
  document.getElementById("experiment-section").style.display = "none";
  document.getElementById("download-section").style.display = "block";
}

// Convert data to CSV
function generateCSV() {
  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += `Name,Age,Gender,StartTime\n${participantData.name},${participantData.age},${participantData.gender},${participantData.startTime}\n\n`;
  csvContent += "Trial,Timestamp,Result\n";

  trialResults.forEach(trial => {
    csvContent += `${trial.trial},${trial.timestamp},${trial.result}\n`;
  });

  return encodeURI(csvContent);
}

// Download CSV
document.getElementById("download-btn").addEventListener("click", function () {
  const csv = generateCSV();
  const link = document.createElement("a");
  link.setAttribute("href", csv);
  link.setAttribute("download", `${participantData.name}_results.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
});
