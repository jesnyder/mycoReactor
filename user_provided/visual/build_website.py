# Date Created: 2026-02-12
# MycoReactor Website Builder
# Purpose: Generate interactive HTML dashboard from heater experiment CSV data
# Output: index.html in ../../docs and JavaScript data files in ../../docs/js

import os
import csv
import json
from datetime import datetime


def build_website():
    """
    Main function to build the MycoReactor website.
    Reads CSV files from ../../results/heater, creates JavaScript data files,
    and generates an interactive HTML dashboard with plots, tables, and statistics.
    """
    print("=" * 60)
    print("MycoReactor Website Builder Started")
    print("=" * 60)

    # Define paths
    heater_folder = "../../results/heater"
    docs_folder = "../../docs"
    js_folder = os.path.join(docs_folder, "js")
    notes_folder = "../../user_provided/experiment_notes"

    # Create necessary directories
    print("\n[1/5] Creating output directories...")
    os.makedirs(docs_folder, exist_ok=True)
    os.makedirs(js_folder, exist_ok=True)
    print(f"  ✓ Created {docs_folder}")
    print(f"  ✓ Created {js_folder}")

    # Get all CSV files and sort in reverse chronological order
    print("\n[2/5] Scanning for CSV files...")
    csv_files = []
    if os.path.exists(heater_folder):
        csv_files = [f for f in os.listdir(heater_folder) if f.endswith('.csv')]
        csv_files.sort(reverse=True)  # Reverse chronological order
        print(f"  ✓ Found {len(csv_files)} CSV file(s)")
        for f in csv_files:
            print(f"    - {f}")
    else:
        print(f"  ✗ Warning: {heater_folder} not found")
        print("  Creating empty website...")

    # Process each CSV file
    print("\n[3/5] Processing CSV files and generating JavaScript...")
    datasets = []

    for csv_file in csv_files:
        print(f"\n  Processing: {csv_file}")
        csv_path = os.path.join(heater_folder, csv_file)
        base_name = csv_file.replace('.csv', '')
        js_filename = f"{base_name}.js"
        js_path = os.path.join(js_folder, js_filename)

        # Parse CSV data
        data = parse_csv(csv_path, base_name)

        if data:
            # Generate JavaScript file
            create_js_file(js_path, base_name, data)
            print(f"    ✓ Created {js_filename}")

            # Check for experiment notes
            notes = get_experiment_notes(notes_folder, base_name)

            # Calculate statistics
            stats = calculate_statistics(data)

            # Store dataset info
            datasets.append({
                'filename': csv_file,
                'basename': base_name,
                'js_filename': js_filename,
                'notes': notes,
                'stats': stats,
                'data': data
            })
            print(f"    ✓ Statistics calculated")
        else:
            print(f"    ✗ No valid data found in {csv_file}")

    # Generate HTML
    print("\n[4/5] Generating index.html...")
    html_path = os.path.join(docs_folder, "index.html")
    generate_html(html_path, datasets)
    print(f"  ✓ Created index.html")

    print("\n[5/5] Website build complete!")
    print("=" * 60)
    print(f"Output location: {os.path.abspath(docs_folder)}")
    print(f"Open: {os.path.abspath(html_path)}")
    print("=" * 60)


