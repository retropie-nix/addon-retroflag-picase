# RetroFlag Pi Case safe shutdown script

import os
import signal
import sys
import threading
import time
import subprocess

import RPi.GPIO

# GPIO assignments are board numbers
POWER_SWITCH_PIN = 3  # power switch input
RESET_SWITCH_PIN = 2  # reset switch input
POWER_PIN = 4         # power enable output
LED_PIN = 14          # LED enable output
POLL_INTERVAL = 0.1   # seconds between polling of inputs

# pin number -> command
SWITCH_COMMAND_MAP = {
    POWER_SWITCH_PIN: 'systemctl reboot',
    RESET_SWITCH_PIN: 'systemctl reboot',
}


def main():
    """Program entry point."""
    init_gpio()
    led_blinker = Blinker(LED_PIN)
    led_blinker.start()

    # create a trap to set LED solid before process exits
    def handle_signal(signum, frame):
        led_blinker.stop()
        led_blinker.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_signal)  # user exit (for testing)
    signal.signal(signal.SIGTERM, handle_signal)  # system exit (for shutdown)

    # run command for each switch press
    while True:
        pressed_pin = wait_for_press(SWITCH_COMMAND_MAP.keys())
        command = SWITCH_COMMAND_MAP[pressed_pin]
        led_blinker.blink()
        run(command)
        led_blinker.solid()


def run(command):
    """Change working directory to shutdown script location and run command."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    subprocess.run(command, shell=True, check=True, text=True)


def init_gpio():
    """Set pin directions and pull-ups/pull-downs."""
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    RPi.GPIO.setwarnings(False)

    RPi.GPIO.setup(POWER_SWITCH_PIN, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(RESET_SWITCH_PIN, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(POWER_PIN, RPi.GPIO.OUT, initial=RPi.GPIO.HIGH)


def wait_for_press(pins):
    """Wait for a falling edge on one of pins and return pin number."""
    prev_states = [RPi.GPIO.input(pin) for pin in pins]
    while True:
        states = []

        for index, pin in enumerate(pins):
            prev_state = prev_states[index]
            state = RPi.GPIO.input(pin)

            # detect falling edge
            if prev_state == RPi.GPIO.HIGH and state == RPi.GPIO.LOW:
                return pin

            states.append(state)

        # sleep so polling doesn't eat CPU
        time.sleep(POLL_INTERVAL)
        prev_states = states


class Blinker(threading.Thread):
    """Thread that toggles a pin on a fixed interval.
    Initial (after __init__()) and final (after stop()) state will be high.
    """
    DEFAULT_STATE = RPi.GPIO.HIGH  # initial and final state of pin
    BLINK_INTERVAL = 0.2           # seconds LED is on/off during blinking

    def __init__(self, pin):
        """Create a thread that toggles pin every interval seconds."""
        super(Blinker, self).__init__()

        self._pin = pin
        self._blink_event = threading.Event()  # set to enable blinking
        self._stop_event = threading.Event()  # set to stop thread

        RPi.GPIO.setup(pin, RPi.GPIO.OUT)

    def run(self):
        """Implementation of threading.Thread.run()."""
        state = self.DEFAULT_STATE
        while not self._stop_event.is_set():
            # blinking state
            if self._blink_event.is_set():
                state = not state
            # solid state
            else:
                state = self.DEFAULT_STATE

            RPi.GPIO.output(self._pin, state)
            self._stop_event.wait(self.BLINK_INTERVAL)

        # return to default state
        RPi.GPIO.output(self._pin, self.DEFAULT_STATE)

    def stop(self):
        """Stop thread."""
        self._stop_event.set()

    def blink(self):
        """Start blinking."""
        self._blink_event.set()

    def solid(self):
        """Stop blinking."""
        self._blink_event.clear()


if __name__ == '__main__':
    main()
