document.getElementById("participant-form").addEventListener("submit", function (e) {
    e.preventDefault();  // Stop page refresh

    // Get form values
    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const gender = document.getElementById("gender").value;

    // Show experiment section
    document.getElementById("participant-name").textContent = name;
    document.getElementById("participant-form").style.display = "none";
    document.getElementById("experiment").style.display = "block";

    console.log(`Participant Data: Name=${name}, Age=${age}, Gender=${gender}`);
});
