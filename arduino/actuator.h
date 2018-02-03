/* UAA-URC 2018: Arduinos -> Linear Actuator Control
 *  by Chandra Boyle
 *
 *  for Arduino Pro ATMEGA328,5V,16MHz;
 *      Pololu VNH5019 Driver Boards;
 *      Firgelli Feedback Rod Linear Actuators
 */

/*DIR | A | B | STATE
   0  | 0 | 0 | OFF(BRAKE GND)
   1  | 0 | 1 | ON(RETRACT)
   2  | 1 | 0 | ON(EXTEND)
   3  | 1 | 1 | OFF(BRAKE VCC)
*/

/*CMD | READ RESPONSE | WRITE ACTION | WRITE ARGS
 0x00 | 0x1F          | STOP         | (ACTUATOR 0:LO,1:HI)
 0x01 | LOWER SPD     | SET LO SPD   | SPEED,(DIR)
 0x02 | UPPER SPD     | SET UP SPD   | SPEED,(DIR)
 0x03 | LOWER DIR     | SET LO DIR   | DIR
 0x04 | UPPER DIR     | SET UP DIR   | DIR
 0x05 | LOWER POT     | LOWER TO POS | POSL,POSH,(SPD)
 0x06 | UPPER POT     | UPPER TO POS | POSL,POSH,(SPD)
 0x80 | SEND 0x1F     | NONE
 0x81 | LOWER SPD     | NONE
 0x82 | UPPER SPD     | NONE
 0x83 | LOWER DIR     | NONE
 0x84 | UPPER DIR     | NONE
 0x85 | LOWER POT     | NONE
 0x86 | UPPER POT     | NONE
 0x87 | LO LIMIT SW   | NONE
 0x88 | UP LIMIT SW   | NONE
*/
 
#include <Wire.h>

#define I2C_ADDR 0x05

byte cmd=0;

void recv(int);
void req();

//upper actuator
#define UP_APIN 7//dir signal a
#define UP_BPIN 6//dir signal b
#define UP_DPIN 5//pwm drive
#define UP_PPIN 1//potentiometer
#define UP_SW1 9//limit switch
//lower actuator
#define LO_APIN 4//dir signal a
#define LO_BPIN 2//dir signal b
#define LO_DPIN 3//pwm drive
#define LO_PPIN 0//potentiometer
#define LO_SW1 8//limit switch

#define MIN_SPD 0x1F

byte up_dir=0, lo_dir=0;
byte up_spd=0, lo_spd=0;
int up_pot, lo_pot;
int up_targ=-1, lo_targ=-1;

void setup()
{
	pinMode(UP_APIN,OUTPUT);
	pinMode(UP_BPIN,OUTPUT);
	pinMode(LO_APIN,OUTPUT);
	pinMode(LO_BPIN,OUTPUT);
	pinMode(UP_SW1,INPUT_PULLUP);
	pinMode(LO_SW1,INPUT_PULLUP);
	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);
}

void loop()
{
	if(digitalRead(UP_SW1)==LOW){
		up_spd=0;up_dir=0;up_targ=-1;
	}if(digitalRead(LO_SW1)==LOW){
		lo_spd=0;lo_dir=0;lo_targ=-1;
	}
	up_pot=analogRead(UP_PPIN);
	lo_pot=analogRead(LO_PPIN);
	if(up_targ>=0){
		if(up_spd<=MIN_SPD){
			up_targ=-1;
			up_spd=0;
		}if(up_pot==up_targ){
			up_targ=-1;
			up_dir=3;
		}else if(up_pot>up_targ){
			if(up_dir!=1) up_dir=1;
		}else{
			if(up_dir!=2) up_dir=2;
		}
	}if(lo_targ>=0){
		if(lo_spd<=MIN_SPD){
			lo_targ=-1;
			lo_spd=0;
		}if(lo_pot==lo_targ){
			lo_targ=-1;
			lo_dir=3;
		}else if(lo_pot>lo_targ){
			if(lo_dir!=1) lo_dir=1;
		}else{
			if(lo_dir!=2) lo_dir=2;
		}
	}
	switch(up_dir){
	  case 0:
		digitalWrite(UP_APIN,LOW);
		digitalWrite(UP_BPIN,LOW);
		break;
	  case 1:
		digitalWrite(UP_APIN,LOW);
		digitalWrite(UP_BPIN,HIGH);
		break;
	  case 2:
		digitalWrite(UP_APIN,HIGH);
		digitalWrite(UP_BPIN,LOW);
		break;
	  case 3:
		digitalWrite(UP_APIN,HIGH);
		digitalWrite(UP_BPIN,HIGH);
		break;
	}analogWrite(UP_DPIN,up_spd);
	switch(lo_dir){
	  case 0:
		digitalWrite(LO_APIN,LOW);
		digitalWrite(LO_BPIN,LOW);
		break;
	  case 1:
		digitalWrite(LO_APIN,LOW);
		digitalWrite(LO_BPIN,HIGH);
		break;
	  case 2:
		digitalWrite(LO_APIN,HIGH);
		digitalWrite(LO_BPIN,LOW);
		break;
	  case 3:
		digitalWrite(LO_APIN,HIGH);
		digitalWrite(LO_BPIN,HIGH);
		break;
	}analogWrite(LO_DPIN,lo_spd);
	//delay(500);
}

