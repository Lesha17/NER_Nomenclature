lines = []

with open("lines.txt") as input:
    for line in input:
        line = line.replace("\r", "")
        line = line.replace("\n", "")
        print(line)
        lines.append(line)

with open("output.txt", "w") as output:
    output.write("INPUT:text\tINPUT:part\n")
    for line in lines:
        tokens = line.split(" ")
        for token in tokens:
            l = line + "\t" + token + "\n"
            output.write(l)
  

