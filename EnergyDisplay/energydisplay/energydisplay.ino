#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>

// Construct an LCD object and pass it the 
// I2C address, width (in characters) and
// height (in characters). Depending on the
// Actual device, the IC2 address may change.
LiquidCrystal_I2C lcd(0x3F, 16, 2);

const char* ssid = "Bergernetz"; // your wireless network name (SSID)
const char* password = "GrummelKeks1"; // your Wi-Fi network password
const char* apiIP = "192.168.0.38";
WiFiClient client;
String result;
int lcdpos = 0;

void setup() {
  Serial.begin(115200);

  // The begin call takes the width and height. This
  // Should match the number provided to the constructor.
  lcd.begin(16,2);
  lcd.init();

  // Turn on the backlight.
  lcd.backlight();

  // Move the cursor characters to the right and
  // zero characters down (line 1).
  lcd.setCursor(0, 0);

  // Print HELLO to the screen, starting at 5,0.
  lcd.print("Connecting...");
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
}

void loop() {
  lcd.backlight();
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
    client.stop();
    Serial.println("\n[Disconnected]");
    float wh = result.toFloat();
    int lcdpos = 13 - result.length();
    lcd.clear();
    lcd.setCursor(lcdpos,0);
    lcd.print(result);
    lcd.setCursor(14,0);
    lcd.print("Wh");
    float cost = 0.0002775 * wh;
    String coststr = String(cost);    
    lcdpos = 12 - coststr.length();
    lcd.setCursor(lcdpos, 1);
    lcd.print(coststr);
    lcd.setCursor(13, 1);
    lcd.print("EUR");
  }else{
    // connection failure
    Serial.println("Connection to tick-API failed!");        
  }
  delay(5000);
  lcd.backlight();
  delay(30000);
}
