import random
import csv
import time
import textwrap
from Utilities import POSITIONS, random_letter, random_digit


class Experiment:
    def __init__(self, o1, o2, collision_type, which_changes, lag,
                 participant_id, is_training=False):
        self.o1 = o1
        self.o2 = o2
        self.o1.original_text = random_digit()
        self.o2.original_text = random_digit()
        self.o1.text = self.o1.original_text
        self.o2.text = self.o2.original_text
        self.collision_type = collision_type
        self.which_changes = which_changes
        self.lag = lag
        self.change_duration = 94
        self.collision_time = None
        self.fake_causal_duration = 350
        self.fake_causal_pause_ended = False
        self.state = "running"
        self.t1_value = None
        self.t2_value = None
        self.score = 0
        #self.attention_prompt = random.random() < 0.1
        self.attention_prompt = False
        self.response = ""
        self.t1_object = "O1" if which_changes == "o1_twice" else "O1"
        self.t2_object = "O1" if which_changes == "o1_twice" else "O2"
        self.T1_response = ""
        self.T2_response = ""
        self.participant_id = participant_id
        self.is_training = is_training

        try:
            # --- MODIFICATIONS START HERE ---

            # Set O1 to start at a specific point (e.g., the first position in POSITIONS)
            # You can change '0' to any valid index in POSITIONS to specify the starting point.
            specific_o1_start_index = 0
            self.o1.x, self.o1.y = POSITIONS[specific_o1_start_index]
            self.o1.position_index = specific_o1_start_index
            print(textwrap.fill(
                f"O1 initial position set to: ({self.o1.x:.2f}, {self.o1.y:.2f}) "
                f"at index {specific_o1_start_index}", width=80))
            '''print(f"O1 initial position set to: ({self.o1.x:.2f}, {self.o1.y:.2f}) "
                  f"at index {specific_o1_start_index}")'''

            # Ensure O2 stays static
            self.o2.is_moving = False
            print("O2 is set to be static.")

            # Slow down stream by 20% (increase move_interval by 20%)
            self.o1.move_interval *= 1.2
            # O2's move_interval is still set, but it won't move because is_moving is False
            self.o2.move_interval = self.o1.move_interval

            # Ensure O2 is placed to avoid collision before 1 rotation (1000 ms)
            min_collision_time_initial_placement = 1000  # 1 rotation for O1 to move
            positions_per_rotation = 128
            # After 1 rotation for O1
            min_position_index_for_o1_move = int(min_collision_time_initial_placement / self.o1.move_interval)

            valid_indices = []

            for i in range(len(POSITIONS)):
                # Calculate O1's future position after 1 rotation
                o1_future_index = ((self.o1.position_index + min_position_index_for_o1_move)
                                   % len(POSITIONS))
                o1_future_x, o1_future_y = POSITIONS[o1_future_index]

                # Check distance between O1's future position and current O2 candidate position
                dx = o1_future_x - POSITIONS[i][0]
                dy = o1_future_y - POSITIONS[i][1]
                distance = (dx ** 2 + dy ** 2) ** 0.5

                # Ensure distance is large enough to avoid collision before 1 rotation
                threshold = 50 if collision_type == "overtaking" else 20
                if distance > threshold:
                    valid_indices.append(i)

                self.o2.position_index = random.randint(0, len(POSITIONS) - 1)
                self.o2.x, self.o2.y = POSITIONS[self.o2.position_index]
                #print(f"O2 randomly placed at index {self.o2.position_index}")
            '''if not valid_indices:
                raise ValueError("No valid O2 position ensures collision "
                                 "after 1 rotation")'''

            # This part now ensures O2 is placed such that O1 will eventually collide with it,
            # even though O2 is static.
            # We'll select a random collision index, but then calculate O2's *initial* position
            # based on where O1 will be at the *planned collision time*.
            # This 'collision_index' is actually the index where the collision *will occur*.
            collision_position_on_track = random.choice(valid_indices)


            # Set t1_time, t2_time, and collision timing
            min_stream_duration = 1500  # 1.5 rotations
            max_stream_duration = 3500  # 3.5 rotations
            max_post_collision_duration = 1000  # 1 rotation after collision
            frame_duration = 31.25  # ms per frame

            # --- MODIFICATION FOR T1 BEFORE, T2 AFTER COLLISION ---
            # This logic will now apply to all lags, ensuring collision is between T1 and T2
            min_t1_time_for_stream = min_collision_time_initial_placement # Ensure T1 doesn't happen too early
            max_t1_time_for_stream = (max_stream_duration - self.lag -
                                      self.change_duration - max_post_collision_duration)

            if max_t1_time_for_stream < min_t1_time_for_stream:
                raise ValueError("Stream duration constraints too tight "
                                 "for given lag and T1/T2 placement")

            t1_index_frame = random.randint(0, int((max_t1_time_for_stream - min_t1_time_for_stream)
                                             / frame_duration))
            self.t1_time = min_t1_time_for_stream + t1_index_frame * frame_duration
            if self.lag in [500, 700]:
                self.t2_time = self.t1_time + self.lag
            else:
                self.t2_time = None  # Disable T2

            self.t2_time = self.t1_time + self.lag

            # The collision must occur *between* the end of T1 and the start of T2.
            # Define the window for collision: after T1 ends, before T2 starts.
            min_actual_collision_time = self.t1_time + self.change_duration
            max_actual_collision_time = self.t2_time - self.change_duration # Ensure collision ends before T2 starts
            min_window = 20
            if max_actual_collision_time - min_actual_collision_time < min_window:
                print(f"Warning : Collision window is invalid {max_actual_collision_time - min_actual_collision_time:.1f} ms")
            #if min_actual_collision_time >= max_actual_collision_time:
                 #raise ValueError("Collision window is invalid (min_collision >= max_collision)")

            # Randomly select a collision time within this window
            # Convert times to frame counts for more accurate placement

            min_frames_to_collision = int(min_actual_collision_time / self.o1.move_interval)
            max_frames_to_collision = int(max_actual_collision_time / self.o1.move_interval)

            # Calculate O1's position at the desired collision time.
            # This will be O2's static initial position.
            if min_frames_to_collision >= max_frames_to_collision:
                print(f"WARNING : Adjusting collision window : min={min_frames_to_collision} , max = {max_frames_to_collision}")
                max_frames_to_collision = min_frames_to_collision + 5

            o1_frames_to_collision = random.randint(min_frames_to_collision, max_frames_to_collision)
            o1_position_at_collision_index = ((self.o1.position_index + o1_frames_to_collision) % len(POSITIONS))

            self.o2.x, self.o2.y = POSITIONS[o1_position_at_collision_index]
            self.o2.position_index = o1_position_at_collision_index

            # The self.collision_time will be set in the update loop when O1 actually reaches O2's position.
            # We don't pre-set self.collision_time here as it's dynamic.
            print(f"O2 initial position set to: ({self.o2.x:.2f}, {self.o2.y:.2f}) "
                  f"at index {self.o2.position_index} to ensure collision with O1.")


            print(f"T1 time: {self.t1_time:.1f} ms, T2 time: {self.t2_time:.1f} ms, "
                  f"Collision expected between {min_actual_collision_time:.1f}ms and {max_actual_collision_time:.1f}ms")

        except Exception as e:
            print(f"Init error: {e}")
            raise

    def update(self, current_time):
        try:
            if not self.o1.stopped:
                self.o1.move(current_time)

            # O2 is static by default. It only moves if collision_type is "true_causal"
            # and collision has occurred, or if "fake_causal" and pause ended.
            if self.o2.is_moving and not self.o2.stopped:
                if current_time >= self.o2.last_move_time + self.o2.move_interval:
                    self.o2.move(current_time)

            distance = self.o1.distance_to(self.o2)

            # Handle T1 change (O1)
            if (self.t1_time <= current_time <
                    self.t1_time + self.change_duration):
                if not self.t1_value:
                    self.t1_value = random_letter()
                    self.o1.change(self.t1_value)
            elif (current_time >= self.t1_time + self.change_duration and
                  self.o1.is_target): # Reset O1 after T1 change
                self.o1.reset()
                self.o1.text = self.o1.original_text

            # Handle T2 change (O1 or O2 depending on which_changes)
            if self.t2_time and (self.t2_time <= current_time <
                    self.t2_time + self.change_duration):
                if not self.t2_value:
                    self.t2_value = random_letter()
                    if self.which_changes == "o1_then_o2":
                        self.o2.change(self.t2_value) # O2 changes its character
                    else: # o1_twice
                        self.o1.change(self.t2_value) # O1 changes again
            elif self.t2_time and (current_time >= self.t2_time + self.change_duration):
                if self.which_changes == "o1_then_o2" and self.o2.is_target:
                    self.o2.reset()
                    self.o2.text = self.o2.original_text
                elif self.which_changes == "o1_twice" and self.o1.is_target:
                    self.o1.reset()
                    self.o1.text = self.o1.original_text


            # Handle collisions
            if self.collision_time is None:  # Only detect if not already detected
                collision_detected = False

                if self.collision_type == "overtaking":
                    # Overtaking occurs when O1 passes O2 and is within threshold
                    # Since O2 is static, O1 reaching O2's position constitutes the "overtaking"
                    if distance < 50: # Close enough for overtaking
                        collision_detected = True
                        print(f"O1 passes O2, min distance: {distance:.2f} "
                              f"at {current_time} ms (overtaking)")

                elif self.collision_type in ["fake_causal", "true_causal"]:
                    if distance < 20: # Much closer for collision
                        collision_detected = True

                if collision_detected:
                    self.collision_time = current_time
                    print(f"Collision detected at {current_time} ms, "
                          f"type: {self.collision_type}, distance: {distance:.2f}")

                    if self.collision_type == "fake_causal":
                        self.o1.stopped = True
                        self.o2.stopped = True # O2 is already not moving, but set stopped=True for consistency
                        self.o2.is_moving = False # Explicitly ensure O2 remains not moving
                        print(f"Both objects stopped at collision time "
                              f"{current_time} ms (fake_causal)")

                    elif self.collision_type == "true_causal":
                        self.o1.stopped = True
                        self.o2.is_moving = True # O2 starts moving after true_causal collision
                        # For true_causal, O2 takes over O1's movement.
                        # Its position should be updated to O1's current position to simulate the "hand-off."
                        self.o2.position_index = self.o1.position_index
                        self.o2.x, self.o2.y = POSITIONS[self.o2.position_index]
                        self.o2.dx = 0 # No immediate displacement, just starts moving along path
                        self.o2.dy = 0
                        self.o2.last_move_time = current_time # Set last_move_time to current_time for immediate move
                        print(f"O2 starts moving on O1's trajectory at index "
                              f"{self.o2.position_index}, O1 stopped at "
                              f"{current_time} ms (true_causal)")

            # Handle fake_causal pause end
            if (self.collision_type == "fake_causal" and
                    self.collision_time is not None and
                    not self.fake_causal_pause_ended and
                    current_time >= self.collision_time + self.fake_causal_duration):
                self.o2.is_moving = True
                self.o2.stopped = False
                # O2 now moves from O1's position at the time the pause ends.
                # Its position index needs to be synchronized with O1's last position before O1 stopped.
                self.o2.position_index = self.o1.position_index # O2 starts moving from where O1 stopped
                self.o2.x, self.o2.y = POSITIONS[self.o2.position_index]
                self.o2.last_move_time = current_time # Set last_move_time to current_time for immediate move
                self.o1.stopped = True
                self.o1.is_moving = False # O1 remains stopped
                self.fake_causal_pause_ended = True
                print(f"250ms pause ended at {current_time} ms. "
                      f"O2 starts moving from O1's last position, O1 remains static (Fake Causal)")

            if current_time > self.t2_time + 1000: # Ensure enough time after T2 for response
                if self.state == "running":
                    self.state = "asking"
                    print("\n" + "=" * 50)
                    if self.attention_prompt:
                        print("ATTENTION CHECK: Did you see a red dot appear "
                              "anywhere on the screen?")
                        print("Type 'yes' or 'no' and press ENTER")
                    else:
                        print("What letters did you see? Type the letters "
                              "and press ENTER")
                        print("Example: 'AK' or 'XYZ'")
                    print("=" * 50)

        except Exception as e:
            print(f"Update error: {e}")
            raise

    def submit_response(self, T1_response, T2_response):
        """Called from main.py when user presses ENTER"""
        try:
            self.T1_response = T1_response.strip().upper()
            self.T2_response = T2_response.strip().upper()
            self.check_response(self.T1_response + " " + self.T2_response)
            self.state = "completed"
            print(f"Trial completed. Score: {self.score}")
            self.log_trial()
            return True
        except Exception as e:
            print(f"Submit response error: {e}")
            return False

    def check_response(self, response):
        try:
            response = response.upper().strip()
            valid_chars = [c for c in response if c.isalpha()]
            self.score = 0

            print(f"Raw response: '{response}'")
            responses = [r.strip().lower() for r in response.split() if r.strip()]

            '''if self.attention_prompt:
                self.T1_response = response
                self.T2_response = response
                print("Attention Prompt Trial.. no scoring")
                return'''
            #else:
            self.T1_response = valid_chars[0] if len(valid_chars) >= 1 else ""
            self.T2_response = valid_chars[1] if len(valid_chars) >= 2 else ""

            print(f"Parsed responses: {responses}")
            if not self.t2_time:
                self.T2_response = ""

            self.score = 0
            #if self.attention_prompt:
                #print("Attention prompt trial - no scoring")
                #return

            if self.t1_value and self.t1_value.lower() in responses:
                print(f"T1 correct: {self.t1_value}")
                self.score += 1
            else:
                print(f"T1 wrong: Expected {self.t1_value}, got {responses}")

            if self.t2_value and self.t2_value.lower() in responses:
                print(f"T2 correct: {self.t2_value}")
                self.score += 1
            else:
                print(f"T2 wrong: Expected {self.t2_value}, got {responses}")

        except Exception as e:
            print(f"Check response error: {e}")

    def get_results(self):
        return {
            "participant_id": self.participant_id,
            "collision_type": self.collision_type,
            "which_changes": self.which_changes,
            "lag": self.lag,
            "o1_start": self.o1.original_text,
            "o2_start": self.o2.original_text,
            "score": self.score,
            "t1_value": self.t1_value,
            "t2_value": self.t2_value,
            "attention_prompt": self.attention_prompt,
            "t1_object": self.t1_object,
            "t2_object": self.t2_object,
            "T1_response": self.T1_response,
            "T2_response": self.T2_response,
            "is_training": self.is_training
        }

    def log_trial(self, filename="Arthur.csv"):
        results = self.get_results()
        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(results)
