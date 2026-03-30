#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <Servo.h>

#define BUZZER_PIN 22
#define RGB_PIN 23
#define NUM_LEDS 2

Servo servo1;
Servo servo2;
Servo servo3;

Adafruit_NeoPixel pixels(NUM_LEDS, RGB_PIN, NEO_GRB + NEO_KHZ800);

void attach_servo(){
  servo1.attach(0);
  servo2.attach(2);
  servo3.attach(7);
}

void playESCStartup() {
  // 1. Three short rising beeps with Red/Yellow flashes
  int frequencies[] = {1000, 1200, 1500};
  for (int f : frequencies) {
    // Light up Orange-ish for detection
    pixels.fill(pixels.Color(255, 100, 0)); 
    pixels.show();
    
    tone(BUZZER_PIN, f);
    delay(100);
    
    noTone(BUZZER_PIN);
    pixels.clear();
    pixels.show();
    delay(50);
  }

  delay(200); // Short pause before ready signal

  // 2. Long confirmation beep with Green flash
  pixels.fill(pixels.Color(0, 255, 0)); // Solid Green
  pixels.show();
  
  tone(BUZZER_PIN, 2500);
  delay(400);
  
  noTone(BUZZER_PIN);
  pixels.clear();
  pixels.show();
}

void rgb_status() {
  // Purple status pulse

  pixels.setPixelColor(0,pixels.Color(255,255,0));
  pixels.setPixelColor(1,pixels.Color(255,255,0));
  pixels.show();
  delay(500);

  pixels.clear();
  pixels.show();
  delay(500);
}

void read_encoder(){
  if (Serial.available() > 0){

  }
}
void setup() {
  // Initialize LEDs
  pixels.begin();
  pixels.setBrightness(50); // 255 is very bright for desk work!

  // Initialize Buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Run startup sequence
  playESCStartup();
  rgb_status();
  attach_servo();
}

void loop() {
  // Your Mecanum/BDSM control logic goes here
  rgb_status();

  
}