def parse_csv(csv_path, base_name):
    """
    Parse CSV file and extract valid data points.
    Handles UTF-8 encoding issues, ignores NAN and negative values.

    Args:
        csv_path: Path to the CSV file
        base_name: Base filename without extension

    Returns:
        Dictionary with parsed data arrays
    """
    print(f"    Parsing CSV data...")

    data = {
        'time_minutes': [],
        'humidity': [],
        'temperature': [],
        'target': [],
        'heater': [],
        'time_elapsed': []
    }

    try:
        # Open with UTF-8 encoding and ignore errors
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Parse TimeElapsed (HH:MM:SS)
                time_elapsed = row.get('TimeElapsed', '').strip()
                if time_elapsed and time_elapsed != 'NAN':
                    try:
                        parts = time_elapsed.split(':')
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        seconds = int(parts[2])
                        total_minutes = hours * 60 + minutes + seconds / 60.0
                    except (ValueError, IndexError):
                        continue  # Skip invalid time formats
                else:
                    continue  # Skip rows with NAN time

                # Parse Humidity (ignore NAN and negative)
                humidity_str = row.get('Humidity', '').strip()
                humidity = None
                if humidity_str and humidity_str != 'NAN':
                    try:
                        humidity = float(humidity_str)
                        if humidity < 0:
                            humidity = None
                    except ValueError:
                        humidity = None

                # Parse Temperature (ignore NAN and negative)
                temp_str = row.get('Temperature', '').strip()
                temperature = None
                if temp_str and temp_str != 'NAN':
                    try:
                        temperature = float(temp_str)
                        if temperature < 0:
                            temperature = None
                    except ValueError:
                        temperature = None

                # Parse Target (ignore NAN and negative)
                target_str = row.get('Target', '').strip()
                target = None
                if target_str and target_str != 'NAN':
                    try:
                        target = float(target_str)
                        if target < 0:
                            target = None
                    except ValueError:
                        target = None

                # Parse Heater status
                heater = row.get('Heater', '').strip()
                if heater not in ['ON', 'OFF']:
                    heater = None

                # Store data point (only if we have valid time)
                data['time_minutes'].append(total_minutes)
                data['humidity'].append(humidity)
                data['temperature'].append(temperature)
                data['target'].append(target)
                data['heater'].append(heater)
                data['time_elapsed'].append(time_elapsed)

        print(f"    ✓ Parsed {len(data['time_minutes'])} data points")
        return data

    except Exception as e:
        print(f"    ✗ Error reading CSV: {e}")
        return None


def create_js_file(js_path, base_name, data):
    """
    Create JavaScript file with dataset as a const variable.

    Args:
        js_path: Path to output JavaScript file
        base_name: Base filename for variable naming
        data: Parsed data dictionary
    """
    # Create unique variable name (replace special chars with underscore)
    var_name = f"data_{base_name.replace('-', '_')}"

    # Create header comment
    header = f"""/*
 * MycoReactor Data File
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * Source: {base_name}.csv
 *
 * TO USE THIS FILE IN index.html:
 * 1. Add this line in the <head> section or before the closing </body> tag:
 *    <script src="js/{base_name}.js"></script>
 *
 * 2. Access the data in your JavaScript code using:
 *    {var_name}
 *
 * Data structure:
 *   - time_minutes: Array of time points in minutes
 *   - humidity: Array of humidity values (%)
 *   - temperature: Array of temperature values (°C)
 *   - target: Array of target temperature values (°C)
 *   - heater: Array of heater status ('ON' or 'OFF')
 *   - time_elapsed: Array of formatted time strings (HH:MM:SS)
 */

"""

    # Convert data to JSON
    js_content = header + f"const {var_name} = {json.dumps(data, indent=2)};\n"

    # Write to file
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)


def get_experiment_notes(notes_folder, base_name):
    """
    Check for experiment notes file and read contents.

    Args:
        notes_folder: Path to notes folder
        base_name: Base filename to look for

    Returns:
        String with notes content or None
    """
    if not os.path.exists(notes_folder):
        return None

    notes_path = os.path.join(notes_folder, f"{base_name}.txt")
    if os.path.exists(notes_path):
        try:
            with open(notes_path, 'r', encoding='utf-8', errors='ignore') as f:
                notes = f.read().strip()
                print(f"    ✓ Found experiment notes")
                return notes
        except Exception as e:
            print(f"    ✗ Error reading notes: {e}")

    return None


def calculate_statistics(data):
    """
    Calculate statistics from the data.
    Ignores None values (which represent NAN or negative numbers).

    Args:
        data: Parsed data dictionary

    Returns:
        Dictionary with calculated statistics
    """
    stats = {}

    # Duration calculations
    time_points = data['time_minutes']
    if time_points:
        stats['duration_minutes'] = max(time_points) - min(time_points)
    else:
        stats['duration_minutes'] = 0

    # Calculate heater ON and OFF durations
    heater_on_duration = 0
    heater_off_duration = 0

    for i in range(len(data['heater']) - 1):
        if data['heater'][i] is not None:
            time_diff = data['time_minutes'][i+1] - data['time_minutes'][i]
            if data['heater'][i] == 'ON':
                heater_on_duration += time_diff
            elif data['heater'][i] == 'OFF':
                heater_off_duration += time_diff

    stats['heater_on_minutes'] = heater_on_duration
    stats['heater_off_minutes'] = heater_off_duration

    # Temperature statistics (filter out None values)
    valid_temps = [t for t in data['temperature'] if t is not None]
    if valid_temps:
        stats['temp_min'] = min(valid_temps)
        stats['temp_max'] = max(valid_temps)
        stats['temp_avg'] = sum(valid_temps) / len(valid_temps)
        stats['temp_range'] = stats['temp_max'] - stats['temp_min']
    else:
        stats['temp_min'] = stats['temp_max'] = stats['temp_avg'] = stats['temp_range'] = 0

    # Humidity statistics (filter out None values)
    valid_humidity = [h for h in data['humidity'] if h is not None]
    if valid_humidity:
        stats['humidity_min'] = min(valid_humidity)
        stats['humidity_max'] = max(valid_humidity)
        stats['humidity_avg'] = sum(valid_humidity) / len(valid_humidity)
        stats['humidity_range'] = stats['humidity_max'] - stats['humidity_min']
    else:
        stats['humidity_min'] = stats['humidity_max'] = stats['humidity_avg'] = stats['humidity_range'] = 0

    return stats


