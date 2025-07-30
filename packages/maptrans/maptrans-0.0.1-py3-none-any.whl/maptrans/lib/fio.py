import csv


def saveCSV(file, content):
    with open(file, 'w', newline='', encoding='utf-8-sig') as nfile:
        nf = csv.writer(nfile)
        nf.writerows(content)


def getCSV(file, width=3, startLine=1, startCol=0):
    cf = csv.reader(open(file, encoding='utf-8-sig'))
    result = [[] for _ in range(width - startCol)]

    count = 0
    for line in cf:
        if count >= startLine:
            for i in range(startCol, width):
                x = line[i].strip()
                try:
                    result[i - startCol].append(float(x))
                except ValueError:
                    result[i - startCol].append(x)
        count += 1

    return result
