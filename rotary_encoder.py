from RPi import GPIO
from time import sleep

# Pin definitions for Encoder 1
clk1 = 19
dt1 = 16

# Pin definitions for Encoder 2
clk2 = 20
dt2 = 26

# Range for mapped values
range1_min, range1_max = 0, 800
range2_min, range2_max = 0, 480

# Initialize variables
counter1 = 0
counter2 = 0
clk1LastState = 0
clk2LastState = 0

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clk2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Mapping function
def map_value(value, in_min, in_max, out_min, out_max):
    value = max(in_min, min(in_max, value))  # Clamp the value
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Callback function for Encoder 1
def rotary_callback1(channel):
    global counter1

    clkState = GPIO.input(clk1)
    dtState = GPIO.input(dt1)

    if clkState != clk1LastState:
        if dtState != clkState:
            counter1 += 1
        else:
            counter1 -= 1

        # Map counter1 to range
        mapped_value1 = map_value(counter1, 0, 100, range1_min, range1_max)  # Example counter range: 0-100
        print(f"Encoder 1 Counter: {counter1}, Mapped Value: {mapped_value1}")

# Callback function for Encoder 2
def rotary_callback2(channel):
    global counter2

    clkState = GPIO.input(clk2)
    dtState = GPIO.input(dt2)

    if clkState != clk2LastState:
        if dtState != clkState:
            counter2 += 1
        else:
            counter2 -= 1

        # Map counter2 to range
        mapped_value2 = map_value(counter2, 0, 100, range2_min, range2_max)  # Example counter range: 0-100
        print(f"Encoder 2 Counter: {counter2}, Mapped Value: {mapped_value2}")

# Setup interrupts for both encoders
GPIO.add_event_detect(clk1, GPIO.BOTH, callback=rotary_callback1, bouncetime=1)
GPIO.add_event_detect(clk2, GPIO.BOTH, callback=rotary_callback2, bouncetime=1)

try:
    print("Dual Rotary Encoder Test with Mapping - Press Ctrl+C to exit")
    while True:
        sleep(0.1)  # Main loop can remain lightweight
finally:
    GPIO.cleanup()
