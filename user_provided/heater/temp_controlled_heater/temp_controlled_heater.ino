/*
Date: 2026-02-11
Objective: Control an electric heating pad using an SHT30 temperature and humidity sensor.
The Arduino reads the temperature and humidity, controls the heater via a MOSFET, and prints system status.
Target heater temperature is adjustable via the Serial Monitor (e.g., "H 50" sets target to 50°C).
Default target temperature is 40°C.

Hardware Setup:

1. SHT30 Temperature & Humidity Sensor (I2C)
   - Red    -> 5V (VCC)
   - Black  -> GND
   - Yellow -> SCL (Arduino MEGA pin 21)
   - White  -> SDA (Arduino MEGA pin 20)

2. Electric Heating Pad via MOSFET (IRL44N)
   - MOSFET pins facing flat side: left → Gate, middle → Drain, right → Source
   - Gate   -> Arduino pin 9
   - Drain  -> Heater negative (-)
   - Source -> GND
   - Heater positive (+) -> 12V DC Adapter positive
   - 1N4007 diode across heater:
       Cathode (silver band) -> +12V
       Anode -> Heater negative (Drain side)
       Purpose: protects MOSFET from back EMF spikes.

3. Power Supply
   - Alito AC/DC Adapter ALT-1201: 12V DC, 1A for heating pad
   - Arduino powered via USB or separate 5V supply

Libraries to include:
- Wire.h         -> I2C communication
- Adafruit_SHT31.h -> For SHT30 sensor readings
*/

#include <Wire.h>
#include "Adafruit_SHT31.h"

// Create SHT30 object
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// Pin connected to MOSFET gate
const int heaterPin = 9;

// Default target temperature in Celsius
float targetTemp = 40.0;

// Time tracking
unsigned long startMillis;

void setup() {
  Serial.begin(9600);           // Start Serial monitor
  pinMode(heaterPin, OUTPUT);   // Set heater pin as output
  digitalWrite(heaterPin, LOW); // Make sure heater is OFF initially

  // Initialize SHT30 sensor
  if (!sht31.begin(0x44)) {
    Serial.println("Error: SHT30 sensor not found!");
  }

  // Start the elapsed time counter
  startMillis = millis();

  // Optional: Explain startup
  Serial.println("Heating pad control initialized.");
  Serial.print("Default target temperature: "); Serial.print(targetTemp); Serial.println("°C");
}

void loop() {
  // --- Serial input to adjust target temperature ---
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Remove whitespace
    if (cmd.startsWith("H")) {
      float val = cmd.substring(1).toFloat();
      if (val > 0 && val < 100) {
        targetTemp = val;
        Serial.print("Target temperature updated to: "); Serial.print(targetTemp); Serial.println("°C");
      }
    }
  }

  // --- Read SHT30 sensor ---
  float temperature = sht31.readTemperature(); // °C
  float humidity = sht31.readHumidity();       // %

  bool heaterOn = false;

  // --- Heater control logic ---
  if (!isnan(temperature)) {
    if (temperature < targetTemp) {
      digitalWrite(heaterPin, HIGH);
      heaterOn = true;
    } else {
      digitalWrite(heaterPin, LOW);
      heaterOn = false;
    }
  } else {
    // If sensor fails, turn heater off
    digitalWrite(heaterPin, LOW);
    heaterOn = false;
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

  delay(1000); // 1-second loop
}
