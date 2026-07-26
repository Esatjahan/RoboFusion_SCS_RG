# RoboFusion ESP32 Wokwi Zone Node

This simulation represents an ESP32-based smart campus safety zone node.

## Components

- ESP32 DevKit V1
- DHT22 temperature and humidity sensor
- Smoke simulation potentiometer
- Gas simulation potentiometer
- Water-level simulation potentiometer
- Vibration simulation potentiometer
- Flame detection pushbutton
- Motion detection pushbutton

## Pin Mapping

| Component          | ESP32 Pin |
| ------------------ | --------- |
| DHT22 Data         | GPIO 15   |
| Smoke Sensor       | GPIO 34   |
| Gas Sensor         | GPIO 35   |
| Water Level Sensor | GPIO 32   |
| Vibration Sensor   | GPIO 33   |
| Flame Button       | GPIO 25   |
| Motion Button      | GPIO 26   |

## Data Flow

Wokwi ESP32 → HTTPS POST → FastAPI → PostgreSQL → Risk Fusion Engine → React Dashboard

## API Endpoint

The ESP32 sends JSON sensor readings to:

`POST /api/v1/sensor-readings`

## Simulation Wi-Fi

The online Wokwi simulator uses:

- SSID: `Wokwi-GUEST`
- Password: blank

## Test Scenarios

### Normal Scenario

- Temperature: 24°C
- Humidity: 40%
- Smoke: 0 ppm
- Gas: 0 ppm
- Flame: Clear

Expected result:

- Risk score: 0
- Risk level: LOW

### Critical Fire Scenario

- Temperature: approximately 46.5°C
- Smoke: approximately 180 ppm
- Gas: approximately 240 ppm
- Vibration: approximately 1.8
- Flame: Detected

Expected result:

- Risk level: CRITICAL
- Dashboard status: Attention Required

## Run Instructions

1. Start the FastAPI backend.
2. Start the Cloudflare tunnel.
3. Place the active public URL in `API_URL` inside `sketch.ino`.
4. Start the Wokwi simulation.
5. Observe the Serial Monitor.
6. Open the React dashboard.
7. Click `Refresh data` to display the latest reading.
