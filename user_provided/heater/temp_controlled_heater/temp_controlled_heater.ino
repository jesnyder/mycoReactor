/***************************************************************
  Project: Heater Control System with Optional SHT30 Sensor
  Date: 2026-02-11

  Objective:
  Control a 12V heating pad using an Arduino MEGA 2560 and
  IRLZ44N MOSFET. Monitor temperature and humidity using
  an SHT30 sensor (optional). Maintain a target temperature
  of 40°C (default), adjustable via Serial command:
      Example:  H 50
  Logs system status including:
    - Elapsed Time (HH:MM:SS)
    - Temperature (°C)
    - Humidity (%)
    - Target Temperature (°C)
    - Heater ON/OFF state

  If the SHT30 fails or is disconnected:
    - Temperature and humidity are logged as NAN
    - Heater control is disabled

  MOSFET + Diode Wiring Summary:
  --------------------------------
  The IRLZ44N MOSFET acts as a low-side switch:
    Gate  -> Arduino digital pin (through 220Ω resistor recommended)
    Drain -> Heating pad negative
    Source -> Ground

  Heating pad positive -> +12V power supply

  1N4007 Diode:
    Cathode (silver band) -> +12V
    Anode -> MOSFET Drain
  This protects against voltage spikes.

***************************************************************/

#include <Wire.h>
#include <Adafruit_SHT31.h>

// ---------------- PIN DEFINITIONS ----------------
#define HEATER_PIN 8   // MOSFET Gate control pin

// ---------------- GLOBAL VARIABLES ----------------
Adafruit_SHT31 sht30 = Adafruit_SHT31();

float targetTemperature = 40.0;  // Default target temp (°C)
float currentTemperature = NAN;
float currentHumidity = NAN;

bool heaterState = false;
bool sensorAvailable = false;

unsigned long startTime;

// --------------------------------------------------

void setup() {
  Serial.begin(9600);
  pinMode(HEATER_PIN, OUTPUT);
  digitalWrite(HEATER_PIN, LOW);

  startTime = millis();

  Serial.println("Heater Control System Initializing...");

  if (sht30.begin(0x44)) {   // Default I2C address
    sensorAvailable = true;
    Serial.println("SHT30 sensor detected.");
  } else {
    sensorAvailable = false;
    Serial.println("SHT30 sensor NOT detected. Running without temperature control.");
  }
}

// --------------------------------------------------

void loop() {

  readSensor();
  controlHeater();
  readSerialCommands();
  printStatus();

  delay(2000);  // Update every 2 seconds
}

// --------------------------------------------------

void readSensor() {
  if (sensorAvailable) {
    currentTemperature = sht30.readTemperature();
    currentHumidity = sht30.readHumidity();

    if (isnan(currentTemperature) || isnan(currentHumidity)) {
      currentTemperature = NAN;
      currentHumidity = NAN;
    }
  } else {
    currentTemperature = NAN;
    currentHumidity = NAN;
  }
}

// --------------------------------------------------

void controlHeater() {

  if (!isnan(currentTemperature)) {
    if (currentTemperature < targetTemperature) {
      digitalWrite(HEATER_PIN, HIGH);
      heaterState = true;
    } else {
      digitalWrite(HEATER_PIN, LOW);
      heaterState = false;
    }
  } else {
    // Disable heater if no valid temperature
    digitalWrite(HEATER_PIN, LOW);
    heaterState = false;
  }
}

// --------------------------------------------------

void readSerialCommands() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("H")) {
      float newTemp = input.substring(1).toFloat();
      if (newTemp > 0 && newTemp < 100) {
        targetTemperature = newTemp;
        Serial.print("New target temperature set to: ");
        Serial.println(targetTemperature);
      }
    }
  }
}

// --------------------------------------------------

void printStatus() {

  unsigned long elapsedMillis = millis() - startTime;
  unsigned long seconds = elapsedMillis / 1000;
  unsigned int hours = seconds / 3600;
  unsigned int minutes = (seconds % 3600) / 60;
  unsigned int secs = seconds % 60;

  Serial.println("--------------------------------------------------");

  Serial.print("Time Elapsed: ");
  Serial.print(hours);
  Serial.print("h : ");
  Serial.print(minutes);
  Serial.print("m : ");
  Serial.print(secs);
  Serial.println("s");

  Serial.print("Temperature: ");
  Serial.print(currentTemperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(currentHumidity);
  Serial.println(" %");

  Serial.print("Target Temperature: ");
  Serial.print(targetTemperature);
  Serial.println(" °C");

  Serial.print("Heater State: ");
  if (heaterState)
    Serial.println("ON");
  else
    Serial.println("OFF");

  Serial.println("--------------------------------------------------");
}
