/***************************************************************
  Project: Heater Control System with SHT30 Sensor
  Date: 2026-02-11

  Objective:
  Control a 12V heating pad using an Arduino MEGA 2560
  and IRLZ44N MOSFET. Maintain 40°C (default).
  Target temperature adjustable via Serial:
      H 50   -> sets target to 50°C

  System status prints on ONE LINE including:
    Time (HH:MM:SS)
    Humidity (%)
    Temperature (°C)
    Target Temperature (°C)
    Heater ON/OFF

  Required Libraries:
    - Wire
    - Adafruit_SHT31
    - Adafruit_BusIO

  MOSFET Wiring (IRLZ44N - flat side facing you):
    Left  = Gate   -> Arduino Pin 8 (220Ω resistor recommended)
    Middle= Drain  -> Heating pad negative
    Right = Source -> Ground
    Metal tab = Drain

***************************************************************/

#include <Wire.h>
#include <Adafruit_SHT31.h>

#define HEATER_PIN 8

Adafruit_SHT31 sht30 = Adafruit_SHT31();

float targetTemperature = 40.0;
float currentTemperature = NAN;
float currentHumidity = NAN;
