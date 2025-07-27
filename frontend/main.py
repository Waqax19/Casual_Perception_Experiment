import pygame
import random
import itertools
import sys
import traceback
import uuid
import textwrap
from Objects import MovingObject
from experiment import Experiment
from Utilities import WIDTH, HEIGHT, BLACK, WHITE, GRAY, POSITIONS

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Causal Perception Experiment")
clock = pygame.time.Clock()

### MODIFIED: GENERATE RANDOM PARTICIPANT ID ###
participant_id = str(uuid.uuid4())

### MODIFIED: DEFINE CONDITIONS FOR TRIALS ###
collision_types = ["overtaking", "fake_causal", "true_causal"]
which_changes = ["o1_twice", "o1_then_o2"]
lags = [100, 300, 500, 700]
conditions = list(itertools.product(collision_types, which_changes, lags))

exp1_conditions = [c for c in conditions if c[0] == "overtaking"]  # 8
exp2_conditions = [c for c in conditions if c[1] == "o1_twice" and c[0] != "overtaking"]  # 8
exp3_conditions = [c for c in conditions if c[1] == "o1_then_o2" and c[0] != "overtaking"]  # 8
all_experiments = [
    ("Exp1", exp1_conditions),
    ("Exp2", exp2_conditions),
    ("Exp3", exp3_conditions)
]

print(
    f"Exp1: {len(exp1_conditions)} conditions, Exp2: {len(exp2_conditions)} conditions, Exp3: {len(exp3_conditions)} conditions")

### MODIFIED: GENERATE 20 TRAINING TRIALS ###
training_trials = []
for _ in range(20):
    exp_name, exp_conditions = random.choice(all_experiments)
    condition = random.choice(exp_conditions)
    training_trials.append((exp_name, condition))
print(f"Total training trials loaded: {len(training_trials)}")

### MODIFIED: GENERATE 220 MAIN TRIALS ###
main_trials = []
for _ in range(220):
    exp_name, exp_conditions = random.choice(all_experiments)
    condition = random.choice(exp_conditions)
    main_trials.append((exp_name, condition))
print(f"Total main trials loaded: {len(main_trials)}")


