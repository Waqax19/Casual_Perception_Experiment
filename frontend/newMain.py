import pygame
import pyodide
import js
import experiment


def run_experiment():
    # Get canvas from HTML
    canvas = js.document.getElementById("pygame-canvas")
    pygame.display.set_mode((800, 600), canvas=canvas)

    # Get demographics from JavaScript
    participant_id = pyodide.globals.get("participant_id")
    name = pyodide.globals.get("participant_name")
    age = pyodide.globals.get("participant_age")
    gender = pyodide.globals.get("participant_gender")

    # Initialize experiment
    trial_num = 0
    total_trials = 480
    trials_per_break = 50

    while trial_num < total_trials:
        # Run a trial
        trial_data = experiment.run_trial(trial_num, participant_id, name, age, gender)

        # Log trial data to console (temporary, will send to Flask later)
        js.console.log(trial_data)

        # Update progress bar
        js.document.getElementById("progress").textContent = f"Trial {trial_num + 1}/{total_trials}"

        # Add break every 50 trials
        if (trial_num + 1) % trials_per_break == 0 and trial_num + 1 < total_trials:
            font = pygame.font.Font(None, 36)
            text = font.render("Take a break, press any key to continue", True, (255, 255, 255))
            canvas.blit(text, (100, 300))
            pygame.display.flip()
            # Wait for keypress (handled via JavaScript, see below)
            pyodide.runPython('import js; js.wait_for_keypress()')

        trial_num += 1

    # Show confirmation
    js.document.getElementById("experiment").style.display = "none"
    js.document.getElementById("confirmation").style.display = "block"