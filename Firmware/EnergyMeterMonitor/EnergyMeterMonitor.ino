/* Verify (compile) for Arduino Ethernet
 *
 * 
 * This sketch monitors an open collector output on a number of Carlo Gavazzi energy meters Type EM23 DIN and/or Type EM111.
 * When a FALLING pulse registered on interrupt pin 2, all the defined channelPins are read. 
 * The number of milliseconds passed since the Arduino board began running the current instance, 
 * is mapped to the activated channelPins, and these datasets are published to a MQTT (Message Queuing Telemetry Transport) broker.
 * 
 * IP address is hardcoded to reduce memory requirement.
 * 
 * In "ARDUINO_UNO_DEBUG" mode the private network is 192.168.10.0 and the Arduino IP Address is: 192.168.10.123.
 * In none "ARDUINO_UNO_DEBUG" (for the sketch to run one the Arduino Ethernet REV3 board), the privat network is
 * 192.168.10.0 and Ardhino IP address is 192.168.10.146
 *
 * Define ARDUINO_UNO_DEBUG will compile the sketch for the Arduino UNO board and arduino ethernet shield. 
 * If ARDUINO_UNO_DEBUG is undefined, the sketch will be compiled for the Arduino Ethernet REV3 board.
 * 
 * The code is made specific for the Arduino Ethernet REV3 board.
 * 
 * Created:
 * 2023-04-02
 */

#define SKETCH_VERSION "Energy Meter Monitor for Carlo Gavazzi energy meter Type EM23 and/or Type EM111 DIN - V3.0.0"

/*
 * 
 **** Ardhino Ethernet REV3 Pin definition/layout:***
 * Pin  0: Serial RX
 * Pin  1: Serial TX
 * Pin  2: Interrupt pin for counting pulses.
 * Pin  3: Channel pin 1: Input for reading Open Collector output on Type EM111 DIN energy meter (1000 pulses per kWh (PPKW))
 * Pin  4: Chip select (CS) for SD card (Disable SD card if not used - Undefined SD card could cause problems with the Ethernet interface.)
 * Pin  5: Channel pin 2: Input for reading Open Collector output on Type EM111 DIN energy meter (1000 pulses per kWh)
 * Pin  6: Channel pin 3: Input for reading Open Collector output on Type EM111 DIN energy meter (1000 pulses per kWh)
 * Pin  7: Channel pin 4: Input for reading Open Collector output on Type EM111 DIN energy meter (1000 pulses per kWh)
 * Pin  8: Channel pin 5: Input for reading Open Collector output on Type EM111 DIN energy meter (1000 pulses per kWh)
 * Pin  9: Default defined as LED_BUILTIN. NOT WORKING because LED_BUILTIN is defined as PIN 13. Now re-defined as PIN 17 
 * Pin 10: Chip select (CS) for SD card.
 * Pin 11: SPI.h library for MOSI (Master In Slave Out) 
 * Pin 12: SPI.h library for MISO (Master Out Slave In)
 * Pin 13: SPI.h library for SCK (Serial Clock).
 * Pin 14 (A0): Channel pin 6: Input for reading Open Collector output on Type EM23 DIN energy meter (100 pulses per kWh)
 * Pin 15 (A1): Channel pin 7: Input for reading Open Collector output on Type EM23 DIN energy meter (100 pulses per kWh)
 * Pin 16 (A2): Channel pin 8: Input for reading Open Collector output on Type EM23 DIN energy meter (100 pulses per kWh)
 * Pin 17 (A3): Defined as LED_PIN used for indicating pulsecounts and other activity (powerUP or failure to bootup) 
 *              (Replaces defective  definition of LED_BUILTIN)
 * Pin 18 (A4):
 * Pin 19 (A5):
 */

/* 
 * The interruptfunction has a catch: It enters a "while pin 2 is low" loop, and stays there, until the interrupt is released. 
 * Se further explanation in the README.md file.
 * 
 * Publishing issue: Tests has shown, that connection to the MQTT broker are lost every now an then, but 
 * up til a couple of publish re-tries with a 5 seconds break, solves that problem. However since pulses might still arrive
 * in the period required to re-establish MQTT connection, a buffer is required to logged timestamps.
 * 
 * First take: a dubble array of unsigned long int's: timeStamps[number of channerls][number of timestamps] will hold the
 * timestamps collected.
 */

/*
 * Compilation notes:
 * Before adding vars and function for MQTT publishing
 * Sketch uses 13212 bytes (40%) of program storage space. Maximum is 32256 bytes.
 * Global variables use 647 bytes (31%) of dynamic memory, leaving 1401 bytes for local variables. Maximum is 2048 bytes.
 * 
 * After adding vars and process to buffer timestamps:
 * Sketch uses 13342 bytes (41%)
 * Global variables use 807 bytes (39%), leaving 1241.
 * 
 */
