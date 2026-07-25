import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Clock3,
  Cpu,
  Database,
  GraduationCap,
  MapPin,
  RefreshCw,
  Server,
  ShieldCheck,
  Thermometer,
  Wifi,
} from "lucide-react";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getRiskAssessments,
  getSensorReadings,
  getZones,
  type ApiRiskAssessment,
  type ApiSensorReading,
  type ApiZone,
  type RiskLevel,
} from "./api";

import "./App.css";

const MAX_SENSOR_ROWS = 10;
const MAX_RISK_ROWS = 10;
const MAX_CHART_ITEMS = 20;
const REFRESH_INTERVAL_MS = 30_000;

function formatDateTime(value: string | null): string {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-BD", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Dhaka",
  }).format(date);
}

function formatChartTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-BD", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
    timeZone: "Asia/Dhaka",
  }).format(date);
}

function formatNumber(
  value: number | null | undefined,
  digits = 1,
): string {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(value)
  ) {
    return "—";
  }

  return value.toFixed(digits);
}

function normalizeRiskLevel(
  level: string | undefined,
): RiskLevel {
  const normalized = level?.toUpperCase();

  if (
    normalized === "LOW" ||
    normalized === "MEDIUM" ||
    normalized === "HIGH" ||
    normalized === "CRITICAL"
  ) {
    return normalized;
  }

  return "LOW";
}

function getRiskClass(level: string): string {
  return `risk-${normalizeRiskLevel(level).toLowerCase()}`;
}

function getRiskPriority(level: string): number {
  switch (normalizeRiskLevel(level)) {
    case "CRITICAL":
      return 4;
    case "HIGH":
      return 3;
    case "MEDIUM":
      return 2;
    case "LOW":
    default:
      return 1;
  }
}

interface DashboardData {
  zones: ApiZone[];
  sensorReadings: ApiSensorReading[];
  riskAssessments: ApiRiskAssessment[];
}