void recv(int ct)
{
	byte data;
	switch(cmd=Wire.read()){
	  case 0x00:
		if(Wire.available()){
			switch(Wire.read()){
			  case 0x00:
				lo_spd=0;lo_dir=0;lo_targ=-1;
				break;
			  case 0x01:
				up_spd=0;up_dir=0;up_targ=-1;
				break;
			}
		}else{
			lo_spd=0;lo_dir=0;lo_targ=-1;
			up_spd=0;up_dir=0;up_targ=-1;
		}
		break;
	  case 0x01:
		if(Wire.available()){
			if((data=Wire.read())>MIN_SPD) lo_spd=data;
			if(Wire.available()){
				if((data=Wire.read())<0x04) lo_dir=data;
			}
		}
		break;
	  case 0x02:
		if(Wire.available()){
			if((data=Wire.read())>MIN_SPD) up_spd=data;
			if(Wire.available()){
				if((data=Wire.read())<0x04) up_dir=data;
			}
		}
		break;
	  case 0x03:
		if(Wire.available()){
			if((data=Wire.read())<0x04) lo_dir=data;
		}
		break;
	  case 0x04:
		if(Wire.available()){
			if((data=Wire.read())<0x04) up_dir=data;
		}
		break;
	  case 0x05:
		if(Wire.available()>=2){
			lo_targ=Wire.read();
			if((data=Wire.read())<0x04){
				lo_targ|=((int)data)<<8;
			}else lo_targ=-1;
			if(Wire.available()){
				if((data=Wire.read())>MIN_SPD) lo_spd=data;
			}
		}
		break;
	  case 0x06:
		if(Wire.available()>=2){
			up_targ=Wire.read();
			if((data=Wire.read())<0x04){
				up_targ|=((int)data)<<8;
			}else up_targ=-1;
			if(Wire.available()){
				if((data=Wire.read())>MIN_SPD) up_spd=data;
			}
		}
		break;
	}while(Wire.available()) Wire.read();
}

void req()
{
	byte data[4]={0x00,0x00,0x00,0x00};
	switch(cmd){
	  case 0x00:
	  case 0x80:
		Wire.write(0x1F);
		break;
	  case 0x01:
	  case 0x81:
		Wire.write(lo_spd);
		break;
	  case 0x02:
	  case 0x82:
		Wire.write(up_spd);
		break;
	  case 0x03:
	  case 0x83:
		Wire.write(lo_dir);
		break;
	  case 0x04:
	  case 0x84:
		Wire.write(up_dir);
		break;
	  case 0x05:
	  case 0x85:
		data[0]=(byte)lo_pot;
		data[1]=(byte)(lo_pot>>8);
		Wire.write(data,2);
		break;
	  case 0x06:
	  case 0x86:
		data[0]=(byte)up_pot;
		data[1]=(byte)(up_pot>>8);
		Wire.write(data,2);
		break;
	  case 0x87:
		Wire.write((byte)(digitalRead(LO_SW1)==LOW));
		break;
	  case 0x88:
		Wire.write((byte)(digitalRead(UP_SW1)==LOW));
		break;
	}
}
