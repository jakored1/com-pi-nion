#!/usr/bin/env python

import json
from time import sleep
import os
import sys
import random
from requests import get
import re
from math import radians, cos, sin, asin, sqrt

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

# BSSID locator script
BSSID_LOCATOR = os.path.join(CONFIG["base_dir"], "bssid_locator/main.py")

# Locations dir
LOCATIONS_DIR = os.path.join(CONFIG["base_dir"], "images/locations")
UNKNOWN_LOCATION_DIR = os.path.join(CONFIG["base_dir"], "images/unkown_location")


def clear_screen(epd):
	""" Clears the screen """
	# clear screen
	epd.init()
	epd.Clear(0xFF)


def display_text(epd, message: str, display_partial=False, clear=False, bold=False):
	""" Displays given text at the center of the e-ink display """
	if clear:
		clear_screen(epd)

	image = Image.new('1', (epd.height, epd.width), 255)
	draw = ImageDraw.Draw(image)

	# center the text
	if bold:
		_, _, w, h = draw.textbbox((0, 0), message, font=BOLD_FONT)
		draw.text(((epd.height-w)/2, (epd.width-h)/2), message, font=BOLD_FONT, fill="black", stroke_width=BOLD_FONT_STROKE_WIDTH, stroke_fill="black")
	else:
		_, _, w, h = draw.textbbox((0, 0), message, font=FONT)
		draw.text(((epd.height-w)/2, (epd.width-h)/2), message, font=FONT, fill="black", stroke_width=FONT_STROKE_WIDTH, stroke_fill="black")

	if display_partial:
		epd.displayPartial(epd.getbuffer(image))
	else:
		epd.display(epd.getbuffer(image))


def display_image(epd, image_path: str, display_partial=False, clear=False):
	""" Receives the full path of a .bmp image and displays it """
	if clear:
		clear_screen(epd)

	image = Image.open(image_path)

	if display_partial:
		epd.displayPartial(epd.getbuffer(image))
	else:
		epd.display(epd.getbuffer(image))


def check_internet_connection():
	""" Checks weather or not the device can access the internet """
	
	for website in CONFIG['test_internet_with']:
		try:
			url = website["host"]
			expected_status_code = website["expected_status"]
			user_agent = website["user_agent"]
			r = get(url,
				headers={'User-Agent': user_agent},
				timeout=10
			)
			if expected_status_code == r.status_code:
				return True
		except Exception as e:
			print(e)

	# If there is no internet connection
	return False


def connect_to_hotspot(epd):
	""" Connects to wifi network defined in the config file """
	looking_face = random.choice(CONFIG['looking_characters'])
	message = f"Connecting to the hotspot\nSsid - {CONFIG['mobile_hotspot_ssid']}\nPassword - {CONFIG['mobile_hotspot_password']}"
	display_text(epd, f"{message}\n\n{looking_face}", clear=False, display_partial=False)

	# Show current connections
	output = os.popen("nmcli connection show").read()
	# Close any connections using the wifi interface
	connections = output.split("\n")
	del connections[-1]  # Delete empty line
	for connection in connections:
		details = [i for i in connection.split(" ") if i != ""]
		if details[-1] == CONFIG["wifi_interface"]:
			output = os.popen(f"sudo nmcli con down {details[0]}").read()
	sleep(1)
	cnt = 0
	while True:
		# Connect to network
		output = os.popen(f"nmcli device wifi rescan").read()
		output = os.popen(f"nmcli device wifi connect {CONFIG['mobile_hotspot_ssid']} password {CONFIG['mobile_hotspot_password']}").read()
		sleep(2)

		# Check if we are connected to the wifi network
		if check_internet_connection():
			return True, cnt

		cnt += 1
		if cnt > 10:
			print("Couldn't connect to wifi network (couldn't access the web)")
			return False, cnt
		if cnt % 2 == 0:  # Change looking face every 2 attempts
			looking_face = random.choice(CONFIG['looking_characters'])
		display_text(epd, f"{message}\nAttempt {cnt}\n{looking_face}", clear=False, display_partial=True)


def get_nearby_networks():
	""" Scans nearby networks and returns them nicely """
	output = os.popen(f"sudo iwlist {CONFIG['wifi_interface']} scan").read()
	# parsing results
	networks = []
	bssid = None
	ssid = None
	rssi = None
	for line in output.split("\n"):
		if re.search(r"Cell \d* - Address: ", line.strip()):
			bssid = line.split("Address: ")[-1].strip().lower()
			continue
		if bssid is not None and "ESSID:" in line.strip():
			ssid = line.strip().split("ESSID:")[1][1:][:-1]
			continue
		if bssid is not None and re.search(r"Quality=\d*/\d*  Signal level=", line.strip()):
			rssi = int(line.split("Signal level=")[-1].split(" ")[0].strip())
		if bssid is not None and ssid is not None and rssi is not None:
			networks.append({"bssid": bssid, "ssid": ssid, "rssi": rssi})
			bssid = None
			ssid = None
			rssi = None
			continue

	return networks


