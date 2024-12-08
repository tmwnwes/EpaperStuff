from RPi import GPIO
from time import sleep

# Pin definitions for Encoder 1
clk1 = 19
dt1 = 16

# Pin definitions for Encoder 2
clk2 = 20
dt2 = 26

# Initialize variables
counter1 = 0
counter2 = 0
clk1LastState = 0
clk2LastState = 0

Xcoord = 0
Ycoord = 0

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clk2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Callback function for Encoder 1
def rotary_callback1(channel):
    global counter1, clk1LastState

    clkState = GPIO.input(clk1)
    dtState = GPIO.input(dt1)

    if clkState != clk1LastState:
        if dtState != clkState:
            counter1 += 1
        else:
            counter1 -= 1
        #print(f"Encoder 1 Counter: {counter1}")

        Xcoord = map(counter2, 0, 800, -100, 100)
        print(f"Encoder 1 Counter: {Xcoord}")

    clk1LastState = clkState

# Callback function for Encoder 2
def rotary_callback2(channel):
    global counter2, clk2LastState

    clkState = GPIO.input(clk2)
    dtState = GPIO.input(dt2)

    if clkState != clk2LastState:
        if dtState != clkState:
            counter2 += 1
        else:
            counter2 -= 1
        #print(f"Encoder 2 Counter: {counter2}")

        Ycoord = map(counter2, 0, 480, -50, 50)
        print(f"Encoder 2 Counter: {Ycoord}")
    clk2LastState = clkState

# Setup interrupts for both encoders
GPIO.add_event_detect(clk1, GPIO.BOTH, callback=rotary_callback1, bouncetime=1)
GPIO.add_event_detect(clk2, GPIO.BOTH, callback=rotary_callback2, bouncetime=1)

try:
    print("Dual Rotary Encoder Test - Press Ctrl+C to exit")
    while True:
        sleep(0.1)  # Main loop can remain lightweight
finally:
    GPIO.cleanup()
