#include <ArduinoJson.h>
#include <Wire.h>
#include "ACS712.h"
#include "ZMPT101B.h"

#define ACS712_PIN A3
#define ZMPT101B_PIN A2

ACS712 ACS(ACS712_PIN, 5.0, 1023, 100);
ZMPT101B voltageSensor(ZMPT101B_PIN, 50.0);

void setup() {
  Serial.begin(9600);
  ACS.autoMidPoint();
  voltageSensor.calibrate();
}

void loop() {
  float current = ACS.mA_AC();
  float voltage = voltageSensor.getVoltageAC();

  StaticJsonDocument<200> doc;
  doc["Voltage"] = voltage;
  doc["Current"] = current;

  String output;
  serializeJson(doc, output);
  Serial.println(output);  // Send to ESP32

  delay(1000);
}