def get_networks_and_coordinates():
	""" Attempts to get the coordinates of the device by scanning nearby networks and fetching their location """
	message = random.choice(CONFIG['finding_location_message'])
	looking_face = random.choice(CONFIG['looking_characters'])
	display_bssids = CONFIG['display_bssids']
	if display_bssids:
		display_text(epd, f"{message}\n\n  :  :  :  :  :  \n\n{looking_face}", clear=True)
	else:
		display_text(epd, f"{message}\n\n{looking_face}", clear=True)

	# scanning networks
	networks = get_nearby_networks()
	if len(networks) < 1:  # If we didn't scan any networks
		print("No networks were found")
		return None, None

	# Printing for testing
	# print("Found Networks:")
	# for network in networks:
	# 	print(f"-\t{network['bssid']} | {network['rssi']} | {network['ssid']}")

	# finding the BSSID of the best scanned network and finding it's location
	attempted_networks = []
	location = "latitude/longitude"
	while True:
		best_network = ""
		best_rssi = -200
		if len(attempted_networks) == len(networks):
			print("Couldn't locate any of the networks near you")
			return None, networks
		for network in networks:
			if (network['rssi'] > best_rssi) and (network['bssid'] not in attempted_networks):
				best_network = network['bssid']
				best_rssi = network['rssi']
		# Trying to find the networks location
		try:
			looking_face = random.choice(CONFIG['looking_characters'])
			if display_bssids:
				display_text(epd, f"{message}\n\n{best_network}\n\n{looking_face}", clear=False, display_partial=True)
			else:
				display_text(epd, f"{message}\n\n{looking_face}", clear=False, display_partial=True)
			output = os.popen(f"python3 {BSSID_LOCATOR} {best_network}").read()
			output = json.loads(output)
			attempted_networks.append(best_network)
			# If network's location is unknown
			if best_network in output:
				if (output[best_network]["latitude"] == "unknown" and output[best_network]["longitude"] == "unknown") or (best_network not in output):
					continue
			location = [float(output[best_network]["latitude"]), float(output[best_network]["longitude"])]
		except Exception as e:
			continue
		break

	if location == "latitude/longitude":
		return None, networks

	return location, networks


def location_in_radius(current_location: list, target_location: list, radius: float):
	""" Receives a current_location, a target_location, and a radius, and checks if the current_location is in the given radius around target_location """
	lat1 = target_location[0]['lat']
	lon1 = target_location[0]['long']
	lat2 = current_location[0]['lat']
	lon2 = current_location[0]['long']

	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	r = 6371 # Radius of earth in kilometers. Use 3956 for miles
	distance = c * r

	if distance <= radius:  # current_location is inside target_location 
		return True
	else:  # current_location is outside target_location 
		return False


def run_actions(epd, location_dir: str, actions: list):
	""" Receives a folder path and displays the images in the folder according to the actions array """
	for raw_action in actions:
		try:
			action = str(raw_action).strip()
			# clear
			if action == "clear":
				clear_screen(epd)
				continue
			# sleep
			if action.split()[0] == "sleep":
				sleep(float(action.split()[-1]))
			# display message
			if action[0:len("display message ")] == "display message " and len(action) > len("display message "):
				display_text(epd, action.split("display message ")[-1])
				continue
			# display messageBold
			if action[0:len("display messageBold ")] == "display messageBold " and len(action) > len("display messageBold "):
				display_text(epd, action.split("display messageBold ")[-1], bold=True)
				continue
			# displayPartial message
			if action[0:len("displayPartial message ")] == "displayPartial message " and len(action) > len("displayPartial message "):
				display_text(epd, action.split("displayPartial message ")[-1], display_partial=True)
				continue
			# displayPartial messageBold
			if action[0:len("displayPartial messageBold ")] == "displayPartial messageBold " and len(action) > len("displayPartial messageBold "):
				display_text(epd, action.split("displayPartial messageBold ")[-1], display_partial=True, bold=True)
				continue
			# display image
			if action[0:len("display image ")] == "display image " and len(action) > len("display image "):
				image = action.split("display image ")[-1]
				image_path = os.path.join(location_dir, image)
				if image.split(".")[-1] == "bmp" and os.path.isfile(image_path):
					display_image(epd, image_path)
				continue
			# displayPartial image
			if action[0:len("displayPartial image ")] == "displayPartial image " and len(action) > len("displayPartial image "):
				image = action.split("displayPartial image ")[-1]
				image_path = os.path.join(location_dir, image)
				if image.split(".")[-1] == "bmp" and os.path.isfile(image_path):
					display_image(epd, image_path, display_partial=True)
				continue
		except Exception as e:
			print(e)
			continue


