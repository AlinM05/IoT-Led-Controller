import time
import network  # type: ignore
import socket
import ujson  # type: ignore
from machine import Pin, PWM  # type: ignore

led = Pin(16, Pin.OUT)

rgb_red = PWM(Pin(17))
rgb_green = PWM(Pin(18))
rgb_blue = PWM(Pin(19))

rgb_red.freq(1000)
rgb_green.freq(1000)
rgb_blue.freq(1000)

feedback = None

def set_rgb_color(hex_color):
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    rgb_red.duty_u16(int(r / 255 * 65535))
    rgb_green.duty_u16(int(g / 255 * 65535))
    rgb_blue.duty_u16(int(b / 255 * 65535))

def get_file(file_name, encoding_type = None):
    try:
        if "json" in file_name:
            with open(file_name, "r", encoding = encoding_type) as secrets:
                file_content = ujson.load(secrets)
            return file_content
        else:
            with open(file_name, "r", encoding = encoding_type) as file:
                file_content = file.read()
            return file_content
    except FileNotFoundError:
        print(f"Error: The file {file_name} was not found.")
        return None
    except IOError as e:
        print(f"Error: Unable to read the file {file_name}. Error: {e}")
        return None

def read_input():
    cl, addr = s.accept()
    print(f"Client connected from {addr}")
    request = cl.recv(1024).decode("utf-8")
    print(f"Request: {request}")
    return cl, request

def process_command(request, feedback):
    command = {}
    if "GET /styles.css" in request:
        command["type"] = "serve_file"
        command["file_type"] = "css"
    elif "GET /script.js" in request:
        command["type"] = "serve_file"
        command["file_type"] = "js"
    elif "GET /" in request:
        command["type"] = "process_ui"
        command["led_on"] = "led=on" in request
        command["led_off"] = "led=off" in request
        if "rgb=" in request:
            rgb_value = request.split("rgb=")[-1][:6]  # Extract HEX color
            command["rgb"] = rgb_value
    else:
        command["type"] = "not_found"
    
    return command

def run_process(command):
    global feedback
    if command["type"] == "serve_file":
        if command["file_type"] == "css":
            cl.send("HTTP/1.0 200 OK\r\nContent-type: text/css\r\n\r\n")
            cl.sendall(css)
        elif command["file_type"] == "js":
            cl.send("HTTP/1.0 200 OK\r\nContent-type: application/javascript\r\n\r\n")
            cl.sendall(script)
    elif command["type"] == "process_ui":
        if command.get("led_on"):
            print("LED ON")
            led.value(1)
            feedback = "LED ON"
        if command.get("led_off"):
            print("LED OFF")
            led.value(0)
            feedback = "LED OFF"
        if command.get("rgb"):
            print(f"Setting RGB LED color to #{command["rgb"]}")
            set_rgb_color(command["rgb"])
            feedback = f"RGB set to #{command["rgb"]}"

        led_state = "OFF" if led.value() == 0 else "ON"
        response = html.format(led_state=led_state)
        cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        cl.sendall(response)
    elif command["type"] == "not_found":
        cl.send("HTTP/1.0 404 Not Found\r\nContent-type: text/plain\r\n\r\n")
        cl.send("404 Not Found")
    cl.close()
    return feedback

json = get_file("connections.json")
if json is not None:
    print("JSON file read successfully")
    ssid = json.get("ssid")
    password = json.get("password")

html = get_file("index.html", "utf-8")
if html is not None:
    print("HTML file read successfully")

css = get_file("styles.css")
if css is not None:
    print("CSS file read successfully")

script = get_file("script.js")
if script is not None:
    print("JavaScript file read successfully")

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print("Waiting for connection...")
    time.sleep(1)
    
if wlan.status() != 3:
    raise RuntimeError("Network connection failed")
else:
    print("Connected")
    status = wlan.ifconfig()
    print(f"IP = {status[0]}")

addr = socket.getaddrinfo("0.0.0.0", 8080)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

while True:
    cl, request = read_input()
    command = process_command(request, feedback)
    feedback = run_process(command) 