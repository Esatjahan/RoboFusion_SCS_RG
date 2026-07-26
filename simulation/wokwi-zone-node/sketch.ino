#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ========================================================
// ROBOFUSION SCS-RG
// ESP32 WOKWI ZONE NODE
// ========================================================

// ========================================================
// WOKWI WIFI CONFIGURATION
// ========================================================

const char *WIFI_SSID = "Wokwi-GUEST";
const char *WIFI_PASSWORD = "";

// ========================================================
// FASTAPI PUBLIC ENDPOINT
// ========================================================

const char *API_URL =
    "https://soil-mil-tiny-hampton.trycloudflare.com/api/v1/sensor-readings";

// ========================================================
// ZONE NODE IDENTITY
// ========================================================
const int ZONE_ID = 1;
const char *DEVICE_ID = "WOKWI-IOT-LAB-001";

// ========================================================
// SENSOR PIN CONFIGURATION
// ========================================================
#define DHT_PIN 15
#define DHT_TYPE DHT22

#define SMOKE_PIN 34
#define GAS_PIN 35
#define WATER_PIN 32
#define VIBRATION_PIN 33

#define FLAME_PIN 25
#define MOTION_PIN 26

DHT dht(DHT_PIN, DHT_TYPE);

// ========================================================
// DATA SEND INTERVAL
// ========================================================

const unsigned long SEND_INTERVAL_MS = 5000;

unsigned long lastSendTime = 0;

// ========================================================
// FLOAT MAPPING FUNCTION
// ========================================================
float mapFloat(
    int value,
    int inputMin,
    int inputMax,
    float outputMin,
    float outputMax)
{
    return outputMin +
           (static_cast<float>(value - inputMin) *
            (outputMax - outputMin) /
            static_cast<float>(inputMax - inputMin));
}

// ========================================================
// WIFI CONNECTION
// ========================================================
void connectToWiFi()
{
    Serial.println();
    Serial.println("========================================");
    Serial.println("Connecting to Wokwi Wi-Fi...");
    Serial.println("========================================");

    WiFi.mode(WIFI_STA);

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD,
        6);

    int attempt = 0;

    while (
        WiFi.status() != WL_CONNECTED &&
        attempt < 40)
    {
        delay(500);
        Serial.print(".");
        attempt++;
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("Wi-Fi connected successfully.");

        Serial.print("ESP32 IP address: ");
        Serial.println(WiFi.localIP());

        Serial.print("Wi-Fi signal strength: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
    }
    else
    {
        Serial.println("Wi-Fi connection failed.");
    }

    Serial.println("========================================");
}

// ========================================================
// WIFI RECONNECTION CHECK
// ========================================================
bool ensureWiFiConnection()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        return true;
    }

    Serial.println();
    Serial.println("Wi-Fi disconnected.");
    Serial.println("Attempting reconnection...");

    WiFi.disconnect(true);
    delay(500);

    connectToWiFi();

    return WiFi.status() == WL_CONNECTED;
}