def display_unkown_location(epd):
	""" Displays images for unkown location """
	unkown_location_dirs = os.listdir(UNKNOWN_LOCATION_DIR)
	random.shuffle(unkown_location_dirs)
	for unkown_location_dir in unkown_location_dirs:
		try:
			selected_dir = os.path.join(UNKNOWN_LOCATION_DIR, unkown_location_dir)
			actions_file = os.path.join(selected_dir, "actions.json")
			with open(actions_file, "r") as f:
				actions = list(json.loads(f.read()))
			if len(actions) > 0:
				run_actions(epd, selected_dir, actions)
				return
		except Exception as e:
			continue
	display_text(epd, "unkown location")
	sleep(5)
	clear_screen(epd)


def display_images_by_location(epd, coordinates: list, networks: list):
	""" Reads all the config.json files in folders in LOCATIONS_DIR, randomly picks a location that matches the given coordinates, and displays it's images based on the 'actions' array in the config.json file """
	bssids = [network['bssid'].lower() for network in networks]
	ssids = [network['ssid'] for network in networks]
	matching_locations = []
	for subfolder in os.scandir(LOCATIONS_DIR):
		current_location = None
		target_location = None
		radius = None
		actions = None
		matching_ssids = None
		matching_bssids = None
		if os.path.isdir(subfolder.path):
			config_file = os.path.join(subfolder.path, "config.json")
			try:
				with open(config_file, "r") as f:
					config = json.loads(f.read())
				current_location = [{'lat': coordinates[0], 'long': coordinates[1]}]
				target_location = [{'lat': float(config["latitude"]), 'long': float(config["longitude"])}]
				radius = float(config["radius_km"])
				actions = list(config["actions"])
				matching_ssids = [str(ssid) for ssid in list(config["matching_ssids"])]
				matching_bssids = [bssid.lower() for bssid in list(config["matching_bssids"])]
				if (location_in_radius(current_location, target_location, radius) or (set(matching_ssids) & set(ssids)) or (set(matching_bssids) & set(bssids))) and len(actions) > 0:
					matching_locations.append([subfolder.path, actions])
			except Exception as e:
				print(f"Ran into error reading {config_file}:\n{e}")

	if len(matching_locations) <= 0:
		display_unkown_location(epd)
		return

	location = random.choice(matching_locations)
	
	run_actions(epd, location[0], location[1])


def main(epd):

	clear_screen(epd)

	# connect to mobile hotspot
	result, attempts = connect_to_hotspot(epd)
	if result:
		happy_face = random.choice(CONFIG['happy_characters'])
		# if attempts == 0:
		# 	display_text(epd, f"Connected!\n\n{happy_face}", clear=False)
		# else:
		# 	display_text(epd, f"Connected!\n\n{happy_face}", clear=True)
	else:
		sad_face = random.choice(CONFIG['sad_angry_characters'])
		display_text(epd, f"Couldn't connect to the network\nSsid - {CONFIG['mobile_hotspot_ssid']}\nPassword - {CONFIG['mobile_hotspot_password']}\n\n{sad_face}", clear=True)
		sleep(8)
		clear_screen(epd)
		return
	# sleep(1)


	while True:
		coordinates, networks = get_networks_and_coordinates()
		if coordinates is None and networks is None:
			display_unkown_location(epd)
			sleep(8)
			break

		# display_text(epd, f"lat: {coordinates[0]}\nlong: {coordinates[1]}", clear=True)

		clear_screen(epd)
		display_images_by_location(epd, coordinates, networks)

		if not CONFIG["repeat"]:
			break
		sleep(CONFIG["repeat_cooldown"])
		clear_screen(epd)


if __name__ == '__main__':
	try:
		epd = epd2in13_V3.EPD()

		main(epd)

		epd.sleep()
		epd2in13_V3.epdconfig.module_exit(cleanup=True)

	except IOError as e:
		print(e)

	except KeyboardInterrupt:
		# print("ctrl + c:")
		epd2in13_V3.epdconfig.module_exit(cleanup=True)
