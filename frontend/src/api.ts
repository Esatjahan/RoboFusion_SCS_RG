const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000/api/v1";

export type RiskLevel =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL";

export interface ApiZone {
  id: number;
  code: string;
  name: string;
  location: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApiSensorReading {
  id: number;
  zone_id: number;
  device_id: string;

  temperature_c: number;
  humidity_percent: number;
  smoke_ppm: number;
  gas_ppm: number;
  water_level_percent: number;
  vibration_level: number;

  flame_detected: boolean;
  motion_detected: boolean;
  occupancy_count: number;
  battery_voltage: number;

  captured_at: string | null;
  received_at: string;
}

export interface ApiRiskAssessment {
  id: number;
  sensor_reading_id: number;
  zone_id: number;

  score: number;
  level: RiskLevel;

  temperature_risk: number;
  humidity_risk: number;
  smoke_risk: number;
  gas_risk: number;
  water_risk: number;
  vibration_risk: number;
  flame_risk: number;
  occupancy_risk: number;
  battery_risk: number;

  reasons: string[];
  created_at: string;
}

async function apiRequest<T>(
  endpoint: string,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      signal,
    },
  );

  if (!response.ok) {
    let errorMessage =
      `API request failed with status ${response.status}`;

    try {
      const errorBody = await response.json();

      if (
        typeof errorBody === "object" &&
        errorBody !== null &&
        "detail" in errorBody
      ) {
        errorMessage = String(errorBody.detail);
      }
    } catch {
      // Response body JSON না হলেও status message দেখাবে।
    }

    throw new Error(errorMessage);
  }

  return (await response.json()) as T;
}

export function getZones(
  signal?: AbortSignal,
): Promise<ApiZone[]> {
  return apiRequest<ApiZone[]>(
    "/zones",
    signal,
  );
}

export function getSensorReadings(
  signal?: AbortSignal,
): Promise<ApiSensorReading[]> {
  return apiRequest<ApiSensorReading[]>(
    "/sensor-readings",
    signal,
  );
}

export function getRiskAssessments(
  signal?: AbortSignal,
): Promise<ApiRiskAssessment[]> {
  return apiRequest<ApiRiskAssessment[]>(
    "/risk-assessments",
    signal,
  );
}