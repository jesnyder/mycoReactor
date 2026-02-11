import serial
from datetime import datetime

ser = serial.Serial('COM4', 9600)
log_file = "HeaterLog_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

with open(log_file, 'w') as f:
    try:
        while True:
            line = ser.readline().decode().strip()
            timestamped_line = f"{datetime.now().strftime('%H:%M:%S')} | {line}"
            print(timestamped_line)
            f.write(timestamped_line + '\n')
    except KeyboardInterrupt:
        print("Logging stopped")
