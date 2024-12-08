# from RPi import GPIO
# from time import sleep

# clk = 19
# dt = 16

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# counter = 0
# clkLastState = GPIO.input(clk)

# try:

#         while True:
#                 clkState = GPIO.input(clk)
#                 dtState = GPIO.input(dt)
#                 if clkState != clkLastState:
#                         if dtState != clkState:
#                                 counter += 1
#                         else:
#                                 counter -= 1
#                         print (counter)
#                 clkLastState = clkState
#                 sleep(0.01)
# finally:
#         GPIO.cleanup()

from RPi import GPIO
from time import sleep

# Pin definitions
clk = 19
dt = 16

# Initialize variables
counter = 0
clkLastState = 0

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Callback function to handle encoder changes
def rotary_callback(channel):
    global counter, clkLastState

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState != clkLastState:
        if dtState != clkState:
            counter += 1
        else:
            counter -= 1
        print(f"Counter: {counter}")

    clkLastState = clkState

# Setup interrupt for the CLK pin
GPIO.add_event_detect(clk, GPIO.BOTH, callback=rotary_callback, bouncetime=1)

try:
    print("Rotary Encoder Test - Press Ctrl+C to exit")
    while True:
        sleep(0.1)  # Main loop can remain lightweight
finally:
    GPIO.cleanup()
