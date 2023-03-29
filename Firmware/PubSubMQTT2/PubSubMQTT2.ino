#include <TBPubSubClient.h>

#include <SPI.h>
#include <Ethernet.h>
#include <string.h>

// Update these with values suitable for your network.
byte mac[]    = {  0x90, 0xA2, 0xDA, 0x0D, 0x34, 0xF9 };
IPAddress ip(192, 168, 10, 123);

EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

const long interval = 2000;
unsigned long previousMillis = 0;
unsigned long mqttDelay = 0;
int count = 0;



/*
 * ###################################################################################################
 *                       F  U  N  C  T  I  O  N      D  E  F  I  N  I  T  I  O  N  S
 * ###################################################################################################
*/


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
    Serial.print("Ethernet ready at  IP:");
    Serial.println(Ethernet.localIP());
  } else {
    Serial.print("IP address issue: ");
    Serial.print(ip);
    Serial.print(". Assigned IP: ");
    Serial.println(Ethernet.localIP());
    while (1);
  }


  //mqttClient.setServer("192.168.1.41", 1883);
  // mqttClient.setServer("192.168.10.132", 1883);
  mqttClient.setServer("192.168.10.132", 1883);
  


  if (mqttClient.connect("arduino-1")) {
    // connection succeeded
    Serial.println("Connected ");
    boolean r= mqttClient.subscribe("test");
    Serial.print("subscribe ");
    Serial.println(r);
  } 
  else {
    // connection failed
    // mqttClient.state() will provide more information
    // on why it failed.
    Serial.print("Connection failed: ");
    Serial.println( mqttClient.state());
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
    Serial.print(". MQTT delay: ");
    Serial.println(mqttDelay);

    for ( int i = 1; i < 2; i++ ) {
      String sTopic = String("channel/") + i + String("/timestamp");
      char cTopic[22] = "";
      sTopic.toCharArray(cTopic, 22);
      Serial.print("Sending to: ");
      Serial.print(cTopic);

      char cPayload[14] = "";
      sprintf(cPayload, "%u", millis());
      Serial.print(". Message: ");
      Serial.println(cPayload);
      
      boolean rc = mqttClient.publish(cTopic, cPayload);
      if (!rc) {
        Serial.print("Publish failed - ");
        int stateValue = mqttClient.state();
        Serial.println( stateValue);
        if (stateValue == 0) {
          Serial.println("Republishing!");
          delay(2000);
          i--;
        } else {
          Serial.println("Stop publishing.");
          while(1);
        }

      }
    }
    

    // call loop
    Serial.print("Call loop - ");
    if ( mqttClient.loop()) {
      Serial.println("Still connected.");
    } else {
      Serial.println("NOT connected any longer!!! Stop further publishing.");
      while (1);  
    }

  }
}
