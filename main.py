import RPi.GPIO as GPIO
import time
import datetime
import SimpleMFRC522
import twilio
from gpiozero import Buzzer
from gpiozero import LED
import paho.mqtt.client as mqtt

reader = SimpleMFRC522.SimpleMFRC522() # Reader for RFID Scanner
GPIO.cleanup()

GPIO.setmode(GPIO.BOARD) # Set GPIO Mode
control_pins = [32,36,38,40] # Control pins for motor

# Initialise control pins
for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

GPIO.setup(10,GPIO.IN)
GPIO.setup(15,GPIO.OUT)
GPIO.output(16,GPIO.IN)

buzzer = Buzzer(15)
led = LED(18)

# Initialise pins for Stepper motor
halfstep_seq = [
  [1,0,0,0],
  [1,1,0,0],
  [0,1,0,0],
  [0,1,1,0],
  [0,0,1,0],
  [0,0,1,1],
  [0,0,0,1],
  [1,0,0,1]
]

def rotate_motor(dir):
"""
Function for Rotating Motor.
dir : int : specifies the rotation direction
rtype : None
"""
	if(dir==1):	
		for _ in range(200):
		  for halfstep in range(8):
		    for pin in range(4):
		      GPIO.output(control_pins[pin], halfstep_seq[7-halfstep][pin])
		    time.sleep(0.001)
	else:
		for _ in range(200):
		  for halfstep in range(8):
		    for pin in range(4):
		      GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])		
		    time.sleep(0.001)
 
#set GPIO Pins for ultrasonic sensors
GPIO_TRIGGER = 35
GPIO_ECHO = 33
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
"""
Function for Rotating Motor.
:type dir : int : specifies the rotation direction
                  1 refers to CW, while 0 means ACW.
rtype : None
"""
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def check_empty():
"""
Function for Checking whether the locker is empty.
rtype : Bool : True if empty, False if not
"""
  dist = distance()
  if dist < 20:
    return False
  else:
    return True

def beep():
"""
Beeps the buzzer.
rtype : Null
"""
  buzzer.on()
  time.sleep(0.5)
  buzzer.off()

def parse(database):
  """
  Parses the database file
  type database: file
  rtype: dict (with 'id' as key and 'mobile no.' as value)
  """
  db = {}
  for line in database:
    line = line.strip()
    line = line.split(' ')
    db[line[0]] = line[1]
  return db

# the main function
def main():
  database = open("database", "r")
  db = parse(database)
  database.close()
  client = mqtt.Client("info")
  client.connect("localhost", 1883)
  f = open("user_id", "w")
  assigned_id = None
  while 1:
    id, text = reader.read()
    if assigned_id == None or id == assigned_id:
      led.off() # Turn the LED off.
      beep()
      if assigned_id == None:
        to = db[id]
        twilio.send_assign_message(to)
        assigned_id = id
      f.write(id)
      client.publish("locker/0", "Last opened at " + str(datetime.datetime.now()), qos = 0, retain = True )
      rotate_motor(0)

    counter = 0
    while 1:
      # Check if the door is closed or not. if closed, then lock it, else, keep checking
      is_closed = GPIO.input(10)
      if is_closed:
        buzzer.off()
        rotate_motor(1) # Lock the door
        # if somehow the door is locked but not closed, then turn on the buzzer
        is_closed = GPIO.input(10)
        if not is_closed:
          buzzer.on() # Start the Buzzer
          rotate_motor(0) # Then open the lock
          continue
        counter=0
        # In case the locker is empty, and locked, then unassign it
        if check_empty():
          assigned_id = None
          to = db[id]
          client.publish("locker/0", "Unassigned", qos = 0, retain = True )
          twilio.send_unassign_message(to)
          led.on() # Turn the led on.
        break
      else :
        # if however the door is left open for quite some time, then turn on the buzzer, until the door is closed
        if counter >= 5000 :
          buzzer.on()
        time.sleep(0.001)
        counter += 1
        continue

  GPIO.cleanup() # Clean GPIO Pins

if __name__=='__main__':
  main()
