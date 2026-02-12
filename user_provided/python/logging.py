"""
Date: 2026-02-11
Objective: Log Arduino heater system status to a file every 10 seconds.
Major Tasks:
1. Open serial connection to Arduino
2. Create a timestamped CSV log file in '../../results/heater'
3. Read system status line from Arduino
4. Parse time elapsed, humidity, temperature, target heater temperature, heater on/off
5. Append parsed data to log file every 10 seconds
6. Print same information to console on one line
"""

import serial
import time
import os
from datetime import datetime

# ==== CONFIG ====
COM_PORT = 'COM5'        # Set your Arduino COM port
BAUD_RATE = 9600
LOG_INTERVAL = 10        # seconds between log entries
LOG_FOLDER = "../../results/heater"

# ==== CREATE LOG FOLDER ====
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Timestamped CSV filename: YYYYMMDDHHMM.csv
log_filename = os.path.join(LOG_FOLDER, f"{datetime.now().strftime('%Y%m%d%H%M')}.csv")

# ==== OPEN SERIAL PORT ====
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
    time.sleep(2)  # allow Arduino to reset
except serial.SerialException as e:
    print(f"Error opening serial port {COM_PORT}: {e}")
    exit()

print(f"Logging started. Data will append to {log_filename}")

# Write CSV header
with open(log_filename, 'a') as f:
    f.write("TimeElapsed,Humidity,Temperature,Target,Heater\n")

start_time = time.time()

try:
    while True:
        # --- Time elapsed ---
        elapsed = int(time.time() - start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        # --- Read line from Arduino ---
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        # Expected Arduino output format:
        # 00:00:05 | Humidity: 45.2% | Temp: 38.6°C | Target: 40.0°C | Heater: ON
        if line:
            try:
                parts = [p.strip() for p in line.split('|')]
                humidity = parts[1].split()[1].replace('%','')
                temp = parts[2].split()[1].replace('°C','')
                target = parts[3].split()[1].replace('°C','')
                heater = parts[4].split()[1]
            except (IndexError, ValueError):
                humidity = temp = target = heater = 'NAN'
        else:
            humidity = temp = target = heater = 'NAN'

        # --- Build CSV line ---
        log_line = f"{time_str},{humidity},{temp},{target},{heater}\n"

        # --- Append to file ---
        with open(log_filename, 'a') as f:
            f.write(log_line)

        # --- Print to console ---
        print(f"{time_str} | Humidity: {humidity}% | Temp: {temp}°C | Target: {target}°C | Heater: {heater}")

        # --- Wait before next log ---
        time.sleep(LOG_INTERVAL)

except KeyboardInterrupt:
    print("\nLogging stopped by user.")

finally:
    ser.close()
