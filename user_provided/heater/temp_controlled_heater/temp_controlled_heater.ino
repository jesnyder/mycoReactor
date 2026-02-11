/*
Date: 2026-02-11
Objective: Control a heating pad using SHT30 temperature sensor.
The Arduino reads temperature and humidity, controls the heater via MOSFET, and prints system status.
The target heater temperature is adjustable via Serial commands (e.g., "H 50" sets target to 50°C).

Hardware Setup:

1. SHT30 Sensor (I2C)
   - Red    -> 5V
   - Black  -> GND
   - Yellow -> SCL (Mega pin 21)
   - White  -> SDA (Mega pin 20)

2. Heating Pad via MOSFET (IRL44N)
   - Gate   -> Arduino pin 9
   - Drain  -> Heating pad negative (-)
   - Source -> GND
   - Heating pad positive (+) -> 12V DC adapter positive
   - 1N4007 diode across heating pad: Cathode (silver band) to +12V, Anode to - (drain side)
     Purpose: protects MOSFET from back EMF.

3. Power Supply
   - Alito AC/DC Adapter ALT-1201: 12V DC, 1A for heating pad
   - Arduino powered via USB or separate 5V supply

Libraries:
   - Wire.h (I2C communication)
   - Adafruit_SHT31.h (SHT30 sensor)

*/

#include <Wire.h>
#include "Adafruit_SHT31.h"

Adafruit_SHT31 sht31 = Adafruit_SHT31();

const int heaterPin = 9;        // Arduino pin connected to MOSFET gate
float targetTemp = 50.0;        // Default target temperature (°C)

unsigned long startMillis;       // Track elapsed time

void setup() {
  Serial.begin(9600);
  pinMode(heaterPin, OUTPUT);
  digitalWrite(heaterPin, LOW); // Heater off initially

  if (!sht31.begin(0x44)) {
    Serial.println("SHT30 sensor not found!");
  }

  startMillis = millis(); // Start time counter
}

void loop() {
  // --- Handle Serial input for adjusting target temperature ---
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Remove whitespace
    if (cmd.startsWith("H")) {
      float val = cmd.substring(1).toFloat();
      if (val > 0 && val < 100) {
        targetTemp = val;
      }
    }
  }

  // --- Read SHT30 sensor ---
  float temperature = sht31.readTemperature(); // °C
  float humidity = sht31.readHumidity();       // %

  bool heaterOn = false;

  if (!isnan(temperature)) {
    // --- Heater control logic ---
    if (temperature < targetTemp) {
      digitalWrite(heaterPin, HIGH);
      heaterOn = true;
    } else {
      digitalWrite(heaterPin, LOW);
      heaterOn = false;
    }
  }

  // --- Compute elapsed time ---
  unsigned long elapsed = (millis() - startMillis) / 1000;
  unsigned int hours = elapsed / 3600;
  unsigned int minutes = (elapsed % 3600) / 60;
  unsigned int seconds = elapsed % 60;

  // --- Print system status on one line ---
  Serial.print(hours); Serial.print(":");
  if (minutes < 10) Serial.print("0");
  Serial.print(minutes); Serial.print(":");
  if (seconds < 10) Serial.print("0");
  Serial.print(seconds); Serial.print(" | ");

  Serial.print("Humidity: ");
  Serial.print(isnan(humidity) ? -1 : humidity, 1);
  Serial.print("% | Temp: ");
  Serial.print(isnan(temperature) ? -1 : temperature, 1);
  Serial.print("°C | Target: ");
  Serial.print(targetTemp, 1);
  Serial.print("°C | Heater: ");
  Serial.println(heaterOn ? "ON" : "OFF");

  delay(1000); // 1-second loop for readability
}
