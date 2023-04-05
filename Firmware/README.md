# Energi Meter Monitor

This sketch monitors an open collector output on a number of Carlo Gavazzi energy meters Type EM23 DIN and/or Type EM111.

When a FALLING pulse registered on interrupt pin 2, all the defined channelPins are read. The number of milliseconds passed since the Arduino board began running the current instance, is mapped to the activated channelPins, and these datasets are published to a MQTT (Message Queuing Telemetry Transport) broker.

Since tests 

IP address is hardcoded to reduce memory requirement.


## Version history

### **Issues**

**Issue #1**

Connection to ethernet fails after an indefined number of POST requests...

To be investigated: [Reference](https://stackoverflow.com/questions/7432309/arduino-uno-ethernet-client-connection-fails-after-many-client-prints)

There is a bug in the Arduino Ethernet library in v22 (as discussed in Linux/Windows V0022/1.0 Ethernet problem SOLVED).

The solution for me was to use the Ethernet2 library (by Peter from tinker.it). The code needed minor tinkering, but everything appears to be working fine now. I've managed to get over 40000+ HTTP messages sent without any problems. (Occasionally single messages cannot be sent, but this error rate is less than 4%.)

I would slow down the communication rate by increasing time 10x between the messages. Then if you don't get an error between 1000 and 7000 messages, it would probably mean that you are talking too fast to your little Arduino and it's buffer gets an overflow which communication library unfortunately can not recover from. I would also monitor Arduino free bytes in a buffer over serial port after each message. You can also test for this behavior by sending messages as fast as you can from PC, and see if that will freeze your Arduino after a while. If it does, you might consider to deny messages until buffer is above some limit.

**Findings #1**

Number of POST requests seems to be too intensive for the requirements to this project.

Looking into a solution, transferring timestamps for each channel using MQTT (Message Queuing Telemetry Transport)