import threading
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
counter1 = 50
counter2 = 50
clk1LastState = 0
clk2LastState = 0

# Coordinates for tracking
Xcoord = 0
Ycoord = 0
XcoordOLD = 0
YcoordOLD = 0

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clk2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize clkLastState values
clk1LastState = GPIO.input(clk1)
clk2LastState = GPIO.input(clk2)

# Mapping function
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Rotary encoder processing thread
def rotary_thread():
    global counter1, counter2, clk1LastState, clk2LastState, Xcoord, Ycoord

    while True:
        # Handle Encoder 1
        clkState1 = GPIO.input(clk1)
        dtState1 = GPIO.input(dt1)
        if clkState1 != clk1LastState:
            if dtState1 != clkState1:
                counter1 += 1
            else:
                counter1 -= 1
            Xcoord = map_value(counter1, 0, 100, range1_min, range1_max)
            print(f"Encoder 1 Counter: {counter1}, Mapped Xcoord: {Xcoord}")
        clk1LastState = clkState1

        # Handle Encoder 2
        clkState2 = GPIO.input(clk2)
        dtState2 = GPIO.input(dt2)
        if clkState2 != clk2LastState:
            if dtState2 != clkState2:
                counter2 += 1
            else:
                counter2 -= 1
            Ycoord = map_value(counter2, 0, 100, range2_min, range2_max)
            print(f"Encoder 2 Counter: {counter2}, Mapped Ycoord: {Ycoord}")
        clk2LastState = clkState2

        # Sleep for a small amount to prevent excessive CPU usage
        sleep(0.05)  # 5ms polling interval

# Old coordinates update thread
def update_old_coordinates():
    global XcoordOLD, YcoordOLD
    while True:
        XcoordOLD = Xcoord
        YcoordOLD = Ycoord
        print(f"Updated XcoordOLD: {XcoordOLD}, YcoordOLD: {YcoordOLD}")
        sleep(0.5)  # 5ms interval

try:
    print("Dual Rotary Encoder Test with Threads - Press Ctrl+C to exit")

    # Start threads for rotary encoders and updating old coordinates
    encoder_thread = threading.Thread(target=rotary_thread, daemon=True)
    coord_update_thread = threading.Thread(target=update_old_coordinates, daemon=True)
    encoder_thread.start()
    coord_update_thread.start()

    # Main program loop
    while True:
        # Main loop can perform other tasks
        sleep(0.1)  # Simulate work in the main loop

finally:
    GPIO.cleanup()