function App() {
  const [zones, setZones] = useState<ApiZone[]>([]);
  const [sensorReadings, setSensorReadings] = useState<
    ApiSensorReading[]
  >([]);
  const [riskAssessments, setRiskAssessments] = useState<
    ApiRiskAssessment[]
  >([]);

  const [currentDateTime, setCurrentDateTime] =
    useState<Date>(new Date());

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] =
    useState(false);
  const [error, setError] = useState<string | null>(
    null,
  );
  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  const loadDashboardData = useCallback(
    async (
      signal?: AbortSignal,
      showFullLoader = false,
    ) => {
      if (showFullLoader) {
        setIsLoading(true);
      } else {
        setIsRefreshing(true);
      }

      try {
        const [
          zonesResponse,
          sensorReadingsResponse,
          riskAssessmentsResponse,
        ] = await Promise.all([
          getZones(signal),
          getSensorReadings(signal),
          getRiskAssessments(signal),
        ]);

        const dashboardData: DashboardData = {
          zones: zonesResponse,
          sensorReadings: sensorReadingsResponse,
          riskAssessments: riskAssessmentsResponse,
        };

        setZones(dashboardData.zones);
        setSensorReadings(
          dashboardData.sensorReadings,
        );
        setRiskAssessments(
          dashboardData.riskAssessments,
        );

        setError(null);
        setLastUpdated(new Date());
      } catch (requestError) {
        if (
          requestError instanceof DOMException &&
          requestError.name === "AbortError"
        ) {
          return;
        }

        const message =
          requestError instanceof Error
            ? requestError.message
            : "Unable to load dashboard data.";

        setError(
          `${message} Make sure the FastAPI backend is running on port 8000.`,
        );
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [],
  );

  useEffect(() => {
    const controller = new AbortController();

    void loadDashboardData(
      controller.signal,
      true,
    );

    return () => {
      controller.abort();
    };
  }, [loadDashboardData]);

  useEffect(() => {
    const clockTimer = window.setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000);

    return () => {
      window.clearInterval(clockTimer);
    };
  }, []);

  useEffect(() => {
    const refreshTimer = window.setInterval(() => {
      void loadDashboardData();
    }, REFRESH_INTERVAL_MS);

    return () => {
      window.clearInterval(refreshTimer);
    };
  }, [loadDashboardData]);

  const zoneMap = useMemo(() => {
    return new Map(
      zones.map((zone) => [zone.id, zone]),
    );
  }, [zones]);

  const latestReading = sensorReadings[0] ?? null;
  const latestRisk = riskAssessments[0] ?? null;

  const activeZones = useMemo(
    () =>
      zones.filter((zone) => zone.is_active)
        .length,
    [zones],
  );

  const uniqueDevices = useMemo(() => {
    return new Set(
      sensorReadings.map(
        (reading) => reading.device_id,
      ),
    ).size;
  }, [sensorReadings]);

  const highestRisk = useMemo(() => {
    if (riskAssessments.length === 0) {
      return null;
    }

    return riskAssessments.reduce(
      (highest, current) => {
        const currentPriority = getRiskPriority(
          current.level,
        );
        const highestPriority = getRiskPriority(
          highest.level,
        );

        if (currentPriority > highestPriority) {
          return current;
        }

        if (
          currentPriority === highestPriority &&
          current.score > highest.score
        ) {
          return current;
        }

        return highest;
      },
    );
  }, [riskAssessments]);

  const latestRiskByZone = useMemo(() => {
    const riskMap = new Map<
      number,
      ApiRiskAssessment
    >();

    for (const assessment of riskAssessments) {
      if (!riskMap.has(assessment.zone_id)) {
        riskMap.set(
          assessment.zone_id,
          assessment,
        );
      }
    }

    return riskMap;
  }, [riskAssessments]);

  const latestReadingByZone = useMemo(() => {
    const readingMap = new Map<
      number,
      ApiSensorReading
    >();

    for (const reading of sensorReadings) {
      if (!readingMap.has(reading.zone_id)) {
        readingMap.set(
          reading.zone_id,
          reading,
        );
      }
    }

    return readingMap;
  }, [sensorReadings]);

  const riskChartData = useMemo(() => {
    return riskAssessments
      .slice(0, MAX_CHART_ITEMS)
      .reverse()
      .map((assessment) => ({
        time: formatChartTime(
          assessment.created_at,
        ),
        score: assessment.score,
        level: assessment.level,
        zone:
          zoneMap.get(assessment.zone_id)
            ?.code ??
          `Zone ${assessment.zone_id}`,
      }));
  }, [riskAssessments, zoneMap]);

  const sensorChartData = useMemo(() => {
    return sensorReadings
      .slice(0, MAX_CHART_ITEMS)
      .reverse()
      .map((reading) => ({
        time: formatChartTime(
          reading.received_at,
        ),
        temperature: reading.temperature_c,
        humidity: reading.humidity_percent,
        smoke: reading.smoke_ppm,
        gas: reading.gas_ppm,
      }));
  }, [sensorReadings]);

  const dateText =
    new Intl.DateTimeFormat("en-BD", {
      weekday: "short",
      day: "2-digit",
      month: "short",
      year: "numeric",
      timeZone: "Asia/Dhaka",
    }).format(currentDateTime);

  const timeText =
    new Intl.DateTimeFormat("en-BD", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
      timeZone: "Asia/Dhaka",
    }).format(currentDateTime);

  if (isLoading) {
    return (
      <div className="app-shell">
        <main className="dashboard">
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-label">
                  CONNECTING
                </p>

                <h3>
                  Loading smart campus data
                </h3>
              </div>

              <RefreshCw
                size={22}
                className="spin-icon"
              />
            </div>

            <p className="loading-message">
              Fetching zones, sensor readings and
              risk assessments from the backend.
            </p>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <p className="eyebrow">
            ROBOFUSION TECHATHON 2026
          </p>

          <h1>
            Smart Campus Safety Dashboard
          </h1>

          <p className="subtitle">
            Real-time environmental monitoring,
            risk fusion and emergency intelligence
          </p>

          <div className="university-line">
            <GraduationCap size={18} />

            <span>
              University of Frontier Technology,
              Bangladesh
            </span>
          </div>
        </div>

        <div className="header-status">
          <div className="date-time-block">
            <Clock3 size={20} />

            <div>
              <strong>{timeText}</strong>
              <span>{dateText}</span>
            </div>
          </div>

          <div className="live-pill">
            <span className="live-dot" />
            System Online
          </div>

          <div className="team-block">
            <span>Team</span>
            <strong>GenZ Ignite</strong>
          </div>
        </div>
      </header>

      <main className="dashboard">
        {error && (
          <section className="panel error-panel">
            <div className="error-content">
              <AlertTriangle size={22} />

              <div>
                <strong>
                  Backend connection problem
                </strong>

                <p>{error}</p>
              </div>
            </div>

            <button
              className="refresh-button"
              type="button"
              onClick={() =>
                void loadDashboardData()
              }
              disabled={isRefreshing}
            >
              <RefreshCw
                size={17}
                className={
                  isRefreshing
                    ? "spin-icon"
                    : ""
                }
              />

              {isRefreshing
                ? "Refreshing..."
                : "Try again"}
            </button>
          </section>
        )}

        <section className="dashboard-toolbar">
          <div>
            <p className="section-label">
              LIVE OVERVIEW
            </p>

            <p className="toolbar-status">
              {lastUpdated
                ? `Last updated ${lastUpdated.toLocaleTimeString(
                    "en-BD",
                    {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                      hour12: true,
                    },
                  )}`
                : "Waiting for first update"}
            </p>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={() =>
              void loadDashboardData()
            }
            disabled={isRefreshing}
          >
            <RefreshCw
              size={17}
              className={
                isRefreshing
                  ? "spin-icon"
                  : ""
              }
            />

            {isRefreshing
              ? "Refreshing..."
              : "Refresh data"}
          </button>
        </section>

        <section className="stats-grid">
          <article className="stat-card">
            <div className="stat-icon">
              <MapPin size={23} />
            </div>

            <div>
              <p>Active Zones</p>
              <h2>{activeZones}</h2>

              <span>
                {zones.length} total registered
                zones
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">
              <Cpu size={23} />
            </div>

            <div>
              <p>Detected Devices</p>

              <h2 className="device-title">
                {uniqueDevices}
              </h2>

              <span>
                {sensorReadings.length} sensor
                readings received
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">
              <Activity size={23} />
            </div>

            <div>
              <p>Latest Risk Score</p>

              <h2>
                {latestRisk
                  ? formatNumber(
                      latestRisk.score,
                      0,
                    )
                  : "—"}
              </h2>

              <span
                className={`risk-badge ${
                  latestRisk
                    ? getRiskClass(
                        latestRisk.level,
                      )
                    : "risk-low"
                }`}
              >
                {latestRisk?.level ?? "NO DATA"}
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">
              {highestRisk?.level ===
              "CRITICAL" ? (
                <AlertTriangle size={23} />
              ) : (
                <ShieldCheck size={23} />
              )}
            </div>

            <div>
              <p>System Status</p>

              <h2 className="status-title">
                {highestRisk?.level ===
                "CRITICAL"
                  ? "Attention Required"
                  : highestRisk?.level === "HIGH"
                    ? "High Risk"
                    : "Operational"}
              </h2>

              <span>
                Highest recorded level:{" "}
                {highestRisk?.level ??
                  "No assessment"}
              </span>
            </div>
          </article>
        </section>

        <section className="charts-grid">
          <article className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-label">
                  RISK ANALYTICS
                </p>

                <h3>Risk Score Trend</h3>
              </div>

              <BarChart3 size={22} />
            </div>

            <div className="chart-container">
              {riskChartData.length > 0 ? (
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <AreaChart
                    data={riskChartData}
                    margin={{
                      top: 10,
                      right: 12,
                      left: -15,
                      bottom: 0,
                    }}
                  >
                    <defs>
                      <linearGradient
                        id="riskGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="5%"
                          stopColor="#38bdf8"
                          stopOpacity={0.4}
                        />

                        <stop
                          offset="95%"
                          stopColor="#38bdf8"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#263449"
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#64748b"
                      tick={{
                        fill: "#94a3b8",
                        fontSize: 11,
                      }}
                    />

                    <YAxis
                      domain={[0, 100]}
                      stroke="#64748b"
                      tick={{
                        fill: "#94a3b8",
                        fontSize: 11,
                      }}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#0f172a",
                        border: "1px solid #334155",
                        borderRadius: "10px",
                      }}
                      labelStyle={{
                        color: "#f8fafc",
                      }}
                    />

                    <Area
                      type="monotone"
                      dataKey="score"
                      name="Risk score"
                      stroke="#38bdf8"
                      strokeWidth={2.5}
                      fill="url(#riskGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">
                  No risk assessment data available.
                </div>
              )}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-label">
                  SENSOR ANALYTICS
                </p>

                <h3>Environmental Overview</h3>
              </div>

              <Thermometer size={22} />
            </div>

            <div className="chart-container">
              {sensorChartData.length > 0 ? (
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart
                    data={sensorChartData}
                    margin={{
                      top: 10,
                      right: 12,
                      left: -15,
                      bottom: 0,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#263449"
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#64748b"
                      tick={{
                        fill: "#94a3b8",
                        fontSize: 11,
                      }}
                    />

                    <YAxis
                      stroke="#64748b"
                      tick={{
                        fill: "#94a3b8",
                        fontSize: 11,
                      }}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#0f172a",
                        border: "1px solid #334155",
                        borderRadius: "10px",
                      }}
                      labelStyle={{
                        color: "#f8fafc",
                      }}
                    />

                    <Legend />

                    <Bar
                      dataKey="temperature"
                      name="Temperature °C"
                      fill="#38bdf8"
                      radius={[4, 4, 0, 0]}
                    />

                    <Bar
                      dataKey="humidity"
                      name="Humidity %"
                      fill="#8b5cf6"
                      radius={[4, 4, 0, 0]}
                    />

                    <Bar
                      dataKey="smoke"
                      name="Smoke ppm"
                      fill="#f97316"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">
                  No sensor data available.
                </div>
              )}
            </div>
          </article>
        </section>

        <section className="panel table-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">
                CAMPUS MONITORING
              </p>

              <h3>Zones Status</h3>
            </div>

            <Server size={22} />
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Temperature</th>
                  <th>Risk Score</th>
                  <th>Risk Level</th>
                </tr>
              </thead>

              <tbody>
                {zones.length > 0 ? (
                  zones.map((zone) => {
                    const reading =
                      latestReadingByZone.get(
                        zone.id,
                      );

                    const risk =
                      latestRiskByZone.get(zone.id);

                    return (
                      <tr key={zone.id}>
                        <td>
                          <strong>{zone.name}</strong>
                          <br />
                          <span>{zone.code}</span>
                        </td>

                        <td>{zone.location}</td>

                        <td>
                          <span
                            className={
                              zone.is_active
                                ? "online-badge"
                                : "offline-badge"
                            }
                          >
                            <span
                              className={
                                zone.is_active
                                  ? "online-dot"
                                  : "offline-dot"
                              }
                            />

                            {zone.is_active
                              ? "Active"
                              : "Inactive"}
                          </span>
                        </td>

                        <td>
                          {reading
                            ? `${formatNumber(
                                reading.temperature_c,
                              )} °C`
                            : "—"}
                        </td>

                        <td>
                          {risk
                            ? formatNumber(
                                risk.score,
                                0,
                              )
                            : "—"}
                        </td>

                        <td>
                          {risk ? (
                            <span
                              className={`risk-badge ${getRiskClass(
                                risk.level,
                              )}`}
                            >
                              {risk.level}
                            </span>
                          ) : (
                            <span>NO DATA</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={6}>
                      No zones are registered.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel table-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">
                REAL-TIME TELEMETRY
              </p>

              <h3>Latest Sensor Readings</h3>
            </div>

            <Wifi size={22} />
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Zone</th>
                  <th>Temperature</th>
                  <th>Humidity</th>
                  <th>Smoke</th>
                  <th>Gas</th>
                  <th>Flame</th>
                  <th>Received</th>
                </tr>
              </thead>

              <tbody>
                {sensorReadings.length > 0 ? (
                  sensorReadings
                    .slice(0, MAX_SENSOR_ROWS)
                    .map((reading) => (
                      <tr key={reading.id}>
                        <td>
                          <strong>
                            {reading.device_id}
                          </strong>
                        </td>

                        <td>
                          {zoneMap.get(
                            reading.zone_id,
                          )?.code ??
                            `Zone ${reading.zone_id}`}
                        </td>

                        <td>
                          {formatNumber(
                            reading.temperature_c,
                          )}{" "}
                          °C
                        </td>

                        <td>
                          {formatNumber(
                            reading.humidity_percent,
                          )}
                          %
                        </td>

                        <td>
                          {formatNumber(
                            reading.smoke_ppm,
                          )}{" "}
                          ppm
                        </td>

                        <td>
                          {formatNumber(
                            reading.gas_ppm,
                          )}{" "}
                          ppm
                        </td>

                        <td>
                          {reading.flame_detected
                            ? "Detected"
                            : "Clear"}
                        </td>

                        <td>
                          {formatDateTime(
                            reading.received_at,
                          )}
                        </td>
                      </tr>
                    ))
                ) : (
                  <tr>
                    <td colSpan={8}>
                      No sensor readings available.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel table-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">
                RISK FUSION ENGINE
              </p>

              <h3>Latest Risk Assessments</h3>
            </div>

            <Database size={22} />
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Assessment</th>
                  <th>Zone</th>
                  <th>Score</th>
                  <th>Level</th>
                  <th>Primary Reasons</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>
                {riskAssessments.length > 0 ? (
                  riskAssessments
                    .slice(0, MAX_RISK_ROWS)
                    .map((assessment) => (
                      <tr key={assessment.id}>
                        <td>
                          #{assessment.id}
                        </td>

                        <td>
                          {zoneMap.get(
                            assessment.zone_id,
                          )?.name ??
                            `Zone ${assessment.zone_id}`}
                        </td>

                        <td>
                          {formatNumber(
                            assessment.score,
                            0,
                          )}
                        </td>

                        <td>
                          <span
                            className={`risk-badge ${getRiskClass(
                              assessment.level,
                            )}`}
                          >
                            {assessment.level}
                          </span>
                        </td>

                        <td>
                          {assessment.reasons.length >
                          0
                            ? assessment.reasons.join(
                                " ",
                              )
                            : "No reason provided."}
                        </td>

                        <td>
                          {formatDateTime(
                            assessment.created_at,
                          )}
                        </td>
                      </tr>
                    ))
                ) : (
                  <tr>
                    <td colSpan={6}>
                      No risk assessments
                      available.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel latest-summary-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">
                LATEST SYSTEM SNAPSHOT
              </p>

              <h3>Current Monitoring Summary</h3>
            </div>

            <Activity size={22} />
          </div>

          <div className="summary-grid">
            <div>
              <span>Latest device</span>
              <strong>
                {latestReading?.device_id ??
                  "No data"}
              </strong>
            </div>

            <div>
              <span>Temperature</span>
              <strong>
                {latestReading
                  ? `${formatNumber(
                      latestReading.temperature_c,
                    )} °C`
                  : "—"}
              </strong>
            </div>

            <div>
              <span>Smoke level</span>
              <strong>
                {latestReading
                  ? `${formatNumber(
                      latestReading.smoke_ppm,
                    )} ppm`
                  : "—"}
              </strong>
            </div>

            <div>
              <span>Risk level</span>
              <strong>
                {latestRisk?.level ?? "No data"}
              </strong>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <p>
          <strong>Team GenZ Ignite</strong> · Mst.
          Esat Jahan Akhi · Md. Muniruzzaman Bony
        </p>

        <p className="footer-university">
          University of Frontier Technology,
          Bangladesh
        </p>

        <p>
          RoboFusion Techathon 2026 · Smart Campus
          Safety and Risk Fusion System
        </p>
      </footer>
    </div>
  );
}

export default App;