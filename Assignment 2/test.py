import re
message = input()
a = re.match(r"@\[([a-z][a-z0-9]+)\]\[.+\]",message)
if a:
    print(message)
else:
    print("wrong")