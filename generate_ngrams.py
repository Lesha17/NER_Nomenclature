lines = []

with open("lines2.txt") as input:
    for line in input:
        line = line.lower()
        line = line.replace("\r", "")
        line = line.replace("\n", "")
        lines.append(line)

n = 3

with open("ngrams.txt", "w") as output:
    for line in lines:
        tokens = line.split(" ")
        for i in range(0, len(tokens)):
            min_n = min(n, len(tokens) - i)
            for j in range(1, min_n + 1):
                words = tokens[i:i+j]
                ngram = ""
                for w in words:
                    to_append = ""
                    if ngram:
                        to_append = " "
                    to_append += w
                    ngram += to_append
                output.write(ngram + "\n")