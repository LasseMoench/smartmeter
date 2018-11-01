#include <ESP8266WiFi.h>

#define IRLED 4

int withLed = 0;
int withoutLed = 0;
int stripeCount = 0;
int diff = 0;
WiFiClient client;

const int threshold = 150;

// Wi-Fi Settings
const char* ssid = "Bergernetz"; // your wireless network name (SSID)
const char* password = "GrummelKeks1"; // your Wi-Fi network password
const char* apiIP = "192.168.0.47";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  pinMode(IRLED, OUTPUT);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void loop() {    
    withoutLed = analogRead(A0);
    
    digitalWrite(IRLED, LOW);

    delay(10);

    withLed = analogRead(A0);

    digitalWrite(IRLED, HIGH);

    diff = withoutLed - withLed;

    Serial.print("Without LED: ");
    Serial.println(withoutLed);

    Serial.print("With LED: ");
    Serial.println(withLed);

    Serial.print("Difference is: ");
    Serial.println(diff);

    Serial.println("NEW");

    if(diff < threshold){
      stripeCount++;
    }

    if(diff > threshold && stripeCount > 0){
      stripeCount = 0;

      if (client.connect(apiIP, 8080)){
        // we are connected to the host!
        client.print(String("GET /tick") + " HTTP/1.1\r\n" +
             "Host: " + apiIP + "\r\n" +
             "Connection: close\r\n" +
             "\r\n"
            );
        Serial.println("Reporting tick!");
        while (client.connected()){
          if (client.available()){
            String line = client.readStringUntil('\n');
            Serial.println(line);
          }
        }
        client.stop();
        Serial.println("\n[Disconnected]");
      }else{
        // connection failure
        Serial.println("Connection to tick-API failed!");        
      }
    }

    //Make it more readable by slowing it down
    delay(100);
}
