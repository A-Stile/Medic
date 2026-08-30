import csv

diseases = set()

with open("Final_Augmented_dataset_Diseases_and_Symptoms.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        diseases.add(row["diseases"])

for i in sorted(diseases):
    print("-" + i)