#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_V2
from RPi import GPIO
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import threading
from RPi import GPIO
from time import sleep
from gpiozero import Button


# Pin definitions for Encoder 1
clk1 = 19
dt1 = 16

# Pin definitions for Encoder 2
clk2 = 20
dt2 = 26

# Push buttons
buttonL = Button(13)
buttonR = Button(12)

# Range for mapped values
range1_min, range1_max = 0, 800
range2_min, range2_max = 0, 480

# Initialize variables
counter1 = 50
counter2 = 50
clk1LastState = 0
clk2LastState = 0

shutdown_flag = False
is_update = False
color_switch = False
exit_drawing = False

lock = threading.Lock()

# Coordinates for tracking
Xcoord = 0
Ycoord = 0
XcoordOLD = 0
YcoordOLD = 0

tempX = 0
tempY = 0

tempX2 = 0
tempY2 = 0

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
    try:
        while not shutdown_flag:

            # Handle Encoder 1
            clkState1 = GPIO.input(clk1)
            dtState1 = GPIO.input(dt1)
            if clkState1 != clk1LastState:
                if dtState1 != clkState1:
                    counter1 += 1
                else:
                    counter1 -= 1

                counter1 = max(0, min(counter1, 100))  # Limit counter to [0, 100]
                Xcoord = map_value(counter1, 0, 100, range1_min, range1_max)
                logging.info(f"Encoder 1 Counter: {counter1}, Mapped Xcoord: {Xcoord}")
            clk1LastState = clkState1

            # Handle Encoder 2
            clkState2 = GPIO.input(clk2)
            dtState2 = GPIO.input(dt2)
            if clkState2 != clk2LastState:
                if dtState2 != clkState2:
                    counter2 += 1
                else:
                    counter2 -= 1

                counter2 = max(0, min(counter2, 100))  # Limit counter to [0, 100]
                Ycoord = map_value(counter2, 0, 100, range2_min, range2_max)
                logging.info(f"Encoder 2 Counter: {counter2}, Mapped Ycoord: {Ycoord}")
            clk2LastState = clkState2

            # Sleep for a small amount to prevent excessive CPU usage
            sleep(0.005)  # 5ms polling interval
    except Exception as e:
        logging.error(f"Exception in rotary_thread: {e}", exc_info=True)

# Old coordinates update thread
def update_old_coordinates():
    global XcoordOLD, YcoordOLD, tempX2, tempY2, is_update
    XcoordOLD = 400
    YcoordOLD = 240

    try:
        while not shutdown_flag:
            with lock: #maybe remove this
                if is_update:  # Detect changes
                    XcoordOLD = tempX2
                    YcoordOLD = tempY2
                    print(f"Updated XcoordOLD: {XcoordOLD}, YcoordOLD: {YcoordOLD}")
                    is_update = False

            time.sleep(1)
    except Exception as e:
        logging.error(f"Exception in update_old_coordinates: {e}", exc_info=True)

def left_button_check():
    global exit_drawing
    try:
        while not shutdown_flag:
            if buttonL.is_pressed:
                print("Left button pressed")
                exit_drawing = True
                time.sleep(0.5)  # Debounce
            time.sleep(0.05)  # free up CPU
    except Exception as e:
        logging.error(f"Exception in left_button_check: {e}", exc_info=True)

def right_button_check():
    global color_switch
    try:
        while not shutdown_flag:
            if buttonR.is_pressed:
                print("Right button pressed")
                color_switch = not color_switch
                time.sleep(0.5)  # Debounce
            time.sleep(0.05)  # free up CPU
    except Exception as e:
        logging.error(f"Exception in right_button_check: {e}", exc_info=True)

try:

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Dual Rotary Encoder Test with Threads - Press Ctrl+C to exit")

    # Start threads for rotary encoders and updating old coordinates
    encoder_thread = threading.Thread(target=rotary_thread, daemon=True)
    coord_update_thread = threading.Thread(target=update_old_coordinates, daemon=True)
    left_button_thread = threading.Thread(target=left_button_check, daemon=True)
    right_button_thread = threading.Thread(target=right_button_check, daemon=True)
    encoder_thread.start()
    coord_update_thread.start()
    left_button_thread.start()
    right_button_thread.start()

    logging.info("Etch a Sketch Test")

    epd = epd7in5b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame BLACK
    Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame RED
    draw_Himage = ImageDraw.Draw(Himage)
    draw_other = ImageDraw.Draw(Other)

    while not exit_drawing:
        tempX, tempY, tempX2, tempY2 = XcoordOLD, YcoordOLD, Xcoord, Ycoord
        for x in range(5, 0, -1):
            print(x) 
            time.sleep(1)
        if color_switch:
            draw_other.line((tempX, tempY, tempX2, tempY2), fill = 0)
            epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
            print(f"red drawn")
            is_update = True
        elif not color_switch:
            draw_Himage.line((tempX, tempY, tempX2, tempY2), fill = 0)
            epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
            print(f"black drawn")
            is_update = True

    # logging.info("3.read bmp file")
    # epd.init_Fast()
    # Himage = Image.open(os.path.join(picdir, '7in5_V2_b.bmp'))
    # Himage_Other = Image.open(os.path.join(picdir, '7in5_V2_r.bmp'))
    # epd.display(epd.getbuffer(Himage),epd.getbuffer(Himage_Other))
    # time.sleep(2)

    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    logging.info("Shutdown signal received.")
    logging.info("ctrl + c:")
    logging.info("Goto Sleep...")
    epd.sleep()
    shutdown_flag = True  # Signal threads to stop
    encoder_thread.join()  # Wait for threads to finish
    coord_update_thread.join()
    left_button_thread.join()
    right_button_thread.join()
    epd7in5b_V2.epdconfig.module_exit(cleanup=True)
    exit()

finally:
    logging.info("Shutting down...")
    shutdown_flag = True  # Signal threads to stop

    # Wait for threads to finish
    try:
        encoder_thread.join(timeout=1)
        coord_update_thread.join(timeout=1)
        left_button_thread.join(timeout=1)
        right_button_thread.join(timeout=1)
    except Exception as e:
        logging.error(f"Error while joining threads: {e}")

    GPIO.cleanup()
    epd7in5b_V2.epdconfig.module_exit(cleanup=True)
    logging.info("GPIO cleaned up and e-Paper module exited.")