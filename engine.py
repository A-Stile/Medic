import pandas as pd
import math

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
def entropy(symptom, pool):
    pool_total = df_entropy(pool, "diseases")
    if pool[symptom].nunique() != 1:
        val = pool.groupby(symptom)["diseases"].value_counts(normalize=True)
        sizes = pool.groupby(symptom).size()
        size_0 = sizes.iloc[0]
        size_1 = sizes.iloc[1]
        column_1 = val.loc[1]
        column_0 = val.loc[0]
        x = pool_entropy(column_0) * size_0/len(pool)
        y = pool_entropy(column_1) * size_1/len(pool)
        return pool_total - (x + y)
    return 0

def max_entropy(pool):
    max = -1
    max_entropy = ""
    for i in pool.columns:
        if i != "diseases":
            x = entropy(i, pool)
            if x > max:
                max = x
                max_entropy = i
    return max_entropy, max