#include <SPI.h> 
#include <Ethernet.h>


/*
 * ######################################################################################################################################
 *                                    D E F I N E    D E G U G G I N G
 * ######################################################################################################################################
*/
#define DEBUG        // If defined (remove // at line beginning) - Sketch await serial input to start execution, and print basic progress 
                       //   status informations
#define WEB_DEBUG    // (Require definition of  DEBUG!) If defined - print detailed informatins about web server and web client activities
#define COUNT_DEBUG  // (Require definition of  DEBUG!)If defined - print detailed informatins about puls counting. 
#define ARDUINO_UNO_DEBUG  //If defined: MAC and IP address will be set accoring to the MAC address for the Arduino Ethernet shield
/*
 * ######################################################################################################################################
 *                       C  O  N  F  I  G  U  T  A  B  L  E       D  E  F  I  N  I  T  I  O  N  S
 * ######################################################################################################################################
*/

#define NO_OF_CHANNELS 8                                                   // Number of energy meters connected
#define NO_OF_TIMESTAMPS 5                                                 // Define how many timestamps
const int channelPin[NO_OF_CHANNELS] = {3,5,6,7,8,14,15,16};               // define which pin numbers are used for input channels
const int PPKW[NO_OF_CHANNELS] = {1000,1000,1000,1000,1000,100,100,100};    //Variable for holding Puls Pr Kilo Watt (PPKW) for each channel (energy meter)

#define INTERRUPT_PIN 2
#define CHIP_SELECT_PIN 4
#define LED_BUILTIN 17
#define MQTT_CLIENT_PORT_NUMBER 1883

/*
 * Incapsulate strings i a P(string) macro definition to handle strings in PROGram MEMory (PROGMEM) to reduce valuable memory  
  MACRO for string handling from PROGMEM
  https://todbot.com/blog/2008/06/19/how-to-do-big-strings-in-arduino/
  max 149 chars at once ...
*/

char p_buffer[150];
#define P(str) (strcpy_P(p_buffer, PSTR(str)), p_buffer)

                                                                    #ifdef ARDUINO_UNO_DEBUG  //overwrite configuration for Arduino Ethernet REV3 board
                                                                      byte mac[] = { 0x90, 0xA2, 0xDA, 0x0D, 0x34, 0xF9};  //Ethernet Shield (Arduino)
                                                                      IPAddress ArduinoIP( 192, 168, 10, 123); // Ethernet Shield (Arduino)
                                                                      IPAddress mqttClientIP( 192, 168, 10, 132);          // IP address for energy-webhook server
                                                                    #else
byte mac[] = { 0x90, 0xA2, 0xDA, 0x0D, 0x63, 0x15 };  // MAC address for Arduino Ethernet REV3 board
IPAddress ArduinoIP( 192, 168, 10, 146);                     // IP address for Arduino Ethernet REV3 board
IPAddress mqttClientIP( 192, 168, 10, 132);          // IP address for energy-webhook server
                                                                    #endif


/*
 *  #####################################################################################################################
 *                       V  A  R  I  A  B  L  E      D  E  F  I  N  A  I  T  O  N  S
 *  #####################################################################################################################
 */

#define ERR_ETHERNET_BEGIN 1
#define INPUT_OUTPUT_STRING_LENGHT 134

EthernetClient webHookClient;

unsigned long timeStamps[NO_OF_CHANNELS][NO_OF_TIMESTAMPS];
unsigned long led_buildin_ON_at;
boolean led_buildin_ON;

/*
 *  #####################################################################################################################
 *                       V o l a t i l e    g l o b a l   v a r e i a b l e
 *                                   used in interruptfunction
 *  #####################################################################################################################
 */
volatile boolean channelState[NO_OF_CHANNELS];
volatile unsigned long volTimeStamp[NO_OF_CHANNELS];

/*
 * ###################################################################################################
 *                       F  U  N  C  T  I  O  N      D  E  F  I  N  I  T  I  O  N  S
 * ###################################################################################################
*/

/*
 * >>>>>>>>>>>>>>   P U B L I S H    T O     E N N R G Y - M Q T T H O O K    <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
 *
*/


/*
 * >>>>>>>>>>>>>>>>>>>>>>>>>>> i n d i c a t e  E r r o r   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
 */

void indicateError( int errPoint, int returnValue) {

                                                              #ifdef DEBUG
                                                                Serial.print(P("Error at: "));
                                                                Serial.print(errPoint);
                                                                Serial.print(P(". Return Valune: "));
                                                                Serial.println(returnValue);
                                                              #endif
  while (true) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(250);
    digitalWrite(LED_BUILTIN, LOW);
    delay(250);
  }


}

