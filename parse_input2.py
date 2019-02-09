lines = []

with open("lines2.txt") as input:
    for line in input:
        line = line.replace("\r", "")
        line = line.replace("\n", "")
        print(line)
        lines.append(line)

int n = 3;

with open("output2.txt", "w") as output:
    for line in lines:
        tokens = line.split(" ")
        for i in range(0, len(tokens) - 2):
            min_n = min(n, len(tokens) - i)
            for j in range(1, min_n):
                words = tokens[i:i+j]
                ngram = ""
                for w in words:
                    ngram += w + " "
                    output.write(ngram + "\n")