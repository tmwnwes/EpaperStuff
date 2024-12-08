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
        sleep(0.005)  # 5ms polling interval

# Old coordinates update thread
def update_old_coordinates():
    global XcoordOLD, YcoordOLD
    while True:
        XcoordOLD = Xcoord
        YcoordOLD = Ycoord
        if (XcoordOLD != Xcoord):
            print(f"Updated XcoordOLD: {XcoordOLD}, YcoordOLD: {YcoordOLD}")
        sleep(0.5)  # 5ms interval

try:
    print("Dual Rotary Encoder Test with Threads - Press Ctrl+C to exit")

    # Start threads for rotary encoders and updating old coordinates
    encoder_thread = threading.Thread(target=rotary_thread, daemon=True)
    coord_update_thread = threading.Thread(target=update_old_coordinates, daemon=True)
    encoder_thread.start()
    coord_update_thread.start()

    logging.info("epd7in5b_V2 Demo")

    epd = epd7in5b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Himage)
    draw_other = ImageDraw.Draw(Other)

    # for x in range(6):
    #     draw_other.line((165, 50, 165, 100), fill = 0)
    #     draw_Himage.line((140, 75, 190, 75), fill = 0)

    # # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    draw_Himage.text((10, 0), 'hello world', font = font24, fill = 0)
    draw_Himage.text((10, 20), '7.5inch e-Paper B', font = font24, fill = 0)
    draw_Himage.text((150, 0), u'微雪电子', font = font24, fill = 0)    
    draw_other.line((20, 50, 70, 100), fill = 0)
    draw_other.line((70, 50, 20, 100), fill = 0)
    draw_other.rectangle((20, 50, 70, 100), outline = 0)
    draw_other.line((165, 50, 165, 100), fill = 0)
    draw_Himage.line((140, 75, 190, 75), fill = 0)
    draw_Himage.arc((140, 50, 190, 100), 0, 360, fill = 0)
    draw_Himage.rectangle((80, 50, 130, 100), fill = 0)
    draw_Himage.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
    time.sleep(2)

    logging.info("3.read bmp file")
    epd.init_Fast()
    Himage = Image.open(os.path.join(picdir, '7in5_V2_b.bmp'))
    Himage_Other = Image.open(os.path.join(picdir, '7in5_V2_r.bmp'))
    epd.display(epd.getbuffer(Himage),epd.getbuffer(Himage_Other))
    time.sleep(2)

    # # partial update
    # logging.info("4.show time")
    # epd.init()
    # epd.display_Base_color(0xFF)
    # epd.init_part()
    # Himage = Image.new('1', (epd.width, epd.height), 0)
    # draw_Himage = ImageDraw.Draw(Himage)
    # num = 0
    # while (True):
    #     draw_Himage.rectangle((10, 120, 130, 170), fill = 0)
    #     draw_Himage.text((10, 120), time.strftime('%H:%M:%S'), font = font24, fill = 255)
    #     epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
    #     num = num + 1
    #     if(num == 10):
    #         break


    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit(cleanup=True)
    exit()


finally:
    GPIO.cleanup()
