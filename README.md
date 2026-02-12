# mycoReactor

# About

**Repo Name:** mycoReactor

## Objective
Control and monitor a heating pad system for precise temperature regulation using an Arduino, SHT30 temperature/humidity sensor, and MOSFET. Data is logged and visualized to optimize heater performance.

## Major Tasks
1. Read temperature and humidity from the SHT30 sensor.
2. Control a heating pad via IRL44N MOSFET based on target temperature.
3. Log system status to timestamped CSV files every 10 seconds.
4. Generate interactive web-based plots of temperature and humidity over time.

## Tools Used
- Arduino (Mega/Uno)
- SHT30 I2C temperature & humidity sensor
- IRL44N N-channel MOSFET
- Python (logging and website generation)
- Plotly.js for interactive plotting
- HTML/CSS/JavaScript for the dashboard

## More Information
For detailed instructions, plots, and additional documentation, visit the project website:  
[https://jesnyder.github.io/mycoReactor/](https://jesnyder.github.io/mycoReactor/)


# Lessons Learned from the MycoReactor Heater Project

1. **Double-check pin assignments on the Arduino**
   - Always confirm which Arduino pin is connected to the MOSFET gate.
   - Using the wrong pin can prevent control signals from reaching the MOSFET or, worse, fry components.

2. **Understand the MOSFET pinout**
   - The IRL44N (and similar MOSFETs) has **Gate (G), Drain (D), Source (S)**.
   - On most IRL44N packages (TO-220 or similar), looking at the **front (text side)**, left to right is **Gate → Drain → Source**.
   - Misidentifying pins can make the heater permanently on or prevent it from turning on.

   The IRL44N (Allecin) diagram: https://www.icdrex.com/introducing-the-irlz44n-complete-guide-features-and-applications/

3. **Always connect a common ground**
   - The Arduino ground and the heater/MOSFET ground **must be connected**.
   - Without a shared reference, the MOSFET cannot properly switch, leading to erratic behavior.

4. **Diode placement matters**
   - A flyback diode (e.g., 1N4007) is needed **across the load**, not the MOSFET.
   - The **cathode (silver band) goes to the positive voltage**, and the anode goes to the MOSFET drain/negative side of the heating pad.
   - This protects the MOSFET from voltage spikes caused by inductive loads or sudden heater disconnection.

5. **Check voltage ratings of components**
   - Make sure the MOSFET and diode are rated for the heater voltage and current.
   - Using components rated too low can cause permanent damage.

6. **Test with low power first**
   - Before applying full 12V, test control logic with small loads or an LED.
   - This prevents frying MOSFETs or other components if wiring is incorrect.

7. **Thermal lag is normal**
   - The temperature sensor reacts to the environment, not instantly to heater changes.
   - Expect some overshoot and lag — it’s normal for bang-bang controllers.

8. **Serial commands are useful for dynamic adjustment**
   - Being able to set target temperature via the Serial Monitor allows safe testing without reprogramming.
   - Example: `"H 50"` sets the target to 50°C.

9. **Document wiring clearly**
   - Diagrams and text notes prevent mistakes.
   - Label wires: SHT30 (VCC, GND, SCL, SDA), MOSFET (G, D, S), heater (+, -), diode.

10. **Keep spares of sensitive components**
    - MOSFETs and diodes can fry if wired incorrectly.
    - Having replacements prevents long downtime.
