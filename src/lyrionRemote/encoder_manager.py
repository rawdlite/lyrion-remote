from gpiozero import RotaryEncoder

class EncoderManager:
    def __init__(self, pin_a, pin_b):
        # Initialize gpiozero's RotaryEncoder
        self.encoder = RotaryEncoder(pin_a, pin_b, max_steps=100)
        
        # Link the internal events to our class methods
        self.encoder.when_rotated_clockwise = self._on_clockwise
        self.encoder.when_rotated_counter_clockwise = self._on_counter_clockwise
        
        self.current_value = 0

    def _on_clockwise(self):
        self.current_value += 1
        print(f"[Encoder] Rotated Clockwise. Value: {self.current_value}")

    def _on_counter_clockwise(self):
        self.current_value -= 1
        print(f"[Encoder] Rotated Counter-Clockwise. Value: {self.current_value}")
        
    def get_steps(self):
        return self.current_value