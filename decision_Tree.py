import pandas as pd
from engine import max_entropy

df = pd.read_csv("Final_Augmented_dataset_Diseases_and_Symptoms.csv")

asked_symptoms = []

def symptom_check(symptom):
    asked_symptoms.append(symptom)
    result = input(f"Do you have: {symptom} Y/N? ")
    if result == 'Y':
        return 1
    return 0

def leaf_confidence(pool):
    counts = pool["diseases"].value_counts(normalize=True)
    print(counts[counts > 0.0049].head(5))
    return 0

def leaf_check(pool):
    if leaf_confidence(pool) >= 0.95:
        return True
    if len(asked_symptoms) == len(df):
        return True
    if max_entropy(pool)[1] == 0:
        return True
    if len(pool) <= 20:
        return True
    return False

def leaf_print(pool):
    return pool.head()

def tree_builder(pool):
    if leaf_check(pool) == False:
        result = max_entropy(pool)[0]
        positive_pool = pool[pool[result] == 1]
        negative_pool = pool[pool[result] == 0]
        print("cut into 2 pools", leaf_confidence(positive_pool))
        tree_builder(positive_pool)
        print("finsihed positive pools")
        tree_builder(negative_pool)
        print("finished all pools")
    return leaf_print(pool)

print(tree_builder(df))