def format_timestamp(base_name):
    """
    Convert filename timestamp to readable date format.
    Example: 202602111405 -> Feb 11, 2026 14:05

    Args:
        base_name: Filename without extension (e.g., '202602111405')

    Returns:
        Formatted date string
    """
    try:
        # Parse timestamp: YYYYMMDDHHMM
        year = int(base_name[0:4])
        month = int(base_name[4:6])
        day = int(base_name[6:8])
        hour = int(base_name[8:10])
        minute = int(base_name[10:12])

        dt = datetime(year, month, day, hour, minute)
        return dt.strftime('%b %d, %Y %H:%M')
    except (ValueError, IndexError):
        return base_name


def convert_urls_to_links(text):
    """
    Convert URLs in text to HTML hyperlinks that open in new tab.

    Args:
        text: Text that may contain URLs

    Returns:
        Text with URLs converted to <a> tags
    """
    if not text:
        return text

    import re
    # Simple URL pattern
    url_pattern = r'(https?://[^\s]+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)


def generate_html(html_path, datasets):
    """
    Generate the main index.html file with all visualizations.

    Args:
        html_path: Path to output HTML file
        datasets: List of dataset dictionaries
    """

    # Start HTML document
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MycoReactor</title>

    <!-- External Libraries -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css" rel="stylesheet">
    <script type="text/javascript" src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>