### MODIFIED: FUNCTION TO DISPLAY TEXT SCREEN ###
def display_text_screen(text_lines, wait_for_key=True, key_to_wait_for=None, font_size=28):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    max_chars_per_line = (WIDTH - 100) // (font_size // 2)

    wrapped_lines = []
    for line in text_lines:
        if len(line) > max_chars_per_line:
            # Use textwrap to break long lines
            wrapped = textwrap.fill(line, width=max_chars_per_line)
            wrapped_lines.extend(wrapped.split('\n'))
        else:
            wrapped_lines.append(line)

    # Calculate total height needed
    line_height = font_size + 5  # Add some spacing between lines
    total_height = len(wrapped_lines) * line_height

    # Start position - center vertically
    start_y = (HEIGHT - total_height) // 2

    for i, line in enumerate(wrapped_lines):
        text_surface = font.render(line, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = WIDTH // 2  # Center horizontally
        text_rect.y = start_y + (i * line_height)
        screen.blit(text_surface, text_rect)


    '''y_offset = HEIGHT // 2 - len(text_lines) * 20
    for line in text_lines:
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
        y_offset += 40'''
    pygame.display.flip()


    if wait_for_key:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if key_to_wait_for is None or event.key == key_to_wait_for:
                        return


### MODIFIED: FUNCTION TO COLLECT LETTER RESPONSE WITH ENTER KEY SUPPORT FOR YES/NO ###
def collect_letter_response(prompt_text):
    response = ""
    input_active = False
    font = pygame.font.Font(None, 40)
    user_input = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not input_active:
                input_active = True
                pygame.time.delay(500)
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                if key_name == "space":
                    response = "O"
                    break
                elif key_name == "return" and user_input.lower() in ["yes", "no"]:
                    response = user_input.upper()
                    break
                elif key_name == "backspace":
                    user_input = user_input[:-1]
                elif key_name in [chr(i) for i in range(97, 123)]:  # Letters a-z
                    if "Did you see a red dot?" in prompt_text:
                        if len(user_input) < 3:  # Limit input to 'yes' or 'no'
                            user_input += key_name
                    else:
                        response = key_name.upper()
                        break

        screen.fill(BLACK)
        prompt_surface = font.render(prompt_text, True, WHITE)
        screen.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT - 100))
        if input_active:
            response_surface = font.render(user_input, True, WHITE)
            screen.blit(response_surface, (WIDTH // 2 - response_surface.get_width() // 2, HEIGHT - 50))
        pygame.display.flip()
        clock.tick(480)



        if response:
            break

    print(f"Response collected: {response}")
    pygame.time.delay(500)
    return response


### MODIFIED: SHOW INSTRUCTION SCREEN ###
instruction_text = [
    "Hello! Thank you for participating.",
    "",  # Empty line for spacing
    "You will be shown a stream of rapidly changing digits",
    "that move across the screen.",
    "",
    "Twice in that stream, a letter will appear for a very",
    "short amount of time. These are your targets.",
    "",
    "Your task is to identify which letters they were and type them in the order in which you saw them.",
    "",
    "If you are not sure, still give it a try: sometimes you",
    "will have seen them without being aware of it, and",
    "so your guess will be the right answer.",
    "",
    "If you really do not know, press the spacebar.",
    "",
    "Let's start with 20 mock trials, for you to practice."
]

display_text_screen(instruction_text, wait_for_key=True)

### MODIFIED: RUN TRAINING TRIALS ###
for trial_num, (exp_name, condition) in enumerate(training_trials, 1):
    collision_type, which_changes, lag = condition
    print(
        f"\nTraining Trial {trial_num}/{len(training_trials)}: {exp_name}, {collision_type}, {which_changes}, Lag: {lag} ms")

    try:
        o1 = MovingObject(POSITIONS[0][0], POSITIONS[0][1], 40, (255, 0, 0), random.choice('XYZ'))  # Red
        o2 = MovingObject(0, 0, 40, (135, 206, 250), random.choice('XYZ'))  # Light blue
        experiment = Experiment(o1, o2, collision_type, which_changes, lag, participant_id, is_training=True)

        running = True
        response_taken = False
        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks() - start_time
            experiment.update(current_time)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("User quit")
                    pygame.quit()
                    sys.exit()

            if experiment.state == "asking" and not response_taken:
                response_taken = True
                if experiment.attention_prompt:
                    prompt = "ATTENTION CHECK: Did you see a red dot? (yes/no)"
                    response = collect_letter_response(prompt)
                    experiment.submit_response(response, response)
                else:
                    prompt_t1 = "What do you think was the first target?"
                    "(“I don’t know” = space bar)"
                    t1_response = collect_letter_response(prompt_t1)
                    prompt_t2 = "What do you think was the second target?"
                    "(“I don’t know” = space bar)"
                    t2_response = collect_letter_response(prompt_t2)
                    experiment.submit_response(t1_response, t2_response)
                    running = False
                    print(f"Training Trial {trial_num} completed")

            screen.fill(BLACK)
            font = pygame.font.Font(None, 48)
            o1_text = font.render(o1.text, True, o1.color)
            o2_text = font.render(o2.text, True, o2.color)
            screen.blit(o1_text, (int(o1.x - o1_text.get_width() // 2), int(o1.y - o1_text.get_height() // 2)))
            screen.blit(o2_text, (int(o2.x - o2_text.get_width() // 2), int(o2.y - o2_text.get_height() // 2)))

            pygame.display.flip()
            clock.tick(480)

    except Exception as e:
        print(f"Training Trial {trial_num} failed: {e}")
        traceback.print_exc()
        continue

### MODIFIED: SHOW TRAINING COMPLETION SCREEN ###
display_text_screen(["Great job. Now, on to the actual experiment. Good luck!"], wait_for_key=True,
                    key_to_wait_for=pygame.K_SPACE)

### MODIFIED: RUN MAIN TRIALS WITH BREAKS ###
for trial_num, (exp_name, condition) in enumerate(main_trials, 1):
    collision_type, which_changes, lag = condition
    print(f"\nMain Trial {trial_num}/{len(main_trials)}: {exp_name}, {collision_type}, {which_changes}, Lag: {lag} ms")

    try:
        o1 = MovingObject(POSITIONS[0][0], POSITIONS[0][1], 40, (255, 0, 0), random.choice('XYZ'))  # Red
        o2 = MovingObject(0, 0, 40, (135, 206, 250), random.choice('XYZ'))  # Light blue
        experiment = Experiment(o1, o2, collision_type, which_changes, lag, participant_id, is_training=False)

        running = True
        response_taken = False
        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks() - start_time
            experiment.update(current_time)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("User quit")
                    pygame.quit()
                    sys.exit()

            if experiment.state == "asking" and not response_taken:
                response_taken = True
                #if experiment.attention_prompt:
                    #prompt = "ATTENTION CHECK: Did you see a red dot? (yes/no)"
                    #response = collect_letter_response(prompt)
                    #experiment.submit_response(response, response)
                #else:
                prompt_t1 = "What do you think was the first target?"
                "(Press SPACE if you don't know)"
                t1_response = collect_letter_response(prompt_t1)
                prompt_t2 = "What do you think was the second target?"
                "(Press SPACE if you don't know)"
                t2_response = collect_letter_response(prompt_t2)
                experiment.submit_response(t1_response, t2_response)
                running = False
            #print(f"Main Trial {trial_num} completed")

            screen.fill(BLACK)
            font = pygame.font.Font(None, 48)
            o1_text = font.render(o1.text, True, o1.color)
            o2_text = font.render(o2.text, True, o2.color)
            screen.blit(o1_text, (int(o1.x - o1_text.get_width() // 2), int(o1.y - o1_text.get_height() // 2)))
            screen.blit(o2_text, (int(o2.x - o2_text.get_width() // 2), int(o2.y - o2_text.get_height() // 2)))

            pygame.display.flip()
            clock.tick(480)

    except Exception as e:
        print(f"Main Trial {trial_num} failed: {e}")
        traceback.print_exc()
        continue

    ### MODIFIED: SHOW BREAK SCREEN EVERY 50 TRIALS ###
    if trial_num % 50 == 0:
        display_text_screen([
            "You have just completed 50 trials.",
            "Take a small break if you need. When you are ready, resume by pressing any key"
        ], wait_for_key=True)

### MODIFIED: SHOW END SCREEN ###
end_text = [
    "The experiment is over. Thanks a lot for participating!",
    "",
    "Your data will be anonymised and stored in compliance",
    "with the UK General Data Protection Regulation.",
    "",
    "Have a good one!"
]
display_text_screen(end_text, wait_for_key=True)

pygame.quit()