/*
 * ######################  I N T E R R U P T    F U N C T I O N  -   B E G I N     ####################
 * When a LOW pulse triggers the interrupt pin, status on all channels are read, as long as the pulse on the interrupt pin 
 * is active (LOW). If a channel has been read as active (LOW), it will not be re-read.
 * Explanation:
 * When more pulses from different energy meters arrives and overlapping each other, the trigger pulse will stay active LOW 
 * as long as one of the pulses from the energy meters are low. 
 * When reading the channels over and over, without re-reading channels that allready has been read active (low), 
 * pulses on all channels will be read
 */

void readChannelPins() {
  unsigned long time = millis();
  while ( !digitalRead(INTERRUPT_PIN)) { 
    for (int ii = 0; ii < NO_OF_CHANNELS; ii++) {
      if (channelState[ii]) {
        channelState[ii] = digitalRead(channelPin[ii]);
        volTimeStamp[ii] = time;
      }
    }
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
void setup() {
  Serial.begin(115200);
  Serial.println(P(SKETCH_VERSION));
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
                                                              #ifdef DEBUG
                                                              while (!Serial) {
                                                                ;  // Wait for serial connectionsbefore proceeding
                                                              }
                                                              Serial.println(P("Hit [Enter] to start!"));
                                                              while (!Serial.available()) {
                                                                ;  // In order to prevent unattended execution, wait for [Enter].
                                                              }
                                                              #endif
  for (int ii = 0; ii < NO_OF_CHANNELS; ii++) {  // Initialize input channels - and counter flags
    pinMode(channelPin[ii], INPUT_PULLUP);
    channelState[ii] = HIGH;
    volTimeStamp[ii] = 0;
    for (int yy = 0; yy < NO_OF_TIMESTAMPS; yy++) {
      timeStamps[ii][yy] = 0;
    }
  }

/*
 * Initiate Ethernet connection
 * Static IP is used to reduce sketch size
 */
  Ethernet.begin(mac, ArduinoIP);
                                                              #ifdef DEBUG
                                                              if (ArduinoIP == Ethernet.localIP()) {
                                                                Serial.print(P("Ethernet ready at assighed IP address:"));
                                                                Serial.println(Ethernet.localIP());
                                                              } else {
                                                                Serial.print(P("IP address issue! programmed IP address: "));
                                                                Serial.print(ArduinoIP);
                                                                Serial.print(P(". Assigned IP address: "));
                                                                Serial.println(Ethernet.localIP());
                                                              }
                                                              #endif
  if (ArduinoIP != Ethernet.localIP())
    indicateError(ERR_ETHERNET_BEGIN, 0);

/*
 * Initialise MQTT client 
 */
 

 /*
  * Initialize and arm interrupt.
  */ 
  pinMode(INTERRUPT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), readChannelPins, FALLING);

  /*
   * Initialize variable for blinking LED_BUILTIN on every puls registration
   */
  led_buildin_ON_at = millis();

  digitalWrite(LED_BUILTIN, LOW);
  led_buildin_ON = false;
                                                              #ifdef DEBUG
                                                              Serial.print(P("Setup successfull - enter loop, and wait for activity."));
                                                              #endif
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
  

  /*
  * >>>>>>>>>>>>>>>>>>>>>>>>>  C o u n i n g    m o d u l e   -   B E G I N     <<<<<<<<<<<<<<<<<<<<<<<
  * >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  * 
  */

 
  for (int ii = 0; ii < NO_OF_CHANNELS; ii++) {
    if ( !channelState[ii] ) {
      int yy = 0;
      while (timeStamps[ii][yy] != 0 and yy < NO_OF_TIMESTAMPS)
        yy++;
      timeStamps[ii][yy] = volTimeStamp[ii];
      channelState[ii] = HIGH;

      led_buildin_ON_at = millis();
      digitalWrite(LED_BUILTIN, HIGH);
      led_buildin_ON = true;
                                                         #ifdef COUNT_DEBUG
                                                              int channel = ii + 1;
                                                              if ( channel == 1)
                                                                Serial.println();
                                                                Serial.print(P("Pulse registrated for channel "));
                                                                Serial.print( channel);
                                                                Serial.print(P(" at: "));
                                                                Serial.println(volTimeStamp[ii]);
                                                              #endif
    }
  }

  /*
  * <<<<<<<<<<<<<<<<<<<<<<<<<  C o u n i n g    m o d u l e   -   E N D      >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  * <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  */

//  for (int ii = 0; ii < NO_OF_CHANNELS; ii++) {
  

  if (led_buildin_ON) {
    if (millis() > led_buildin_ON_at + (long)150) {
      digitalWrite(LED_BUILTIN, LOW);
      led_buildin_ON = false;
    }
  }
}
