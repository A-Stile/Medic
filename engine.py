import pandas as pd
import math
import time

df = pd.read_csv("Final_Augmented_dataset_Diseases_and_Symptoms.csv")

def pool_entropy(pool):
    total = 0
    for i in pool:
        total += -(i*math.log2(i))
    return total

def df_entropy(pool, column):
    total = 0
    for i in pool[column].value_counts(normalize=True):
        total += -(i*math.log2(i))
    return total

total_rows = len(df)
pool_total = df_entropy(df, "diseases")
def entropy(symptom):
    if df[symptom].nunique() != 1:
        val = df.groupby(symptom)["diseases"].value_counts(normalize=True)
        sizes = df.groupby(symptom).size()
        size_0 = sizes.iloc[0]
        size_1 = sizes.iloc[1]
        column_1 = val.loc[1]
        column_0 = val.loc[0]
        x = pool_entropy(column_0) * size_0/len(df)
        y = pool_entropy(column_1) * size_1/len(df)
        return pool_total - (x + y)
    return 0

max = -1
max_entropy = ""
for i in df.columns:
    if i != "diseases":
        x = entropy(i)
        if x > max:
            max = x
            max_entropy = i
print("Max Entropy:", max, max_entropy)