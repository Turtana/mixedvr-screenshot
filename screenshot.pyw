import os
import time
import requests
from pathlib import Path

import pyautogui

# Use only if your SteamVR takes broken screenshots.

# I don't take any responsibility of any damages this script may cause.
# I made it for myself and it works on my machine. Be cautious.

# Preconditions:
# pyautogui has to be installed
# SteamVR toolbar box thing can't be minimized
# SteamVR live view has to be open (no need to be active though)
# Your Steam profile has to be public (to get what you're playing through API)

# -- Config -- #
steam_screenshot_folder = "C:\\Program Files (x86)\\Steam\\userdata\\88692041\\760\\remote" # Check this. It probably varies by user.
svr_window_title = "SteamVR-tila" # The window title of SteamVR toolbar thing. Edit according to localization.
svr_view_title = "VR-näkymä" # The window title of SteamVR live view. Edit according to localization.
screenshot_time_buffer = 2 # How many seconds of screenshots you want to overwrite when you take a custom screenshot. DO NOT SET THIS TO A HIGH VALUE.

steam_config_file = open("steamdata.txt")
lines = steam_config_file.readlines()
steam_profile_id = lines[0]
steam_api_key = lines[1]
steam_config_file.close()
# ------------ #

current_game_folder = "\\250820\\screenshots"

def take_screenshot(img_paths):

    # A failsafe in case you're accidentally trying to overwrite your whole screenshot folder.
    # Disable cautiously.
    if len(img_paths) > 10:
        return

    svr_toolbox_array = pyautogui.getWindowsWithTitle(svr_window_title)
    svr_view_array = pyautogui.getWindowsWithTitle(svr_view_title)

    if len(svr_toolbox_array) == 0 or len(svr_view_array) == 0:
        print("Missing critical VR windows")
        return

    svr_toolbox = pyautogui.getWindowsWithTitle(svr_window_title)[0] 

    
    # fullscreens the live view
    svr_view = pyautogui.getWindowsWithTitle(svr_view_title)[0]
    svr_toolbox.minimize()
    try:
        svr_view.activate()
    except:
        svr_view.minimize()
        svr_view.restore()
    pyautogui.press("f11")

    # takes the pic and saves it over all screenshots younger than 5 sec
    time.sleep(.05)
    screenshot = pyautogui.screenshot()
    for path in img_paths:
        screenshot.save(path)

    # returns to the beginning
    pyautogui.press("f11")
    svr_toolbox.maximize()

def vr_is_active():
    window_titles = pyautogui.getWindowsWithTitle("Windows Mixed Reality")
    return len(window_titles) > 0

def get_current_game():
    steamdata = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + steam_api_key + "&steamids=" + steam_profile_id).json()
    gameid = steamdata.get("response").get("players")[0].get("gameid")
    return gameid


# Optimization. If VR is not active, check the situation every 10 seconds instead of 10 times a second. Move to higher frequency if user starts VR
# 10 secs is surely enough to boot up the screenshot service
# TODO: testaa että tää toimii
def vr_watch():
    while True:
        if vr_is_active():
            screenshot_watch()
        time.sleep(10)

def screenshot_watch():
    img_list = list(Path(steam_screenshot_folder + current_game_folder).rglob('*'))
    list_size = len(img_list)

    counter = 0

    while True:
        img_list = list(Path(steam_screenshot_folder + current_game_folder).rglob('*'))

        # detect screenshot taken
        if len(img_list) > list_size:
            list_size = len(img_list)

            img_paths = []
            for img in img_list:
                # overwrites all screenshots taken within the last [screenshot_time_buffer] secs. Can't take just the last one, since Steam generates the thumbnail last
                # skip the stereoscopic pic to avoid duplicates
                if time.time() - os.path.getctime(img) < screenshot_time_buffer and not str(img).__contains__("_vr"):
                    # DANGER!!! Be very careful editing the above condition!
                    # You could end up overwriting YOUR WHOLE SCREENSHOT FOLDER and losing years of video game memories, including non-vr games!
                    # I only realized this afterwards, and it's a small miracle I didn't manage to destroy mine. I added a failsafe but still, be careful.
                    img_paths.append(img)
            take_screenshot(img_paths)

        time.sleep(.1)
        counter += 1

        # check for game every... two seconds? Note that this is an internet request and the program waits for a response.
        if counter % 20 == 0:
            game = get_current_game()
            if game:
                current_game_folder = "\\" + game + "\\screenshots"
            else:
                current_game_folder = "\\250820\\screenshots" # SteamVR folder


        # go back to the "sleep mode"
        if not vr_is_active():
            return

vr_watch()