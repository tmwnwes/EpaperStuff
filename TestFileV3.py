#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import threading
import logging
import time
from waveshare_epd import epd7in5b_V2
from PIL import Image,ImageDraw,ImageFont
from RPi import GPIO


# Paths for assets
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)



# GPIO pins for rotary encoders
ENCODER_1_CLK = 19
ENCODER_1_DT = 16
ENCODER_2_CLK = 20
ENCODER_2_DT = 26

# Mapped value ranges
RANGE_X_MIN, RANGE_X_MAX = 0, 800
RANGE_Y_MIN, RANGE_Y_MAX = 0, 480

# Shared variables
Xcoord, Ycoord = 0, 0
XcoordOLD, YcoordOLD = 0, 0
is_update = False

shutdown_flag = False
lock = threading.Lock()

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_1_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_1_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_2_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_2_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mapping function
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Rotary encoder handling
def process_encoder(clk_pin, dt_pin, counter, range_min, range_max):
    clk_last_state = GPIO.input(clk_pin)
    while not shutdown_flag:
        clk_state = GPIO.input(clk_pin)
        dt_state = GPIO.input(dt_pin)
        if clk_state != clk_last_state:
            if dt_state != clk_state:
                counter += 1
            else:
                counter -= 1
            counter = max(0, min(counter, 100))  # Limit counter to [0, 100]
            mapped_value = map_value(counter, 0, 100, range_min, range_max)
            with lock:
                if clk_pin == ENCODER_1_CLK:
                    global Xcoord
                    Xcoord = mapped_value
                else:
                    global Ycoord
                    Ycoord = mapped_value
            logging.info(f"Encoder on pin {clk_pin} updated: {mapped_value}")
        clk_last_state = clk_state
        time.sleep(0.005)

# Coordinates update thread
def update_coordinates():
    global XcoordOLD, YcoordOLD, is_update
    while not shutdown_flag:
        with lock:
            if (XcoordOLD != Xcoord) or (YcoordOLD != Ycoord):
                XcoordOLD, YcoordOLD = Xcoord, Ycoord
                is_update = True
                logging.info(f"Coordinates updated: X={XcoordOLD}, Y={YcoordOLD}")
        time.sleep(0.005)

# E-paper display handler
def display_handler():
    epd = epd7in5b_V2.EPD()
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    
    h_image = Image.new('1', (epd.width, epd.height), 255)
    other_image = Image.new('1', (epd.width, epd.height), 255)
    draw_h_image = ImageDraw.Draw(h_image)
    draw_other = ImageDraw.Draw(other_image)

    try:
        while not shutdown_flag:
            if is_update:
                draw_other.line((XcoordOLD, YcoordOLD, Xcoord, Ycoord), fill=0)
                epd.display(epd.getbuffer(h_image), epd.getbuffer(other_image))
                logging.info("Display updated")
            time.sleep(1)
    except Exception as e:
        logging.error(f"Display handler error: {e}", exc_info=True)
    finally:
        epd.Clear()
        epd.sleep()

# Unified shutdown
def shutdown():
    global shutdown_flag
    logging.info("Shutting down...")
    shutdown_flag = True
    GPIO.cleanup()
    logging.info("GPIO cleaned up.")

# Main
try:
    logging.info("Starting rotary encoder threads...")
    threading.Thread(target=process_encoder, args=(ENCODER_1_CLK, ENCODER_1_DT, 50, RANGE_X_MIN, RANGE_X_MAX), daemon=True).start()
    threading.Thread(target=process_encoder, args=(ENCODER_2_CLK, ENCODER_2_DT, 50, RANGE_Y_MIN, RANGE_Y_MAX), daemon=True).start()
    threading.Thread(target=update_coordinates, daemon=True).start()
    threading.Thread(target=display_handler, daemon=True).start()

    while not shutdown_flag:
        time.sleep(0.1)

except KeyboardInterrupt:
    logging.info("Shutdown signal received.")
    logging.info("ctrl + c:")
    shutdown()

finally:
    shutdown()
