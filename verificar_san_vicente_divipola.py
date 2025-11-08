import csv

print("Puestos de San Vicente del Caguan en DIVIPOLA:")
print("-" * 80)

with open('divipola.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['municipio'] == 'SAN VICENTE DEL CAGUAN':
            print(f"Zona {row['zz']:4} | {row['puesto']}")
