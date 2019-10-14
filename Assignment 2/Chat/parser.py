import re
message = input("Enter message: ")
valid = re.match(r"^@\[([a-z][a-z0-9]*)\]\[(.+)\]$",message)
if valid:
    sender, message = message[2:-1].split("][")
    print(sender)
    print(message)
else:
    print("Wrong input format")