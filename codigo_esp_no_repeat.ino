#include <ESP8266WiFi.h>  // For ESP wireless
#include <PubSubClient.h> // For MQTT

const String MACHINE_NAME = "machinename" // Machine name, lowercase, used for MQTT topics

// WiFi network - must be replaced for testing
const char* ssid = "VISA";
const char* password = "v1s4!@#$";

// Pin values
const int but_pin_red = D1;
const int but_pin_green = D5;
const int but_pin_yellow = D3;

// Raspberry Pi's IP address
const char* mqtt_server = "105.112.124.30";

// Keeps track of previous value
int prev_state_red = -1;
int prev_state_green = -1;
int prev_state_yellow = -1;

// Initializes the esp_client
WiFiClient esp_client;
PubSubClient client(esp_client);

// Auxiliary timer variables
long now = millis();
long last_measure = 0;
long last_send = 0;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connects to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());
}

void connect_mqtt() {
  // Loop until connected to MQTT server
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("ESP8266Client_" + MACHINE_NAME)) {
      Serial.println("connected");  
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(but_pin_red, INPUT);
  pinMode(but_pin_green, INPUT);
  pinMode(but_pin_yellow, INPUT);
  
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.loop()) {
    connect_mqtt();
  }

  now = millis();
  if (now - last_measure > 1000) {
    last_measure = now;
    
    // Reads buttons
    int but_state_red = digitalRead(but_pin_red);
    int but_state_green = digitalRead(but_pin_green);
    int but_state_yellow = digitalRead(but_pin_yellow);

    if(but_state_red    != prev_state_red    ||
       but_state_green  != prev_state_green  ||
       but_state_yellow != prev_state_yellow ||
       now - last_send > 1000 * 60 * 3) { // 3 minute keep-alive

      last_send = now;

      // Converts to char for MQTT publishing
      char but_char_red[5], but_char_green[5], but_char_yellow[5];
      sprintf(but_char_red, "%d", but_state_red);
      sprintf(but_char_green, "%d", but_state_green);
      sprintf(but_char_yellow, "%d", but_state_yellow);

      // Publishes values
      client.publish("/" + MACHINE_NAME + "/light/red", but_char_red);
      client.publish("/" + MACHINE_NAME + "/light/green", but_char_green);
      client.publish("/" + MACHINE_NAME + "/light/yellow", but_char_yellow);

      prev_state_red = but_state_red;
      prev_state_green = but_state_green;
      prev_state_yellow = but_state_yellow;
    }


    Serial.print("Red light: ");
    Serial.print(but_state_red);
    Serial.println("");
    Serial.print("Green light: ");
    Serial.print(but_state_green);
    Serial.println("");
    Serial.print("Yellow light: ");
    Serial.print(but_state_yellow);
    Serial.println("");
  }
}