# import machine
# import urequests as requests
# import random
# import time
# import datetime
# import network
# import gc
# import json
# import mysql.connector
# import os


# SERVER_URL = "https://ecstacy.pythonanywhere.com/api/update-dht-data"
# uart = machine.UART(1, baudrate=9600, tx=17, rx=16)

# db = mysql.connector.connect(
#     host="#yourhost",
#     user="#username",
#     password="#yourpassword"
# )

# cur = db.cursor()

# cur.execute("CREATE DATABASE IF NOT EXISTS powermonitor")
# cur.execute("USE powermonitor")
# cur.execute("""
#     CREATE TABLE IF NOT EXISTS data(
#         ID INT AUTO_INCREMENT PRIMARY KEY,
#         date DATE,
#         day VARCHAR(10),
#         time TIME,
#         Voltage_V INT,
#         Current_I INT,
#         Power_W INT
#     )
# """)
# def sendmessage(mes , no):
#     try:
#         api_url = "https://api.callmebot.com/whatsapp.php"
#         payload ={
#             "phone": no,
#             "text": mes,
#             "apike": "3yourapikey" 
#         }
#         response = requests.post(api_url, params=payload)

#         if response.status_code == 200:
#             print("Message sent successfully!")
#         else:
#             print("Failed to send message. Error:", response.text)
#     except Exception as e:
#             print("Failed to send message, Try again!", str(e))
  
        
# def add_data(Voltage,Current,Power):
#     current_datetime = datetime.datetime.now()
#     date = current_datetime.date()
#     day = current_datetime.strftime("%A")
#     time = current_datetime.strftime("%H:%M:%S")
#     cur.execute("""
#         INSERT INTO data (date, day, time, Voltage_V, Current_I, Power_W)
#         VALUES (%s, %s, %s, %s, %s, %s)
#     """, (date, day, time, voltage, current, power))
#     db.commit()

# def sensor_data():
   
#     return {"Voltage": voltage, "Current": current}


# def connect_wifi(ssid, password):
#     station = network.WLAN(network.STA_IF)
#     station.active(True)
#     station.connect(ssid, password)
#     while not station.isconnected():
#         pass
#     print('Connection successful')
#     print(station.ifconfig())

# connect_wifi("<your SSID>","<<Password>>")

# def process_uart_data(data):
#     try:
#         data_dict = json.loads(data)
#         return data_dict
#     except ValueError as e:
#         print("Error decoding JSON:", e)
#         return None

# def send_data_to_server(data):
#     global SERVER_URL
#     try:
#         response = requests.post(SERVER_URL, json=data)
#         if response.status_code == 200:
#             print("Data sent successfully to the server.")
#         else:
#             print("Failed to send data to the server. Status code:", response.status_code)
#         response.close() 
#     except Exception as e:
#         print("Error occurred while sending data to the server:", str(e))

# if __name__ == "__main__":
#     while True:
#         try:
#             if uart.any():
#                 data = uart.readline().decode('utf-8').strip()  # Strip whitespace characters
#                 data_dict = process_uart_data(data)
#                 if data_dict is not None:
#                     voltage = data_dict.get("Voltage")
#                     current_str = data_dict.get("Current")
#                     if voltage is not None and current_str is not None:
#                         try:
#                             current = float(current_str) / 1000  # Convert current to amperes
#                             current = '{:.2f}'.format(current)  # Format current
#                             power = voltage* current
#                             if power >= 100:
#                                 sendmessage(f"Alert Power Exceeded {power} W !!", "<<Your phone number>>")
#                             add_data(voltage,current,power)
#                             data = {"Voltage": voltage, "Current": current}
#                             send_data_to_server(data)
#                             gc.collect()
#                         except ValueError:
#                             print("Invalid current value:", current_str)
#                     else:
#                         print("Invalid data format:", data)
#                 else:
#                     print("Invalid JSON syntax:", data)
#             time.sleep(1.5)
#         except KeyboardInterrupt:
#             break

# network.WLAN(network.STA_IF).disconnect()


import machine
import urequests as requests
import time
import datetime
import network
import json
import mysql.connector

uart = machine.UART(1, baudrate=9600, tx=17, rx=16)

# MySQL connection
db = mysql.connector.connect(
    host="yourhost",
    user="yourusername",
    password="yourpassword"
)

cur = db.cursor()

# Create DB + Table
cur.execute("CREATE DATABASE IF NOT EXISTS powermonitor")
cur.execute("USE powermonitor")

cur.execute("""
    CREATE TABLE IF NOT EXISTS data(
        ID INT AUTO_INCREMENT PRIMARY KEY,
        date DATE,
        day VARCHAR(10),
        time TIME,
        Voltage_V FLOAT,
        Current_I FLOAT,
        Power_W FLOAT
    )
""")

# WhatsApp alert function
def sendmessage(mes, no):
    try:
        api_url = "https://api.callmebot.com/whatsapp.php"
        payload = {
            "phone": no,
            "text": mes,
            "apikey": "your_api_key"
        }
        response = requests.post(api_url, params=payload)

        print("Message sent!" if response.status_code == 200 else "Failed:", response.text)

    except Exception as e:
        print("Message send error:", e)

# Insert values into MySQL
def add_data(Voltage, Current, Power):
    now = datetime.datetime.now()
    date = now.date()
    day = now.strftime("%A")
    t = now.strftime("%H:%M:%S")

    cur.execute("""
        INSERT INTO data (date, day, time, Voltage_V, Current_I, Power_W)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (date, day, t, Voltage, Current, Power))

    db.commit()

# Power threshold alert
POWER_LIMIT = 1500   # Example 1500W load limit
alert_sent = False

print("ESP32 Monitoring Started...")

while True:
    if uart.any():
        try:
            raw = uart.readline().decode().strip()
            print("Received:", raw)

            data = json.loads(raw)
            voltage = float(data["Voltage"])
            current = float(data["Current"])
            power = voltage * current

            print("V:", voltage, "I:", current, "P:", power)

            add_data(voltage, current, power)

            # Alert logic
            global alert_sent
            if power > POWER_LIMIT and not alert_sent:
                sendmessage(f"⚠️ High Power Alert!\nLoad consuming: {power:.2f}W", "your_number")
                alert_sent = True

            if power < POWER_LIMIT and alert_sent:
                alert_sent = False  # Reset when load normalizes

        except Exception as e:
            print("Error:", e)

    time.sleep(1)

