import csv

with open('divipola.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'MONTA' in row['municipio']:
            print(f"Municipio en DIVIPOLA: '{row['municipio']}'")
            break
