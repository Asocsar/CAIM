f = open('./vocabulary.txt', 'r', encoding='utf8')
maxfr = 0
weights_doc = {}
for line in f:
    word, frec = line.split()
    weights_doc[word] = int(frec)
    if int(frec) > maxfr:
        maxfr = int(frec)
print(weights_doc)