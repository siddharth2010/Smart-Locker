import os
import SimpleMFRC522

f = open("database", "a")
reader = SimpleMFRC522.SimpleMFRC522()
print "Please scan your ID"
id, text = reader.read()
mobile = raw_input("Enter your mobile no.")
f.writelines(id + ' ' + mobile)
f.close()