#include <TBPubSubClient.h>

#include <SPI.h>
#include <Ethernet.h>
#include <string.h>

// Update these with values suitable for your network.
byte mac[]    = {  0x90, 0xA2, 0xDA, 0x0D, 0x34, 0xF9 };
IPAddress ip(192, 168, 10, 123);

EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

const long interval = 8000;
unsigned long previousMillis = 0;
unsigned long mqttDelay = 0;
int count = 0;


/*
 * ###################################################################################################
 *                       F  U  N  C  T  I  O  N      D  E  F  I  N  I  T  I  O  N  S
 * ###################################################################################################
*/

void mqttConnect() {
  Serial.print("Attempt to connect - ");
  if (mqttClient.connect("arduino-2")) {
    // connection succeeded
    Serial.println("Connected.");
    boolean r= mqttClient.subscribe("test");
    Serial.println("subscribe ");
    Serial.println(r);
  } 
  else {
    // connection failed
    // mqttClient.state() will provide more information
    // on why it failed.

    Serial.print("Connection failed: ");
    mqttConnetFaiure( mqttClient.state());
    while (1);
  }
  
}

void mqttConnetFaiure(int returnCode) {
  Serial.print(returnCode);
  switch (returnCode) {
    case -4 :
      Serial.println (" - MQTT_CONNECTION_TIMEOUT - the server didn't respond within the keepalive time");
      break;
    case -3 :
      Serial.println (" - MQTT_CONNECTION_LOST - the network connection was broken");
      break;
    case -2 :
      Serial.println (" - MQTT_CONNECT_FAILED - the network connection failed");
      break;
    case -1 :
      Serial.println (" - MQTT_DISCONNECTED - the client is disconnected cleanly");
      break;
    case 0 :
      Serial.println (" - MQTT_CONNECTED - the client is connected");
      break;
    case 1 :
      Serial.println (" - MQTT_CONNECT_BAD_PROTOCOL - the server doesn't support the requested version of MQTT");
      break;
    case 2 :
      Serial.println (" - MQTT_CONNECT_BAD_CLIENT_ID - the server rejected the client identifier");
      break;
    case 3 :
      Serial.println (" - MQTT_CONNECT_UNAVAILABLE - the server was unable to accept the connection");
      break;
    case 4 :
      Serial.println (" - MQTT_CONNECT_BAD_CREDENTIALS - the username/password were rejected");
      break;
    case 5 :
      Serial.println (" - MQTT_CONNECT_UNAUTHORIZED - the client was not authorized to connect");
      break;
  }
}

/*
 * ###################################################################################################
 * ###################################################################################################
 * ###################################################################################################
 *                       S E T U P      B e g i n
 * ###################################################################################################
 * ###################################################################################################
 * ###################################################################################################
 */

void setup()
{
    // Open serial communications and wait for port to open:

  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.println("Hit [Enter] to start!");
  while (!Serial.available()) {
    ;  // In order to prevent unattended execution, wait for [Enter].
  }

  Ethernet.begin(mac, ip);
  // Allow the hardware to sort itself out
  delay(1500);
  if (ip == Ethernet.localIP()) {
    Serial.print("Ethernet ready at assighed IP address:");
    Serial.println(Ethernet.localIP());
  } else {
    Serial.print("IP address issue! programmed IP address: ");
    Serial.print(ip);
    Serial.print(". Assigned IP address: ");
    Serial.println(Ethernet.localIP());
    while (1);
  }


  Serial.println("Setting server and port.");
  mqttClient.setServer("192.168.10.132", 1883);
//  mqttClient.setServer("test.mosquitto.org", 1883);
//  mqttClient.setServer("91.121.93.94", 1883);
  
  // mqttConnect();
  if (mqttClient.connect("arduino-1")) {
    // connection succeeded
    Serial.println("Connected ");
    boolean r= mqttClient.subscribe("test");
    Serial.println("subscribe ");
    Serial.println(r);
  } 
  else {
    // connection failed
    // mqttClient.state() will provide more information
    // on why it failed.
    Serial.println("Connection failed ");
  }


}

/*
 * ###################################################################################################
 * ###################################################################################################
 * ###################################################################################################
 *                       L O O P     B e g i n
 * ###################################################################################################
 * ###################################################################################################
 * ###################################################################################################
 */

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time a message was sent
    previousMillis = currentMillis;


    count++;
    Serial.println();
    Serial.print("Count: ");
    Serial.print(count);
    Serial.print(". MQTT publish delay (millisec.): ");
    Serial.println(mqttDelay);

  
    for ( int i = 1; i < 8; i++ ) {
      String sTopic = String("channel/") + i + String("/timestamp");
      char cTopic[22] = "";
      sTopic.toCharArray(cTopic, 22);
      Serial.print("Sending message to topic: ");
      Serial.print(cTopic);

      char cPayload[14] = "";
      sprintf(cPayload, "%u", millis());
      Serial.print(". Message / Payload: ");
      Serial.println(cPayload);
      
      boolean rc = mqttClient.publish(cTopic, cPayload);
      if (!rc) {
        Serial.print("Publish failed - ");
        if ( mqttClient.loop()) {
          Serial.println("Still connected...");
        } else {
          Serial.println("Disconnected!");
          mqttConnect();
          Serial.print("Re publishing last Message / Pauload to topic: ");
          Serial.print(cTopic);
          Serial.print(". Message / Payload: ");
          Serial.print(cPayload);

          boolean rc = mqttClient.publish(cTopic, cPayload);
          if (!rc) {
            Serial.println(" - Failed!");
          } else {
            Serial.println(" - Successfull!");
          }


          while (1);  
        }

      }

      if (mqttDelay != 0)
        delay(mqttDelay);
    }
    // call loop
    Serial.print("Call loop - ");
    if ( mqttClient.loop()) {
      Serial.println("Still connected.");
    } else {
      Serial.println("NOT connected any longer!!! Stop further publishing.");
      while (1);  
    }

/*
    mqttClient.disconnect();
    if ( mqttClient.loop()) {
      Serial.println("ERROR - Disconnection failed!!!");
      while (1);
    } else {
      Serial.println("Disconnection successfull.");
    }
 */


  }


  Serial.println("Disconnecting from Broker!");
  mqttClient.disconnect();
  if ( mqttClient.loop()) {
    Serial.println("ERROR - Disconnection failed!!!");
  } else {
    Serial.println("Disconnection successfull.");
  }

  while (1); 
 
  }
