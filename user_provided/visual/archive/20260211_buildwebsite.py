import os
import csv
import json
from datetime import datetime

# ==== CONFIG ====
HEATER_FOLDER = "../../results/heater"
JS_FOLDER = "../../docs/js"
INDEX_HTML = "../../docs/index.html"

# ==== ENSURE FOLDERS EXIST ====
os.makedirs(JS_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(INDEX_HTML), exist_ok=True)

# ==== HELPER FUNCTIONS ====
def time_to_minutes(time_str):
    """Convert HH:MM:SS to total minutes as float."""
    h, m, s = [int(x) for x in time_str.split(":")]
    return h * 60 + m + s / 60

def read_csv_clean(filepath):
    """
    Reads CSV and returns a list of dicts:
    TimeElapsed (minutes), Humidity, Temperature, Target, Heater
    Skips NAN and negative Temperature values.
    """
    cleaned = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                temp = float(row['Temperature'])
                if temp < 0:
                    continue
            except:
                continue

            try:
                humidity = float(row['Humidity'])
            except:
                humidity = None

            try:
                target = float(row['Target'])
            except:
                target = None

            cleaned.append({
                "TimeElapsed": time_to_minutes(row['TimeElapsed']),
                "Humidity": humidity,
                "Temperature": temp,
                "Target": target,
                "Heater": row['Heater']
            })
    return cleaned

# ==== GENERATE JS FILES AND COLLECT DATA ====
js_files = []
csv_files = sorted(f for f in os.listdir(HEATER_FOLDER) if f.endswith(".csv"))

for filename in csv_files:
    filepath = os.path.join(HEATER_FOLDER, filename)
    data = read_csv_clean(filepath)

    var_name = "data_" + filename.replace(".csv", "")
    js_content = f"""// Date: {datetime.now().strftime('%Y-%m-%d')}
// Copy this JS file into your HTML <head> or before </body> in index.html
// Variable: {var_name}
const {var_name} = {json.dumps(data, indent=2)};
"""
    js_filepath = os.path.join(JS_FOLDER, filename.replace(".csv", ".js"))
    with open(js_filepath, 'w') as f:
        f.write(js_content)

    js_files.append((var_name, filename.replace(".csv", ".js")))

print(f"Generated {len(js_files)} JS files in {JS_FOLDER}")

# ==== GENERATE INDEX.HTML ====
script_tags = "\n".join([f'<script src="js/{js_file}"></script>' for _, js_file in js_files])

# Generate multiple divs for plots
plot_divs = "\n".join([f'<div id="plot_{i}" style="width:100%;height:400px;"></div>' for i in range(len(js_files))])

# Generate JS scripts to create plots for each CSV
plotly_scripts = ""
for i, (var_name, _) in enumerate(js_files):
    plotly_scripts += f"""
var trace_temp_{i} = {{
  x: {var_name}.map(d => d.TimeElapsed),
  y: {var_name}.map(d => d.Temperature),
  mode: 'lines+markers',
  name: '{var_name} Temperature',
  yaxis: 'y1',
  marker: {{color: 'red'}}
}};
var trace_hum_{i} = {{
  x: {var_name}.map(d => d.TimeElapsed),
  y: {var_name}.map(d => d.Humidity),
  mode: 'lines+markers',
  name: '{var_name} Humidity',
  yaxis: 'y2',
  marker: {{color: 'blue'}}
}};
Plotly.newPlot('plot_{i}', [trace_temp_{i}, trace_hum_{i}], {{
  title: '{var_name} - Temperature & Humidity vs Time',
  xaxis: {{title: 'Time (minutes)'}},
  yaxis: {{title: 'Temperature (°C)', side: 'left', color: 'red'}},
  yaxis2: {{
      title: 'Humidity (%)',
      overlaying: 'y',
      side: 'right',
      color: 'blue'
  }}
}});
"""

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MycoReator</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
{script_tags}
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
</style>
</head>
<body>
<h1>MycoReator</h1>

<h2>Objective</h2>
<p>Control a heating pad using SHT30 temperature sensor and visualize the logged temperature and humidity data.</p>

<h2>Major Tasks</h2>
<ul>
<li>Read CSV logs from Arduino heater system</li>
<li>Convert CSV data to JSON for JavaScript</li>
<li>Plot Time vs Temperature (left Y-axis) and Humidity (right Y-axis) using Plotly.js</li>
<li>Ignore invalid or negative temperature readings</li>
<li>Provide interactive visualizations of heater behavior</li>
</ul>

<h2>Tools Used</h2>
<ul>
<li>Python: CSV processing and JS generation</li>
<li>HTML/CSS/JavaScript: website structure and styling</li>
<li>Plotly.js: interactive plotting library</li>
<li>Arduino with SHT30 sensor & MOSFET heater control</li>
<li>CSV logs from Arduino</li>
</ul>

<h2>Hardware Setup</h2>
<pre>
SHT30 Sensor (I2C)
- Red    -> 5V
- Black  -> GND
- Yellow -> SCL (Mega pin 21)
- White  -> SDA (Mega pin 20)

Heating Pad via MOSFET (IRL44N)
- Gate   -> Arduino pin 9
- Drain  -> Heating pad negative (-)
- Source -> GND
- Heating pad positive (+) -> 12V DC adapter positive
- 1N4007 diode across heating pad (Cathode to +12V, Anode to Drain)

Power Supply
- Alito AC/DC Adapter ALT-1201: 12V DC, 1A for heating pad
- Arduino powered via USB or separate 5V supply
</pre>

<h2>Plots</h2>
{plot_divs}

<script>
{plotly_scripts}
</script>

</body>
</html>
"""

with open(INDEX_HTML, 'w') as f:
    f.write(html_content)

print(f"index.html generated at {INDEX_HTML} with {len(js_files)} plots")
