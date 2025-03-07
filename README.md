# The Com-Pi-nion
In this project we will use the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) and the [`2.13 inch E-ink disaply HAT`](https://www.waveshare.com/2.13inch-e-paper-hat.htm) to display images in a "stop motion like manner", creating the illusion of a video.  
The "videos" which are displayed are chosen based on the current location of the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/).  
To discover the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/)'s location without attaching a GPS to it, we scan nearby WiFi networks, and use [this repo](https://github.com/jakored1/bssid_locator) to discover our location with Apple's Geo-Location services.  
To access Apple's Geo-Location services, the Raspberry Pi will have to be connected to a predetermined WiFi network, which in our case will be a mobile hotspot network.  
This might sound like a lot, but it isn't!  
Just follow along :)  
  
## Requirements  
- [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/)  
- [`2.13 inch E-ink disaply HAT`](https://www.waveshare.com/2.13inch-e-paper-hat.htm)  
- (optional) [`Battery for Raspberry Pi Zero`](https://www.tindie.com/products/pisugar/pisugar-2-battery-for-raspberry-pi-zero/)  
- (optional) A friend with a 3D printer, so you can place everything in a small 3D printed case, and hang it on a keychain (just an idea).  
  
## Demo  
https://github.com/jakored1/com-pi-nion/blob/main/demo.mp4
  
## Setup  
The setup starts assuming that you have a fresh installation of the `Raspberry Pi OS Lite (32-bit)` on your [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/), and that you have connected the [`2.13 inch E-ink disaply HAT`](https://www.waveshare.com/2.13inch-e-paper-hat.htm) to it.  
Connect to your [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) however you like, and begin the setup!  
##### If you already know how the project works, or don't care for the details, skip to the [usage](#usage) area.
  
## Installations  
Lets follow the [setup on the waveshare website](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_Manual#Overview) to set up our [`2.13 inch E-ink disaply HAT`](https://www.waveshare.com/2.13inch-e-paper-hat.htm) with the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/).  
First, enable SPI:  
```bash  
sudo raspi-config  
# Choose Interfacing Options --> SPI --> Yes Enable SPI interface  
```  
Then install the required packages:  
```bash  
sudo apt-get update  
sudo apt-get install -y python3-pip git python3-pil python3-spidev python3-rpi.gpio  
```  
Create a directory to hold our project:  
```bash  
sudo mkdir /opt/e-ink_displayer  
sudo chown $USER:$USER /opt/e-ink_displayer  
```  
Now that everything is installed lets try and run the provided demo to ensure that the [`2.13 inch E-ink disaply HAT`](https://www.waveshare.com/2.13inch-e-paper-hat.htm) works:  
```bash  
cd /opt/e-ink_displayer  
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
rm E-Paper_code.zip
cd e-Paper/RaspberryPi_JetsonNano/python/examples/
python3 epd_2in13_V3_test.py
```  
If the demo is working, you should see the screen react and display a bunch of stuff.  
If for some reason it isn't working for you, make sure you are using the same screen I have mentioned throughout. If it isn't exactly the same, you still might be good!  
Check the `/opt/e-ink_displayer/e-Paper/RaspberryPi_JetsonNano/python/examples/` directory and see if there is a script for the display you have.  
Notice, that if you have a different display, you might need to slightly modify some of the code we use later on.  
  
Awesome! now that everything is working, let's display our own images.  

## Displaying Images  
So, now we would like to display our own images.  
To do this, the first thing we need to know, is what resolution should our images be so that they are properly displayed on the e-ink paper?  
According to the [manual](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_Manual#Parameters), the resolution of our device is `250 × 122`.  
Great!  
Now create 2 images/drawings, and make sure they are in a `.bmp` format, as this is what the e-ink display requires.  
You can use free photo editing software, or animation/drawing software to create your own `.bmp` images. Or you could convert images in other formats to `.bmp` online.  
  
Once we have our images, name them `image1.bmp` and `image2.bmp` and place them in the `/opt/e-ink_displayer/images` directory:  
```bash  
mkdir /opt/e-ink_displayer/images
mv image1.bmp image2.bmp /opt/e-ink_displayer/images

ls -l /opt/e-ink_displayer/images
# Output
# image1.bmp
# image2.bmp
```  
Now we will use this script to iterate over the images and display them:  
```python  
#!/usr/bin/python

import os
import sys
SRCDIR = "/opt/e-ink_displayer/e-Paper/RaspberryPi_JetsonNano/python"
sys.path.append(os.path.join(SRCDIR, "lib"))
from PIL import Image, ImageDraw, ImageFont
import socket
import warnings
import time
from waveshare_epd import epd2in13_V3

PICDIR = "/opt/e-ink_displayer/images"

try:
    print("starting epd2in13_V3")
    
    epd = epd2in13_V3.EPD()
    print("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    # read bmp file 
    print("read bmp file...")
    image = Image.open(os.path.join(PICDIR, 'image1.bmp'))
    epd.display(epd.getbuffer(image))
    time.sleep(0.5)

    for i in range(1,5):
        print("read 2nd bmp file...")
        image = Image.open(os.path.join(PICDIR, 'image2.bmp'))
        epd.displayPartial(epd.getbuffer(image))
        time.sleep(0.5)

        image = Image.open(os.path.join(PICDIR, 'image1.bmp'))
        epd.displayPartial(epd.getbuffer(image))
        time.sleep(0.5)
        
    print("Goto Sleep...")
    epd.sleep()

    epd2in13_V3.epdconfig.module_exit(cleanup=True)    

except IOError as e:
    print(e)
    
except KeyboardInterrupt:    
    print("ctrl + c:")
    epd2in13_V3.epdconfig.module_exit(cleanup=True)
    exit()
```  
This script clears the screen, and iterates between the images `image1.bmp` and `image2.bmp`.  
Notice that at the beginning we use `epd.display` to display the image, but later we use `epd.displayPartial`.  
This is because `epd.display` properly clears the screen before displaying an image, and `epd.displayPartial` doesn't.  
Using `epd.display` will result in a clear image with no "previous image residue", but will take longer and flash the screen.  
Using `epd.displayPartial` simply writes the image to the screen, without properly cleaning it first. The side effect is that you might have some "previous image residue", but at least the image is immediately displayed - which is what we need to create a "smooth" video.  
  
Run the script on your [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) to make sure it works:  
```bash  
python3 ~/test_script.py
```  
Hopefully everything worked, and the images you created were displayed on the screen.  
  
So now we know how to "create a video".  
In the next part, we'll understand how to have the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) discover it's location, so we can display different images accordingly.  
  
## Discovering Our Location  
So, how are we going to discover the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/)'s location?  
Glad you asked!  
To find where the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) is located, we will use it's wifi capabilities to scan the wifi networks near us, and then use Apple's Geo-Location services to discover where the networks we scan are located, thus allowing us to discover approximately where the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) is.  
We will use [this repo](https://github.com/jakored1/bssid_locator) to interact with the Apple Geo-Location services.  
We will also check if our latitude and longitude are inside a predetermined polygon.  
Below is a script you can use to test the functionality and make sure it works.  
In the final product we will implement this a bit differently, but using the same [repo](https://github.com/jakored1/bssid_locator) and scanning command.  
Before running the script we need to clone [the repo](https://github.com/jakored1/bssid_locator) and install requirements:  
```bash  
# Clone repo
sudo git clone https://github.com/jakored1/bssid_locator.git /opt/bssid_locator
sudo chown -R $USER:$USER /opt/bssid_locator
# Remove unnecessary files
rm /opt/bssid_locator/Dockerfile /opt/bssid_locator/README.md
# Install requirements
sudo apt install -y python3-full python3-protobuf python3-pycurl
```  
To test it works, scan the networks near you `sudo iwlist wlan0 scan`, and the run the script `python3 /opt/bssid_locator/main.py <BSSID>`.  
  
Now run this script below (notice to change `target_location` and `radius` as needed, if you want):  
```python  
#!/usr/bin/env python

import os
import re
import json
from math import radians, cos, sin, asin, sqrt

print("Scanning for networks...")
output = os.popen("sudo iwlist wlan0 scan").read()
print("Parsing network scan result...")
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

# If we didn't scan any networks
if len(networks) < 1:
    print("There are no Wifi networks near you")
    exit()

# Printing for testing :)
print("Found Networks:")
for network in networks:
    print(f"-\t{network['bssid']} | {network['rssi']} | {network['ssid']}")

# Fetching the BSSID of the best scanned network and finding it's location
attempted_networks = []
location = "latitude/longitude"
while True:
    best_network = ""
    best_rssi = -200
    if len(attempted_networks) == len(networks):
        print("Couldn't locate any of the networks near you")
        exit()
        break
    for network in networks:
        if (network['rssi'] > best_rssi) and (network['bssid'] not in attempted_networks):
            best_network = network['bssid']
            best_rssi = network['rssi']
    # Trying to find the networks location
    try:
        print(f"Attempting to get location of {best_network}")
        # output = os.popen(f"docker run --rm bssid_locator {best_network}").read()
        output = os.popen(f"python3 /opt/bssid_locator/main.py {best_network}").read()
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

print("\nBest scanned network")
print(f"BSSID -                  {best_network}")
print(f"RSSI  -                  {best_rssi}")
print(f"Coordinates (lat/long) - {location[0]},{location[1]}")


# Check if the network we scanned is in an X radius distance from the target location
# If you want to test this part I suggest you replace the target_location with your current location
# To get coordinates for a location just open google maps and right click on a point on the map
# Use this site to see radius around coordinates --> https://www.freemaptools.com/radius-around-point.htm
# Based on this --> https://stackoverflow.com/questions/42686300/how-to-check-if-coordinate-inside-certain-area-python
target_location = [{'lat': -7.7940023, 'long': 110.3656535}]
current_location = [{'lat': location[0], 'long': location[1]}]

lat1 = target_location[0]['lat']
lon1 = target_location[0]['long']
lat2 = current_location[0]['lat']
lon2 = current_location[0]['long']

radius = 1.00 # in kilometer

# convert decimal degrees to radians 
lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

# haversine formula 
dlon = lon2 - lon1 
dlat = lat2 - lat1 
a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
c = 2 * asin(sqrt(a)) 
r = 6371 # Radius of earth in kilometers. Use 3956 for miles
distance = c * r

print('\nDistance (km) : ', distance)
if distance <= radius:
    print('Inside target_location')
else:
    print('Outside target_location')
```  
  
## Connecting To Networks  
The final thing we need to implement, is how to programmatically connect to a wifi network in python (we need this to connect to the predetermined mobile hotspot, so we are able to access the internet, in order to access Apple's Geo-Location services).  
To do this in the script we are going to use `nmcli` (NetworkManager CLI).  
This script will connect the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) to a wifi network:  
```python  
#!/usr/bin/env python

import os
from time import sleep

ssid = "wifi_network"  # no spaces
password = "supersecurepassword"
test_internet_with = [
    {
        "host": "https://duckduckgo.com/",
        "expected_status": 200,
        "user_agent": "Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36"
    },
    {
        "host": "https://google.com",
        "expected_status": 200,
        "user_agent": "Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36"
    },
    {
        "host": "https://www.bing.com",
        "expected_status": 200,
        "user_agent": "Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36"
    }
]


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
    output = os.popen(f"nmcli device wifi connect {ssid} password {password}").read()
    sleep(2)
    # Check if we are connected to the wifi network
    for website in test_internet_with:
        try:
            url = website["host"]
            expected_status_code = website["expected_status"]
            user_agent = website["user_agent"]
            r = get(url,
                headers={'User-Agent': user_agent},
                timeout=10
            )
            if expected_status_code == r.status_code:
                print("Connected to the internet!")
                break
        except Exception as e:
            print(e)
    cnt += 1
    if cnt > 10:
        print("Couldn't connect to wifi network (couldn't access the internet)")
        break
```  
  
That's it!  
Now we know how this project works.  
The next step is to setup your own version (follow instructions bellow)  
  
## Usage  
The setup starts assuming that you have a fresh installation of the `Raspberry Pi OS Lite (32-bit)` on your [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/), and that you have connected the [`2.13 inch E-ink disaply HAT`](https://www.waveshare.com/2.13inch-e-paper-hat.htm) to it.  
Connect to your [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) however you like, and begin the setup!  
  
These are the commands to run on the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) to set this project up:  
```bash  
# Enable SPI
sudo raspi-config  
# Choose Interfacing Options --> SPI --> Yes Enable SPI interface  

# Install requirements
sudo apt-get update  
sudo apt-get install -y git python3-pip python3-pil python3-spidev python3-rpi.gpio python3-full python3-protobuf python3-pycurl python3-requests  

# Clone repo 
cd /opt
sudo git clone https://github.com/jakored1/com-pi-nion.git
sudo chown -R $USER:$USER /opt/com-pi-nion
rm /opt/com-pi-nion/demo.mp4 

# Fetch e-paper display library
cd /opt/com-pi-nion
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
rm E-Paper_code.zip

# Clone bssid locator repo
cd /opt/com-pi-nion
git clone https://github.com/jakored1/bssid_locator.git
```  
Now you can populate the `/opt/com-pi-nion/images/` directory with your own animations for `locations` and `unkown_location`s.  
Available actions for the `config.json` and `actions.json` files to display the images in the `locations` and `unkown_location` directories are:  
- `clear` - clears the screen  
- `display image <IMAGE>.bmp` - fully clear screen and display image  
- `displayPartial image <IMAGE>.bmp` - display image without fully clearing screen  
- `display message <TEXT_MESSAGE>` - fully clear screen and display a text message at the center of the screen  
- `display messageBold <TEXT_MESSAGE>` - fully clear screen and display a bold text message at the center of the screen  
- `displayPartial message <TEXT_MESSAGE>` - display text message at the center of the screen without fully clearing screen  
- `displayPartial messageBold <TEXT_MESSAGE>` - display text message at the center of the screen without fully clearing screen  
- `sleep X` - wait X seconds before moving to next action  
  
Tips:  
- It is not required to run `clear` as the first action, the screen is cleared before iterating over the actions.  
- Don't run `displayPartial` and then `display` directly after. If you want to run `displayPartial` and then `display`, you should add a `clear` after the `displayPartial` or the `display` might not work properly.  
  
Usefull script to convert images to .bmp format:  
```python  
from PIL import Image
src_img_path = "image.png"
dst_img_path = "image.bmp"
img = Image.open(src_img_path)
img.save(dst_img_path)
```  
To make sure you config.json file is valid, run this on it:  
```python  
import json
json.loads("config.json")
```  
If this doesn't produce an error than the json is valid.  
Finally, you can use the `test_animation.py` script to test your animations.  
Give it a folder as an argument and it will look for a `actions.json` or `config.json` and run the actions:  
```bash  
cd /opt/com-pi-nion/
python test_animation.py /opt/com-pi-nion/images/locations/big_ben/
```  
  
Next, you might want to modify the `/opt/com-pi-nion/global_config.json` file.  
Most of the configuration options are self-explanitory, but here are some worth mentioning:  
- `wifi_interface` - The wifi interface on the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) through which it connects to the mobile hotspot  
- `mobile_hotspot_ssid` - The SSID (name) of the mobile hotspot network the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) will attempt to connect to  
- `mobile_hotspot_password` - The password of the mobile hotspot network the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) will attempt to connect to  
- `base_dir` - The base directory of the project. If you followed the above setup and didn't move anything around than this should be left as is  
- `display_bssids` - Whether or not to display the BSSIDs that are being scanned to the user. Enabling this can be usefull for debugging  
- `repeat` - If set to true, the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) will rerun the script endlessly until turned off. This can be nice if you have a bunch of animations for the same location and want them to be displayed over time  
- `repeat_cooldown` - How long to wait before re-running the script  
- `test_internet_with` - This is an array of websites that is used by the script to make sure it has internet. You can edit or add your own. The script will make a GET request to the given url (`host`), with the given user agent (`user_agent`), and asume there is a valid internet connection if the response returns the given status code (`expected_status`)  
  
After you set everything up, you will probably want to make this whole thing into a service so that it runs every time the [`Raspberry Pi Zero W`](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) boots up:  
```bash  
# create service
sudo cat <<EOF > /etc/systemd/system/com-pi-nion.service
[Unit]
Description=Run com-pi-nion on startup after NetworkManager is running
After=network.target NetworkManager.service

[Service]
WorkingDirectory=/opt/com-pi-nion/
ExecStart=/usr/bin/python3 /opt/com-pi-nion/main.py
Type=oneshot
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF

# reload systemd
sudo systemctl daemon-reload

# enable service so it runs on startup
sudo systemctl enable com-pi-nion.service

# start service to test and see it works
sudo systemctl start com-pi-nion.service

# check service status
sudo systemctl status com-pi-nion.service

# if something isn't working add prints and use journalctl to see whats going on
journalctl -u com-pi-nion.service
```  
  
And that's it!  
Enjoy :)  
