import threading
import time

class RFIDManager:
    def __init__(self, led_reference=None):
        # Pass a reference to the LED if you want the RFID to trigger it directly
        self.led = led_reference  
        self.running = True
        
        # Initialize your actual RFID reader hardware here
        # self.reader = SimpleMFRC522() 

        # Automatically start the background thread upon creation
        self.thread = threading.Thread(target=self._rfid_thread_worker, daemon=True)
        self.thread.start()

    def _rfid_thread_worker(self):
        """Internal method that runs in the background to handle blocking RFID reads."""
        print("RFID Thread Started...")
        while self.running:
            try:
                # 1. This line blocks execution until a card is present
                # id, text = self.reader.read() 
                
                # (Simulated blocking read for demonstration)
                time.sleep(5) 
                print("[RFID] Card Scanned successfully!")

                # 2. Trigger an action on another component if available
                if self.led:
                    self.led.blink(on_time=0.1, off_time=0.1, n=3)

            except Exception as e:
                print(f"Error in RFID thread: {e}")
                time.sleep(1) # Prevent infinite rapid looping on hardware errors

    def stop(self):
        """Clean up thread safely if needed."""
        self.running = False