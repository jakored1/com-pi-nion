#!/usr/bin/env python

import json
from time import sleep
import os
import sys

from main import clear_screen, display_text, display_image, run_actions

with open("global_config.json", 'r') as f:
	CONFIG = json.loads(f.read())

sys.path.append(os.path.join(CONFIG["base_dir"], "e-Paper/RaspberryPi_JetsonNano/python/lib"))

from PIL import Image, ImageDraw, ImageFont
import socket
import warnings
from waveshare_epd import epd2in13_V3

# Setting font
FONT = ImageFont.truetype(CONFIG["text_font"], CONFIG["text_font_size"])
FONT_STROKE_WIDTH = CONFIG["text_font_stroke_width"]
BOLD_FONT = ImageFont.truetype(CONFIG["text_font_bold"], CONFIG["text_font_size"])
BOLD_FONT_STROKE_WIDTH = CONFIG["text_font_stroke_width_bold"]

# Locations dir
LOCATIONS_DIR = os.path.join(CONFIG["base_dir"], "images/locations")
UNKNOWN_LOCATION_DIR = os.path.join(CONFIG["base_dir"], "images/unkown_location")


if __name__ == '__main__':

	if len(sys.argv) < 2:
		print("usage: python test_animation.py /path/to/directory/with/actions_or_config_file/")
		exit()
	user_dir = sys.argv[1]
	if not os.path.isdir(user_dir):
		print("usage: python test_animation.py /path/to/directory/with/actions_or_config_file/")
		print(f"\nError: '{user_dir}' is not a valid directory")
		exit()
	if os.path.isfile(os.path.join(user_dir, "config.json")):
		config_file = os.path.join(user_dir, "config.json")
	elif os.path.isfile(os.path.join(user_dir, "actions.json")):
		config_file = os.path.join(user_dir, "actions.json")
	else:
		print("usage: python test_animation.py /path/to/directory/with/actions_or_config_file/")
		print(f"\nError: no 'actions.json' or 'config.json' file in directory '{user_dir}'")
		exit()

	try:
		with open(config_file, "r") as f:
			actions = json.loads(f.read())
			if os.path.basename(config_file) == "config.json":
				actions = list(actions["actions"])
	except Exception as e:
		print("usage: python test_animation.py /path/to/directory/with/actions_or_config_file/")
		print(f"\nError: ran into an error reading or parsing the file '{config_file}'")
		print(f"ERROR:\n{e}")
		exit()

	try:
		epd = epd2in13_V3.EPD()

		clear_screen(epd)
		run_actions(epd, user_dir, actions)

		epd.sleep()
		epd2in13_V3.epdconfig.module_exit(cleanup=True)

	except IOError as e:
		print(e)

	except KeyboardInterrupt:
		# print("ctrl + c:")
		epd2in13_V3.epdconfig.module_exit(cleanup=True)
