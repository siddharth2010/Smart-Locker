import RPi.GPIO as gpio
import time
import twilioMessaging as twilio
gpio.setmode(gpio.BOARD)

gpio.setup(16, gpio.IN)

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

f = open("user_id", "r")
database = open("database", "r")
db = parse(database)
database.close()
while 1:
	user = f.read()
	if user:
		if gpio.input(16):
			to = db[user]
			twilio.send_tampering_message(to)