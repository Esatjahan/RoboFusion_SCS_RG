# RoboFusion SCS-RG

Multi-Hazard Smart Campus Safety & Response Grid developed for RoboFusion 1.0 Techathon Round 1.

## Project Goal

Build a simulation-based full-stack IoT safety system that monitors multiple campus zones for:

- Fire or flame
- Gas concentration
- Water-level or flood risk
- Occupancy or presence

The backend computes risk scores from raw sensor readings, ranks critical zones by response priority, stores events in a real database, and updates a live command dashboard.

## Selected Track

Track B — Wokwi Simulation

## Selected Zones

1. IoT Lab
2. Server Room
3. Robotics Lab

## Planned Technology Stack

- ESP32 and Wokwi
- Python and FastAPI
- PostgreSQL
- React and Vite
- WebSocket
- JWT authentication

## Repository Structure

```text
backend/
frontend/
database/
zone-node/
docs/
tests/
load-tests/
ml/
demo/