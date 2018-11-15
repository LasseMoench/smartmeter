#include <ArduinoJson.h>

#include <Wire.h>  // Only needed for Arduino 1.6.5 and earlier
#include "SSD1306Wire.h" // legacy include: `#include "SSD1306.h"`

#include <ESP8266WiFi.h>

// Initialize the OLED display using Wire library
SSD1306Wire  display(0x3c, D2, D1);
// SH1106 display(0x3c, D3, D5);

const char* ssid = "Bergernetz"; // your wireless network name (SSID)
const char* password = "GrummelKeks1"; // your Wi-Fi network password
const char* apiIP = "192.168.0.38";
WiFiClient client;
StaticJsonBuffer<300> jsonBuffer;
String result;

void setup() {
  Serial.begin(115200);
  
  // Initialising the UI will init the display too.
  display.init();

  display.flipScreenVertically();
  display.setFont(ArialMT_Plain_10);

  display.clear();
  
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  display.setFont(ArialMT_Plain_16);
  display.drawString(64, 24, "Connecting...");
  display.display();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
  display.clear();
}

void loop() {
  if (client.connect(apiIP, 80)){
    // we are connected to the host!
    client.print(String("GET /lcdinfo") + " HTTP/1.1\r\n" +
         "Host: " + apiIP + "\r\n" +
         "Connection: close\r\n" +
         "\r\n"
        );
    Serial.println("Request info from API!");
    while (client.connected()){
      if (client.available()){
        result = client.readStringUntil('\n');
        Serial.println(result);
      }
    }

    JsonObject& root = jsonBuffer.parseObject(result);

    String wh = root["daily_power"];
    String current = root["current_power"];

    if(!root.success()) {
      Serial.println("parseObject() failed");
    }
    
    display.clear();
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.drawString(0, 0, "Now:");
    display.setTextAlignment(TEXT_ALIGN_RIGHT);
    display.drawString(128, 0, current + "W");
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.drawString(0, 16, "Today:");
    display.setTextAlignment(TEXT_ALIGN_RIGHT);
    display.drawString(128, 16, wh + "Wh");
    float daily = root["daily_power"];
    float cost = 0.0002775 * daily;
    String coststr = String(cost);
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.drawString(0, 32, "Cost:");
    display.setTextAlignment(TEXT_ALIGN_RIGHT);
    display.drawString(128, 32, coststr + "€");
    display.display();
    client.stop();
    Serial.println("\n[Disconnected]");

  }else{
    // connection failure
    Serial.println("Connection to tick-API failed!");        
  }
  delay(30000);
}