// ========================================================
// HTTP POST SENSOR DATA
// ========================================================
void sendSensorData()
{
    if (!ensureWiFiConnection())
    {
        Serial.println(
            "Cannot send sensor data because Wi-Fi is offline.");

        return;
    }

    // ------------------------------------------------------
    // READ DHT22
    // ------------------------------------------------------
    float temperatureC = dht.readTemperature();
    float humidityPercent = dht.readHumidity();

    if (
        isnan(temperatureC) ||
        isnan(humidityPercent))
    {
        Serial.println();
        Serial.println("ERROR: Failed to read DHT22.");

        return;
    }

    // ------------------------------------------------------
    // READ ANALOG SENSORS
    // ------------------------------------------------------
    int smokeRaw = analogRead(SMOKE_PIN);
    int gasRaw = analogRead(GAS_PIN);
    int waterRaw = analogRead(WATER_PIN);
    int vibrationRaw = analogRead(VIBRATION_PIN);

    // ------------------------------------------------------
    // CONVERT RAW ADC VALUES
    // ------------------------------------------------------
    float smokePpm = mapFloat(
        smokeRaw,
        0,
        4095,
        0.0,
        300.0);

    float gasPpm = mapFloat(
        gasRaw,
        0,
        4095,
        0.0,
        400.0);

    float waterLevelPercent = mapFloat(
        waterRaw,
        0,
        4095,
        0.0,
        100.0);

    float vibrationLevel = mapFloat(
        vibrationRaw,
        0,
        4095,
        0.0,
        3.0);

    // ------------------------------------------------------
    // READ DIGITAL SENSORS
    // ------------------------------------------------------
    // INPUT_PULLUP ব্যবহারের কারণে button press করলে LOW হবে।
    bool flameDetected =
        digitalRead(FLAME_PIN) == LOW;

    bool motionDetected =
        digitalRead(MOTION_PIN) == LOW;

    // ------------------------------------------------------
    // SIMULATION METADATA
    // ------------------------------------------------------
    int occupancyCount =
        motionDetected ? 5 : 0;

    float batteryVoltage = 4.90;

    // ------------------------------------------------------
    // CREATE JSON PAYLOAD
    // ------------------------------------------------------
    StaticJsonDocument<1024> document;

    document["zone_id"] = ZONE_ID;
    document["device_id"] = DEVICE_ID;

    document["temperature_c"] =
        round(temperatureC * 100.0) / 100.0;

    document["humidity_percent"] =
        round(humidityPercent * 100.0) / 100.0;

    document["smoke_ppm"] =
        round(smokePpm * 100.0) / 100.0;

    document["gas_ppm"] =
        round(gasPpm * 100.0) / 100.0;

    document["water_level_percent"] =
        round(waterLevelPercent * 100.0) / 100.0;

    document["vibration_level"] =
        round(vibrationLevel * 100.0) / 100.0;

    document["flame_detected"] =
        flameDetected;

    document["motion_detected"] =
        motionDetected;

    document["occupancy_count"] =
        occupancyCount;

    document["battery_voltage"] =
        batteryVoltage;

    document["captured_at"] = nullptr;

    String jsonPayload;

    serializeJson(
        document,
        jsonPayload);

    // ------------------------------------------------------
    // SERIAL MONITOR SENSOR OUTPUT
    // ------------------------------------------------------
    Serial.println();
    Serial.println("========================================");
    Serial.println("ROBOFUSION SENSOR READING");
    Serial.println("========================================");

    Serial.print("Device ID: ");
    Serial.println(DEVICE_ID);

    Serial.print("Zone ID: ");
    Serial.println(ZONE_ID);

    Serial.print("Temperature: ");
    Serial.print(temperatureC, 2);
    Serial.println(" C");

    Serial.print("Humidity: ");
    Serial.print(humidityPercent, 2);
    Serial.println(" %");

    Serial.print("Smoke raw ADC: ");
    Serial.println(smokeRaw);

    Serial.print("Smoke: ");
    Serial.print(smokePpm, 2);
    Serial.println(" ppm");

    Serial.print("Gas raw ADC: ");
    Serial.println(gasRaw);

    Serial.print("Gas: ");
    Serial.print(gasPpm, 2);
    Serial.println(" ppm");

    Serial.print("Water raw ADC: ");
    Serial.println(waterRaw);

    Serial.print("Water level: ");
    Serial.print(waterLevelPercent, 2);
    Serial.println(" %");

    Serial.print("Vibration raw ADC: ");
    Serial.println(vibrationRaw);

    Serial.print("Vibration level: ");
    Serial.println(vibrationLevel, 2);

    Serial.print("Flame status: ");
    Serial.println(
        flameDetected ? "DETECTED" : "CLEAR");

    Serial.print("Motion status: ");
    Serial.println(
        motionDetected ? "DETECTED" : "CLEAR");

    Serial.print("Occupancy count: ");
    Serial.println(occupancyCount);

    Serial.print("Battery voltage: ");
    Serial.print(batteryVoltage, 2);
    Serial.println(" V");

    Serial.println();
    Serial.println("JSON PAYLOAD:");
    Serial.println(jsonPayload);

    // ------------------------------------------------------
    // CREATE SECURE HTTPS CLIENT
    // ------------------------------------------------------
    WiFiClientSecure secureClient;

    secureClient.setInsecure();

    // ------------------------------------------------------
    // CREATE HTTP CLIENT
    // ------------------------------------------------------
    HTTPClient http;

    Serial.println();
    Serial.print("Sending POST request to: ");
    Serial.println(API_URL);

    bool started = http.begin(
        secureClient,
        API_URL);

    if (!started)
    {
        Serial.println(
            "ERROR: Could not initialize HTTPS connection.");

        return;
    }

    http.setConnectTimeout(15000);
    http.setTimeout(15000);

    http.addHeader(
        "Content-Type",
        "application/json");

    http.addHeader(
        "Accept",
        "application/json");

    // ------------------------------------------------------
    // SEND HTTP POST
    // ------------------------------------------------------
    int responseCode = http.POST(jsonPayload);

    Serial.print("HTTP response code: ");
    Serial.println(responseCode);

    // ------------------------------------------------------
    // HANDLE SERVER RESPONSE
    // ------------------------------------------------------
    if (responseCode > 0)
    {
        String responseBody = http.getString();

        Serial.println();
        Serial.println("SERVER RESPONSE:");
        Serial.println(responseBody);

        if (
            responseCode == 200 ||
            responseCode == 201)
        {
            Serial.println();
            Serial.println(
                "SUCCESS: Sensor reading saved to FastAPI.");

            Serial.println(
                "SUCCESS: Risk assessment should be generated.");
        }
        else
        {
            Serial.println();
            Serial.println(
                "WARNING: Backend returned a non-success response.");
        }
    }
    else
    {
        Serial.println();
        Serial.print("HTTP request failed: ");

        Serial.println(
            HTTPClient::errorToString(responseCode));
    }

    http.end();

    Serial.println("========================================");
}

// ========================================================
// ESP32 SETUP
// ========================================================
void setup()
{
    Serial.begin(115200);

    delay(1000);

    Serial.println();
    Serial.println("========================================");
    Serial.println("RoboFusion SCS-RG");
    Serial.println("ESP32 Smart Campus Zone Node");
    Serial.println("========================================");

    dht.begin();

    pinMode(SMOKE_PIN, INPUT);
    pinMode(GAS_PIN, INPUT);
    pinMode(WATER_PIN, INPUT);
    pinMode(VIBRATION_PIN, INPUT);

    pinMode(FLAME_PIN, INPUT_PULLUP);
    pinMode(MOTION_PIN, INPUT_PULLUP);

    analogReadResolution(12);

    connectToWiFi();

    sendSensorData();

    lastSendTime = millis();
}

// ========================================================
// ESP32 MAIN LOOP
// ========================================================
void loop()
{
    unsigned long currentTime = millis();

    if (
        currentTime - lastSendTime >=
        SEND_INTERVAL_MS)
    {
        lastSendTime = currentTime;

        sendSensorData();
    }

    delay(50);
}