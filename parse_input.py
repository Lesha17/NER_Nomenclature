lines = []

with open("lines2.txt") as input:
    for line in input:
        line = line.replace("\r", "")
        line = line.replace("\n", "")
        lines.append(line)

with open("output2.txt", "w") as output:
    for line in lines:
        tokens = line.split(" ")
        for token in tokens:
            output.write(token + "\n")
  

