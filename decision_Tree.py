import pandas as pd
from engine import max_entropy
import time

df = pd.read_csv("Final_Augmented_dataset_Diseases_and_Symptoms.csv")

def symptom_check(symptom):
    result = input(f"Do you have: {symptom} Y/N? ")
    if result == 'Y':
        return 1
    return 0

def leaf_confidence(pool):
    counts = pool["diseases"].value_counts(normalize=True)
    print(counts[counts > 0.0049].head(1), "Symptoms:", len(counts), "Diseases:", len(pool))
    return counts[counts > 0.0049].head(5).to_dict()

def leaf_check(pool, confidence):
    if max(confidence.values()) >= 0.95:
        return True
    if max_entropy(pool)[1] == 0:
        return True
    if len(pool) <= 20:
        return True
    return False

def leaf_print(pool):
    return pool.head()

def tree_builder(pool):
    confidence = leaf_confidence(pool)
    if leaf_check(pool, confidence):
        return {"is leaf": True, "diseases": confidence}
    result = max_entropy(pool)[0]
    positive_pool = pool[pool[result] == 1]
    negative_pool = pool[pool[result] == 0]
    yes_branch = tree_builder(positive_pool)
    no_branch = tree_builder(negative_pool)
    return {"symptom": result, "yes": yes_branch, "no": no_branch}

print(tree_builder(df))