/* UAA-URC 2018: Arduinos -> Analog Sensor Access
 *  by Chandra Boyle
 *
 *  for Arduino Pro ATMEGA328,5V,16MHz;
 *  
 */
 
#include <Wire.h>

#define I2C_ADDR 0x06
byte cmd=0;
void recv(int);
void req();

#define TSPIN 0
#define MSPIN 1
#define LED0P 2
#define LED1P 3

void setup()
{
	pinMode(LED0P,OUTPUT);
	pinMode(LED1P,OUTPUT);

	Wire.begin(I2C_ADDR);
}

void loop()
{
	
}

void recv(int ct)
{
	byte data;
	switch(cmd=Wire.read()){
		
	}
}

void req()
{
	Wire.write(0x1F);
}
