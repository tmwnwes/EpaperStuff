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

#
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

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clk2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize variables
counter1 = 50
counter2 = 50

# **Initialize clk1LastState and clk2LastState with their respective GPIO input states**
clk1LastState = GPIO.input(clk1)  # Initialize to the current state of clk1
clk2LastState = GPIO.input(clk2)  # Initialize to the current state of clk2

# Mapping function
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Callback function for Encoder 1
def rotary_callback1(channel):
    global counter1, clk1LastState  # Added clk1LastState to track properly
    clkState = GPIO.input(clk1)
    dtState = GPIO.input(dt1)

    if clkState != clk1LastState:  # State has changed
        if dtState != clkState:
            counter1 += 1
        else:
            counter1 -= 1
        # Map counter1 to range
        mapped_value1 = map_value(counter1, 0, 100, range1_min, range1_max)  # Adjusted for example range
        print(f"Encoder 1 Counter: {counter1}, Mapped Value: {mapped_value1}")
    
    # **Update clk1LastState**
    clk1LastState = clkState

# Callback function for Encoder 2
def rotary_callback2(channel):
    global counter2, clk2LastState  # Added clk2LastState to track properly
    clkState = GPIO.input(clk2)
    dtState = GPIO.input(dt2)

    if clkState != clk2LastState:  # State has changed
        if dtState != clkState:
            counter2 += 1
        else:
            counter2 -= 1
        # Map counter2 to range
        mapped_value2 = map_value(counter2, 0, 100, range2_min, range2_max)  # Adjusted for example range
        print(f"Encoder 2 Counter: {counter2}, Mapped Value: {mapped_value2}")
    
    # **Update clk2LastState**
    clk2LastState = clkState

# **Increased bouncetime for better signal stability**
GPIO.add_event_detect(clk1, GPIO.BOTH, callback=rotary_callback1, bouncetime=5)
GPIO.add_event_detect(clk2, GPIO.BOTH, callback=rotary_callback2, bouncetime=5)


logging.basicConfig(level=logging.DEBUG)

try:

    print("Dual Rotary Encoder Test with Mapping - Press Ctrl+C to exit")
    logging.info("epd7in5b_V2 Demo")

    epd = epd7in5b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    # # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Himage)
    draw_other = ImageDraw.Draw(Other)
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

    
    # Drawing on the Vertical image
    logging.info("2.Drawing on the Vertical image...")
    Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    Limage_Other = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Limage)
    draw_Himage_Other = ImageDraw.Draw(Limage_Other)
    draw_Himage.text((2, 0), 'hello world', font = font18, fill = 0)
    draw_Himage.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    draw_Himage_Other.text((20, 50), u'微雪电子', font = font18, fill = 0)
    draw_Himage_Other.line((10, 90, 60, 140), fill = 0)
    draw_Himage_Other.line((60, 90, 10, 140), fill = 0)
    draw_Himage_Other.rectangle((10, 90, 60, 140), outline = 0)
    draw_Himage_Other.line((95, 90, 95, 140), fill = 0)
    draw_Himage.line((70, 115, 120, 115), fill = 0)
    draw_Himage.arc((70, 90, 120, 140), 0, 360, fill = 0)
    draw_Himage.rectangle((10, 150, 60, 200), fill = 0)
    draw_Himage.chord((70, 150, 120, 200), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Limage), epd.getbuffer(Limage_Other))
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
