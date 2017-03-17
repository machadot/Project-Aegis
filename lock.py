#Imports necessary functions
import RPi.GPIO as GPIO
import time
from time import sleep
#Sets the GPIO of the solenoid
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)

def setLock():
		#Checks if solenoid is unlocked
        if(GPIO.input(22) == 1):
				#Sets solenoid to locked
                GPIO.output(22, 0)
                time.sleep(0.1)
         #Checks if solenoid is locked                       
        elif(GPIO.input(22) == 0):
				#Sets solenoid to unlocked
                GPIO.output(22, 1)
                time.sleep(0.1)

setLock()