/* UAA-URC 2018: Arduinos -> Stepper Motor Control
 *  by Chandra Boyle
 *
 *  for Arduino Pro ATMEGA328,5V,16MHz;
 *      Pololu DRV8825 Driver Boards;
 *      NEMA-17 Steppers
 */
 
#include <Wire.h>

#define I2C_ADDR 0x05
byte cmd=0;
void recv(int);
void req();


