#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define BUZZER_PIN 22
#define RGB_PIN 23
#define NUM_LEDS 2

Adafruit_NeoPixel pixels(NUM_LEDS, RGB_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200); // Standard baud rate for RP2350 communication
  pixels.begin();
  pixels.setBrightness(100);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Wait for serial to be ready (useful when connecting to Pi 5)
  while (!Serial) {
    delay(10);
  }
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming string until newline (\n)
    String input = Serial.readStringUntil('\n');
    input.trim(); // Clean up whitespace or carriage returns (\r)
 
    if (input == "BEEP") {
      tone(BUZZER_PIN, 2000, 100);
      Serial.println("ACK: BEEP_EXECUTED");
    } 
    else if (input == "RED") {
      pixels.fill(pixels.Color(255, 0, 0));
      pixels.show();
      Serial.println("ACK: LED_RED_EXECUTED");
    }
    else if (input == "LED_OFF") {
      pixels.clear();
      pixels.show();
      Serial.println("ACK: LED_CLEARED");
    }
  }
}