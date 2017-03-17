#!/usr/bin/python
from gpiozero import MCP3008
import RPi.GPIO as GPIO
import time
from time import sleep
import datetime
import os
import pygame
#Libraries necessary to send email using python Jhaymie
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
# takePicture removed to avoid conflict with motion detection script
#Email of the Raspberry Pi Jhaymie
raspaddress = "Pi's Email"
#User's Email address
useraddress = "User's Email"
#Structure of the email
msg = MIMEMultipart()
msg['From'] = raspaddress
msg['To'] = useraddress
msg['Subject'] = "Aegis Alert Message"

#Sensor Variables Tyler
temperature = 0
global img
img = 0
global imgTemp
imgTemp = 0
global toggle
toggle = 0
pygame.init()
pygame.mixer.init()
#Audio and declaration
pygame.mixer.music.load("alarm.mp3")
#Temperature Sensor declaration
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-0000061a7832/w1_slave'
#Setting the GPIO pins
GPIO.setmode(GPIO.BCM) #BCM Matches Pin Numbers on piHAT
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.OUT)

def readLight():
        vref = 3.3
        with MCP3008(channel=7) as reading:
                voltage = reading.value * vref
                print(voltage)
                sleep(0.1)                    
        if(voltage >= 2.0):
                print("Lights on")
                with open("log.txt", "a") as logfile:
                   i = datetime.datetime.now()     
                   lightAlert = "%s Lights On \n" % i 
                   logfile.write(lightAlert)
                   time.sleep(0.1)
                   light = "ON"
                time.sleep(0.1)
        else:
                light = "OFF"
        return light
def readDoor():                               
        if(GPIO.input(18) == 0):
                print("Door Closed")
                time.sleep(0.1)
                door = "CLOSED"               
        elif(GPIO.input(18) == 1):
                print("Door Open")
                if(GPIO.input(22) == 0):
                        #emailSender("Door opened when locked")
                        audioAlertOn()
                door = "OPEN"
                with open("log.txt", "a") as logfile:
                   i = datetime.datetime.now()     
                   doorAlert = "%s Door opened \n" % i 
                   logfile.write(doorAlert)
                   time.sleep(0.1)
        return door     
def readSmoke():                                  
        if(GPIO.input(27) == 0):
                print("Smoke Detected")
                smoke = "YES"
                #emailSender("Smoke Detected")
                audioAlertOn()
                with open("log.txt", "a") as logfile:
                   i = datetime.datetime.now()     
                   smokeAlert = "%s Smoke Detected \n" % i 
                   logfile.write(smokeAlert)
                   time.sleep(0.1)
        else:
            smoke = "NO"
        return smoke;   
def readLock():        
        if(GPIO.input(22) == 1):
                print("Unlocked")
                lock = "UNLOCKED"
                time.sleep(0.1)
                                
        elif(GPIO.input(22) == 0):
                print("Locked")
                time.sleep(0.1)
                lock = "LOCKED"
        return lock

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()      
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
                
def audioAlertOn():
        global toggle
        if(toggle == 0):
                toggle = 1
                pygame.mixer.music.play()
        sleep(0.1)

def audioAlertOff():
    global toggle
    pygame.mixer.music.stop()
    toggle = 0
    sleep(0.1)

def webView(smoke,tmp,lock,door,light):
        f = open('/var/www/html/index.php','w')
        i = tmp
        message = """
<!DOCTYPE html>
<html>
<head><title>Project: Aegis</title>
<link class="jsbin" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1/themes/base/jquery-ui.css" rel="stylesheet" type="text/css" />
<script class="jsbin" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
<script class="jsbin" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.0/jquery-ui.min.js"></script>
<meta charset=utf-8 />
<style>
<?php
if (isset($_POST['camera']))
{
exec('sudo python camerano.py');
}
if (isset($_POST['lock']))
{
exec('sudo python lock.py');
}
?>
div.container {
    width: 100%%;

}

header{
    margin: auto;
    height: 100px;
    width: 1000px;
    border-style: solid;
    padding: 1em;
    color: black;
    background: rgba(204, 204, 204, 0.5);
    clear: left;
    text-align: center;
    
}

footer{
    margin: auto;
    height: 800px;
    width: 1000px;
    border-style: solid;
    padding: 1em;
    color: black;
    background: rgba(204, 204, 204, 0.5);
    clear: left;
    text-align: left;
    
}

nav {
    
    max-width: 160px;
    margin: 0;
    padding: 1em;
}

nav{
    list-style-type: none;
    padding: 100;
    
}
   
nav{
    text-decoration: none;
}

article {
    margin-left: 500px;
    border-left: 1px solid gray;
    padding: 0em;
}

body {
  margin-bottom: 120px;
}
</style>
<body style="background-color:grey;">

<div class="container">

<header>
   <h1>Camera Screenshot</h1>
</header>

<article>
<img src="pic.jpg" alt="Latest Screenshot" style="width:400px;height:300px;">
<form method="post">
    <button name="camera">Capture Screenshot</button>
    </form>
</article>

<nav>
    <table border="2">
    <tr>
    <th colspan = "2">Sensor Readings</th>
    </tr>

    <tr>    
    <td>Smoke</td>
    <td>%s</td>
    </tr>

    <tr>
    <td>Temperature</td>
    <td>%s°C</td>
    </tr>

    <tr>
    <td>Lock State</td>
    <td>%s</td>
    </tr>

    <tr>
    <td>Door Status State</td>
    <td>%s</td>
    </tr>

    <tr>
    <td>Light Status State</td>
    <td>%s</td>
    </tr>
    </table>
    <form method="post">
    <button name="lock">Lock/Unlock door</button>
    </form>
</nav>

<footer>
<pre>

<img src="" alt="Images" id="imageReplace"/><br />
<a href="#" onclick="changeImage('1Temp.jpg');">Past Photo 1</a>
<a href="#" onclick="changeImage('2Temp.jpg');">Past Photo 2</a>
<a href="#" onclick="changeImage('3Temp.jpg');">Past Photo 3</a>

</pre>

<script>
function changeImage(element) {
document.getElementById('imageReplace').src = element;
}
</script>

</footer>

</div>


</body>
</html>
    """%(smoke,tmp,lock,door,light)
        f.write(message)
        f.close()
        
def logWriter(alert):
        with open("log.txt", "a") as logfile:
                   logfile.write(alert)
                   time.sleep(0.1)
def emailSender(body):
        #Jhaymie
        msg.attach(MIMEText(body, 'plain'))
        #Parameters for GMail Server
        server = smtplib.SMTP('SMTP Server', 587)
        # Security function needed to connect to the Gmail server to protect the password.
        server.starttls()
        #Password of Raspberry Pi's Email
        server.login(raspaddress, "Pi's Email Password")
        #Sending the email
        text = msg.as_string()
        server.sendmail(raspaddress, useraddress, text)
        server.quit()
while True:
                if(GPIO.input(23) == 0):
                        audioAlertOff()
                print(read_temp())
                smoke = readSmoke()
                temperature = 25.0
                lock = readLock()
                door = readDoor()
                light = readLight()
                webView(smoke,temperature,lock,door,light)
