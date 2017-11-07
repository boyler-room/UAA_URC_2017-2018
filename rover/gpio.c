/*  linux sysfs gpio interface wrapper utility
 *    Chandra Boyle
 *
 *  description: simplifies access to gpio
 *
 *  usage:
 *      gpio [pin#]                  - alias of gpio enabled [pin#]
 *      gpio [pin#] enable           - enable pin
 *      gpio [pin#] disable          - disable pin
 *      gpio [pin#] mode             - print and return pin mode
 *      gpio [pin#] mode [mode]      - set pin to mode
 *      gpio [pin#] read             - print and return pin value
 *      gpio [pin#] write [value]    - write value to pin
*/

#include <sys/fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

//check if pin # is enabled
//checks if /sys/class/gpio/gpio# directory exists
//returns 0 if does not exist, 1 if exists, -1 if error
int pinenabled(int pin)
{
    int status;
    struct stat buff;
    char pfile[64];

    status=sprintf(pfile,"/sys/class/gpio/gpio%d",pin);
    if(status<0) return -1;

    status=stat(pfile,&buff);
    if(status<0 && errno==ENOENT) return 0;
    else if(status==0 && S_ISDIR(buff.st_mode)) return 1;
    return -1;
}

//enable pin # for use
//writes # to /sys/class/gpio/export and verifies directory was created
//returns 0 if successful, -1 if error
int enablepin(int pin)
{
    int status,fd;
    char pfile[64]="/sys/class/gpio/export";
    char buff[8];

    status=pinenabled(pin);
    if(status<0) return -1;
    if(status==1) return 0;

    status=sprintf(buff,"%d",pin);
    if(status<0) return -1;

    fd=open(pfile,O_WRONLY);
    if(fd<0) return -1;

    status=write(fd,buff,strlen(buff));
    if(status<0) return -1;
    close(fd);

    status=pinenabled(pin);
    if(status!=1) return -1;
    return 0;
}

//enable pin # for use
//writes # to /sys/class/gpio/unexport and verifies directory was removed
//returns 0 if successful, -1 if error
int disablepin(int pin)
{
    int status,fd;
    char pfile[64]="/sys/class/gpio/unexport";
    char buff[8];

    status=pinenabled(pin);
    if(status<0) return -1;
    if(status==0) return 0;

    fd=open(pfile,O_WRONLY);
    if(fd<0) return -1;

    status=sprintf(buff,"%d",pin);
    if(status<0) return -1;

    status=write(fd,buff,strlen(buff));
    if(status<0) return -1;
    close(fd);

    status=pinenabled(pin);
    if(status!=0) return -1;
    return 0;
}

//check if pin # is configured to input or output
//reads from /sys/class/gpio/gpio#/direction
//returns 0 if input, 1 if output, -1 if error
int getmode(int pin)
{
    int status,fd;
    char pfile[64];
    char buff[4];

    status=pinenabled(pin);
    if(status<=0) return -1;

    status=sprintf(pfile,"/sys/class/gpio/gpio%d/direction",pin);
    if(status<0) return -1;

    fd=open(pfile,O_RDONLY);
    if(fd<0) return -1;

    status=read(fd,buff,4);
    if(status<0) return -1;
    buff[status-1]='\0';
    close(fd);

    if(strcmp(buff,"out")==0) return 1;
    if(strcmp(buff,"in")==0) return 0;
    return -1;
}

//set pin # to input/output
//writes in/out to /sys/class/gpio/gpio#/direction and verifies mode set
//returns 0 if successful, -1 if error
int setmode(int pin, int mode)
{
    int status,fd;
    char pfile[64];
    char buff[4];

    status=pinenabled(pin);
    if(status<=0) return -1;

    status=getmode(pin);
    if(status<0) return -1;
    if(status==mode) return 0;

    status=sprintf(pfile,"/sys/class/gpio/gpio%d/direction",pin);
    if(status<0) return -1;

    fd=open(pfile,O_WRONLY);
    if(fd<0) return -1;

    status=sprintf(buff,"%s",(mode)?"out":"in");
    if(status<0) return -1;

    status=write(fd,buff,strlen(buff));
    if(status<0) return -1;
    close(fd);

    status=getmode(pin);
    if(status!=mode) return -1;
    return 0;
}

//read value of pin #
//reads from /sys/class/gpio/gpio#/value
//returns 0 if low, 1 if high, -1 if error
int readpin(int pin)
{
    int status,fd;
    char pfile[64];
    char val;

    status=pinenabled(pin);
    if(status<=0) return -1;

    status=sprintf(pfile,"/sys/class/gpio/gpio%d/value",pin);
    if(status<0) return -1;

    fd=open(pfile,O_RDONLY);
    if(fd<0) return -1;

    status=read(fd,&val,1);
    if(status<0) return -1;
    close(fd);

    if(val=='1') return 1;
    if(val=='0') return 0;
    return -1;
}

//writes value of pin #
//writes state to /sys/class/gpio/gpio#/value and verifies value set
//returns 0 if successful, -1 if error
int writepin(int pin, int state)
{
    int status,fd;
    char pfile[64];
    char val=state?'1':'0';

    status=pinenabled(pin);
    if(status<=0) return -1;

    status=readpin(pin);
    if(status<0) return -1;
    if(status==state) return 0;

    status=sprintf(pfile,"/sys/class/gpio/gpio%d/value",pin);
    if(status<0) return -1;

    fd=open(pfile,O_WRONLY);
    if(fd<0) return -1;

    status=write(fd,&val,1);
    if(status<0) return -1;
    close(fd);

    status=readpin(pin);
    if(status!=state) return -1;
    return 0;
}

int main(int argc, char* argv[])
{
    int pin,mode,result=0;
    if(argc>1){
        if(sscanf(argv[1],"%d",&pin)<0) return -1;
        switch(argc){
            case 2:
                result=pinenabled(pin);
                break;
            case 3:
                if(strcmp(argv[2],"enable")==0) result=enablepin(pin);
                else if(strcmp(argv[2],"disable")==0) result=disablepin(pin);
                else if(strcmp(argv[2],"mode")==0) result=getmode(pin);
                else if(strcmp(argv[2],"read")==0) result=readpin(pin);
                break;
            case 4:
                if(sscanf(argv[3],"%d",&mode)<0) return -1;
                if(strcmp(argv[2],"mode")==0) result=setmode(pin,mode);
                else if(strcmp(argv[2],"write")==0) result=writepin(pin,mode);
                break;
        }
    }if(result>=0) printf("%d\n",result);
    return result;
}