"""

    # Add JavaScript data files
    for dataset in datasets:
        html += f'    <script src="js/{dataset["js_filename"]}"></script>\n'

    # Add styles with a clean, scientific aesthetic
    html += """
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #34495e;
            --accent-color: #3498db;
            --success-color: #27ae60;
            --background: #ecf0f1;
            --card-background: #ffffff;
            --text-color: #2c3e50;
            --border-color: #bdc3c7;
            --shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--background);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--card-background);
            padding: 40px;
            border-radius: 8px;
            box-shadow: var(--shadow);
        }

        h1 {
            color: var(--primary-color);
            font-size: 2.5em;
            margin-bottom: 10px;
            border-bottom: 3px solid var(--accent-color);
            padding-bottom: 10px;
        }

        h2 {
            color: var(--secondary-color);
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 4px solid var(--accent-color);
            padding-left: 15px;
        }

        h3 {
            color: var(--secondary-color);
            font-size: 1.4em;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        p {
            margin-bottom: 15px;
        }

        a {
            color: var(--accent-color);
            text-decoration: none;
            font-weight: 500;
        }

        a:hover {
            text-decoration: underline;
        }

        .github-link {
            display: inline-block;
            background: var(--accent-color);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            margin: 20px 0;
            transition: background 0.3s;
        }

        .github-link:hover {
            background: #2980b9;
            text-decoration: none;
        }

        ul, ol {
            margin-left: 30px;
            margin-bottom: 15px;
        }

        li {
            margin-bottom: 8px;
        }

        .dataset {
            background: var(--background);
            padding: 30px;
            margin: 30px 0;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .dataset-title {
            font-size: 1.6em;
            color: var(--primary-color);
            margin-bottom: 15px;
        }

        .notes {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-item {
            background: var(--card-background);
            padding: 15px;
            border-radius: 5px;
            border: 1px solid var(--border-color);
        }

        .stat-label {
            font-weight: 600;
            color: var(--secondary-color);
            font-size: 0.9em;
        }

        .stat-value {
            font-size: 1.3em;
            color: var(--accent-color);
            font-weight: 700;
        }

        .plot-container {
            margin: 20px 0;
            background: var(--card-background);
            padding: 20px;
            border-radius: 5px;
            box-shadow: var(--shadow);
        }

        .download-btn {
            background: var(--success-color);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 1em;
            border-radius: 5px;
            cursor: pointer;
            margin: 15px 0;
            transition: background 0.3s;
            font-weight: 600;
        }

        .download-btn:hover {
            background: #229954;
        }

        .table-container {
            margin: 20px 0;
        }

        .wiring-diagram {
            background: var(--card-background);
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            border: 1px solid var(--border-color);
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }

        code {
            background: var(--background);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MycoReactor</h1>

        <h2>Objective</h2>
        <p>
            Control and monitor a heating pad system for precise temperature regulation using
            an Arduino, SHT30 temperature/humidity sensor, and MOSFET. Data is logged and
            visualized to optimize heater performance and maintain consistent environmental
            conditions for mycelium cultivation.
        </p>
        <a href="https://github.com/jesnyder/mycoReactor" class="github-link" target="_blank">
            View on GitHub →
        </a>

        <h2>Capabilities</h2>
        <p>
            The MycoReactor system provides real-time temperature and humidity monitoring with
            automated heater control. The Arduino reads environmental data every second and
            makes intelligent decisions to maintain target temperatures within specified ranges.
            All system activity is logged to timestamped CSV files every 10 seconds, creating
            a comprehensive record of environmental conditions. This data is then processed and
            visualized through interactive web-based plots, allowing detailed analysis of heating
            patterns, temperature stability, and system performance over time.
        </p>

        <h2>Tasks</h2>

        <h3>Hardware Components</h3>
        <ul>
            <li><strong>Arduino Mega</strong> - Main microcontroller for system control</li>
            <li><strong>SHT30 I2C Temperature & Humidity Sensor</strong> - High-precision environmental monitoring
                <br><a href="https://www.adafruit.com/product/2857" target="_blank">Adafruit SHT30 Sensor</a></li>
            <li><strong>IRL44N N-Channel MOSFET</strong> - Switching element for heater control
                <br><a href="https://www.icdrex.com/introducing-the-irlz44n-complete-guide-features-and-applications/" target="_blank">IRL44N Guide & Pinout</a></li>
            <li><strong>1N4007 Diode</strong> - Flyback protection for inductive loads</li>
            <li><strong>12V DC Heating Pad</strong> - Controlled heat source</li>
            <li><strong>Alito AC/DC Adapter (ALT-1201)</strong> - 12V DC, 1A power supply for heating pad</li>
        </ul>

        <h3>Software & Libraries</h3>
        <ul>
            <li><strong>Arduino IDE</strong> - Development environment for microcontroller programming</li>
            <li><strong>Wire.h</strong> - I2C communication library (built-in)</li>
            <li><strong>Adafruit_SHT31.h</strong> - SHT30 sensor driver
                <br><a href="https://github.com/adafruit/Adafruit_SHT31" target="_blank">GitHub Repository</a></li>
            <li><strong>Python 3</strong> - Data logging and website generation
                <ul>
                    <li>pySerial - Serial communication with Arduino</li>
                    <li>Standard library: csv, json, datetime, os</li>
                </ul>
            </li>
            <li><strong>Plotly.js</strong> - Interactive data visualization
                <br><a href="https://plotly.com/javascript/" target="_blank">Documentation</a></li>
            <li><strong>Tabulator</strong> - Interactive data tables
                <br><a href="https://tabulator.info/" target="_blank">Documentation</a></li>
        </ul>

        <h3>Wiring Diagram</h3>
        <div class="wiring-diagram">
<strong>SHT30 Temperature/Humidity Sensor (I2C)</strong>
├─ Red    → Arduino 5V
├─ Black  → Arduino GND
├─ Yellow → Arduino SCL (Pin 21 on Mega)
└─ White  → Arduino SDA (Pin 20 on Mega)

<strong>IRL44N MOSFET (TO-220 Package, front view with text facing you)</strong>
Pin Layout (left to right): Gate - Drain - Source

├─ <strong>Gate (G)</strong>   → Arduino Pin 9 (PWM control signal)
├─ <strong>Drain (D)</strong>  → Heating Pad Negative (-)
└─ <strong>Source (S)</strong> → Arduino GND (CRITICAL: common ground!)

<strong>Heating Pad Power Circuit</strong>
├─ Positive (+) → 12V DC Adapter Positive
└─ Negative (-) → MOSFET Drain (D)

<strong>1N4007 Flyback Diode (across heating pad)</strong>
├─ <strong>Cathode</strong> (silver band) → Heating Pad Positive (+) / 12V
└─ <strong>Anode</strong>               → Heating Pad Negative (-) / MOSFET Drain
   Purpose: Protects MOSFET from voltage spikes

<strong>Power Supplies</strong>
├─ Arduino: USB or 5V external supply
└─ Heating Pad: 12V DC, 1A adapter (Alito ALT-1201)

<strong>⚠️ CRITICAL CONNECTIONS</strong>
1. Arduino GND MUST connect to MOSFET Source
2. 12V adapter GND MUST connect to Arduino GND
3. All grounds must be common for proper MOSFET operation
        </div>

        <h3>Lessons Learned</h3>
        <ul>
            <li><strong>Double-check pin assignments</strong> - Always confirm which Arduino pin connects to the MOSFET gate. Wrong pins can prevent control or damage components.</li>
            <li><strong>Understand MOSFET pinout</strong> - On IRL44N (TO-220), looking at the front (text side), pins left to right are: Gate → Drain → Source. Misidentification prevents switching or causes permanent-on states.</li>
            <li><strong>Common ground is essential</strong> - Arduino ground and heater/MOSFET ground must be connected. Without shared reference, MOSFET cannot switch properly.</li>
            <li><strong>Diode placement matters</strong> - Flyback diode (1N4007) goes across the load, not the MOSFET. Cathode (silver band) to positive voltage, anode to MOSFET drain. Protects from voltage spikes.</li>
            <li><strong>Check voltage ratings</strong> - Ensure MOSFET and diode are rated for heater voltage and current to prevent damage.</li>
            <li><strong>Test with low power first</strong> - Validate control logic with LEDs or small loads before applying full 12V.</li>
            <li><strong>Thermal lag is normal</strong> - Temperature sensors react to environment, not instantly to heater changes. Expect overshoot and lag with bang-bang control.</li>
            <li><strong>Serial commands enable dynamic adjustment</strong> - Setting target temperature via Serial Monitor (e.g., "H 50" for 50°C) allows safe testing without reprogramming.</li>
            <li><strong>Document wiring clearly</strong> - Detailed diagrams and labels prevent mistakes. Label all wires: SHT30 (VCC, GND, SCL, SDA), MOSFET (G, D, S), heater (+, -), diode.</li>
            <li><strong>Keep spare components</strong> - MOSFETs and diodes can fail if wired incorrectly. Having replacements minimizes downtime.</li>
        </ul>

        <h2>Results</h2>
        <p>Interactive visualizations of heater system performance over time. Each dataset shows temperature and humidity trends with heater activity indicated by shaded regions.</p>
"""

    # Add each dataset
    for dataset in datasets:
        var_name = f"data_{dataset['basename'].replace('-', '_')}"
        readable_date = format_timestamp(dataset['basename'])

        html += f"""
        <div class="dataset" id="dataset_{dataset['basename']}">
            <h3 class="dataset-title">{readable_date}</h3>
"""

        # Add notes if available
        if dataset['notes']:
            notes_html = convert_urls_to_links(dataset['notes'])
            html += f"""
            <div class="notes">
                <strong>Experiment Notes:</strong><br>
                {notes_html}
            </div>
"""

        # Add statistics
        stats = dataset['stats']
        html += f"""
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">Duration</div>
                    <div class="stat-value">{stats['duration_minutes']:.2f} min</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Heater ON</div>
                    <div class="stat-value">{stats['heater_on_minutes']:.2f} min</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Heater OFF</div>
                    <div class="stat-value">{stats['heater_off_minutes']:.2f} min</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Temp Max</div>
                    <div class="stat-value">{stats['temp_max']:.2f} °C</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Temp Min</div>
                    <div class="stat-value">{stats['temp_min']:.2f} °C</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Temp Avg</div>
                    <div class="stat-value">{stats['temp_avg']:.2f} °C</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Temp Range</div>
                    <div class="stat-value">{stats['temp_range']:.2f} °C</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Humidity Max</div>
                    <div class="stat-value">{stats['humidity_max']:.2f} %</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Humidity Min</div>
                    <div class="stat-value">{stats['humidity_min']:.2f} %</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Humidity Avg</div>
                    <div class="stat-value">{stats['humidity_avg']:.2f} %</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Humidity Range</div>
                    <div class="stat-value">{stats['humidity_range']:.2f} %</div>
                </div>
            </div>

            <div class="plot-container">
                <div id="plot_{dataset['basename']}"></div>
            </div>

            <button class="download-btn" onclick="downloadCSV_{dataset['basename']}()">
                📥 Download CSV Data
            </button>

            <div class="table-container">
                <div id="table_{dataset['basename']}"></div>
            </div>
        </div>
"""

    # Add JavaScript for plots and tables
    html += """
    <script>
        // Wait for DOM to be fully loaded
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Initializing MycoReactor visualizations...');
"""

    for dataset in datasets:
        var_name = f"data_{dataset['basename'].replace('-', '_')}"

        html += f"""
            // ========== Dataset: {dataset['basename']} ==========
            console.log('Processing dataset: {dataset['basename']}');

            // Prepare data for plotting
            var times_{dataset['basename']} = {var_name}.time_minutes;
            var temps_{dataset['basename']} = {var_name}.temperature;
            var humidity_{dataset['basename']} = {var_name}.humidity;
            var targets_{dataset['basename']} = {var_name}.target;
            var heater_{dataset['basename']} = {var_name}.heater;

            // Create temperature trace (left y-axis)
            var tempTrace_{dataset['basename']} = {{
                x: times_{dataset['basename']},
                y: temps_{dataset['basename']},
                mode: 'lines+markers',
                name: 'Temperature',
                line: {{color: 'rgb(219, 64, 82)', width: 2}},
                marker: {{size: 4}},
                yaxis: 'y1'
            }};

            // Create humidity trace (right y-axis)
            var humidityTrace_{dataset['basename']} = {{
                x: times_{dataset['basename']},
                y: humidity_{dataset['basename']},
                mode: 'lines+markers',
                name: 'Humidity',
                line: {{color: 'rgb(30, 136, 229)', width: 2}},
                marker: {{size: 4}},
                yaxis: 'y2'
            }};

            // Create target temperature line (dashed)
            var targetTrace_{dataset['basename']} = {{
                x: times_{dataset['basename']},
                y: targets_{dataset['basename']},
                mode: 'lines',
                name: 'Target Temp',
                line: {{color: 'black', width: 2, dash: 'dash'}},
                yaxis: 'y1'
            }};

            // Create heater ON shading
            var shapes_{dataset['basename']} = [];
            var shadeStart_{dataset['basename']} = null;

            for (var i = 0; i < heater_{dataset['basename']}.length; i++) {{
                if (heater_{dataset['basename']}[i] === 'ON' && shadeStart_{dataset['basename']} === null) {{
                    shadeStart_{dataset['basename']} = times_{dataset['basename']}[i];
                }} else if (heater_{dataset['basename']}[i] === 'OFF' && shadeStart_{dataset['basename']} !== null) {{
                    shapes_{dataset['basename']}.push({{
                        type: 'rect',
                        xref: 'x',
                        yref: 'paper',
                        x0: shadeStart_{dataset['basename']},
                        x1: times_{dataset['basename']}[i],
                        y0: 0,
                        y1: 1,
                        fillcolor: 'rgba(255, 200, 200, 0.3)',
                        line: {{width: 0}},
                        layer: 'below'
                    }});
                    shadeStart_{dataset['basename']} = null;
                }}
            }}

            // If heater was still ON at the end
            if (shadeStart_{dataset['basename']} !== null) {{
                shapes_{dataset['basename']}.push({{
                    type: 'rect',
                    xref: 'x',
                    yref: 'paper',
                    x0: shadeStart_{dataset['basename']},
                    x1: times_{dataset['basename']}[times_{dataset['basename']}.length - 1],
                    y0: 0,
                    y1: 1,
                    fillcolor: 'rgba(255, 200, 200, 0.3)',
                    line: {{width: 0}},
                    layer: 'below'
                }});
            }}

            // Plot layout
            var layout_{dataset['basename']} = {{
                title: 'Temperature and Humidity Over Time',
                xaxis: {{
                    title: 'Time Elapsed (minutes)',
                    gridcolor: '#e1e1e1'
                }},
                yaxis: {{
                    title: 'Temperature (°C)',
                    titlefont: {{color: 'rgb(219, 64, 82)'}},
                    tickfont: {{color: 'rgb(219, 64, 82)'}},
                    gridcolor: '#e1e1e1'
                }},
                yaxis2: {{
                    title: 'Humidity (%)',
                    titlefont: {{color: 'rgb(30, 136, 229)'}},
                    tickfont: {{color: 'rgb(30, 136, 229)'}},
                    overlaying: 'y',
                    side: 'right'
                }},
                shapes: shapes_{dataset['basename']},
                hovermode: 'closest',
                showlegend: true,
                legend: {{
                    x: 1.02,
                    xanchor: 'left',
                    y: 1.0,
                    yanchor: 'top',
                    bgcolor: 'rgba(255, 255, 255, 0.9)',
                    bordercolor: '#ccc',
                    borderwidth: 1
                }},
                plot_bgcolor: '#f9f9f9',
                paper_bgcolor: 'white'
            }};

            // Create plot
            var plotData_{dataset['basename']} = [tempTrace_{dataset['basename']}, humidityTrace_{dataset['basename']}, targetTrace_{dataset['basename']}];
            Plotly.newPlot('plot_{dataset['basename']}', plotData_{dataset['basename']}, layout_{dataset['basename']}, {{
                responsive: true,
                toImageButtonOptions: {{
                    filename: '{dataset['basename']}'
                }}
            }});

            // Create table data
            var tableData_{dataset['basename']} = [];
            for (var i = 0; i < times_{dataset['basename']}.length; i++) {{
                tableData_{dataset['basename']}.push({{
                    time_minutes: times_{dataset['basename']}[i],
                    time_elapsed: {var_name}.time_elapsed[i],
                    temperature: temps_{dataset['basename']}[i],
                    humidity: humidity_{dataset['basename']}[i],
                    target: targets_{dataset['basename']}[i],
                    heater: heater_{dataset['basename']}[i]
                }});
            }}

            // Create Tabulator table
            var table_{dataset['basename']} = new Tabulator("#table_{dataset['basename']}", {{
                data: tableData_{dataset['basename']},
                layout: "fitColumns",
                pagination: "local",
                paginationSize: 10,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    {{title: "Time (min)", field: "time_minutes", formatter: function(cell) {{
                        var value = cell.getValue();
                        return value !== null ? value.toFixed(2) : 'N/A';
                    }}}},
                    {{title: "Time Elapsed", field: "time_elapsed"}},
                    {{title: "Temperature (°C)", field: "temperature", formatter: function(cell) {{
                        var value = cell.getValue();
                        return value !== null ? value.toFixed(2) : 'N/A';
                    }}}},
                    {{title: "Humidity (%)", field: "humidity", formatter: function(cell) {{
                        var value = cell.getValue();
                        return value !== null ? value.toFixed(2) : 'N/A';
                    }}}},
                    {{title: "Target (°C)", field: "target", formatter: function(cell) {{
                        var value = cell.getValue();
                        return value !== null ? value.toFixed(2) : 'N/A';
                    }}}},
                    {{title: "Heater", field: "heater"}}
                ]
            }});

            console.log('✓ Completed: {dataset['basename']}');
"""

    html += """
            console.log('All visualizations loaded successfully!');
        });

"""

    # Add CSV download functions
    for dataset in datasets:
        var_name = f"data_{dataset['basename'].replace('-', '_')}"

        html += f"""
        // CSV download function for {dataset['basename']}
        function downloadCSV_{dataset['basename']}() {{
            var csv = 'TimeElapsed,Humidity,Temperature,Target,Heater\\n';

            for (var i = 0; i < {var_name}.time_elapsed.length; i++) {{
                var row = [
                    {var_name}.time_elapsed[i],
                    {var_name}.humidity[i] !== null ? {var_name}.humidity[i] : 'NAN',
                    {var_name}.temperature[i] !== null ? {var_name}.temperature[i] : 'NAN',
                    {var_name}.target[i] !== null ? {var_name}.target[i] : 'NAN',
                    {var_name}.heater[i] !== null ? {var_name}.heater[i] : 'NAN'
                ];
                csv += row.join(',') + '\\n';
            }}

            // Create download link
            var blob = new Blob([csv], {{ type: 'text/csv' }});
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = '{dataset['basename']}.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }}
"""

    # Close HTML
    html += """
    </script>
    </div>
</body>
</html>
"""

    # Write HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)


# Execute the function when script is run
if __name__ == "__main__":
    build_website()
