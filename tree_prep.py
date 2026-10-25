"""One-off prep: annotate starter_tree.json with 'n', then convert leaves for the UI.
Run from the repo folder:  python tree_prep.py   ->  writes ui_tree.json
"""
import json
import sys

import pandas as pd

sys.setrecursionlimit(10000)

CSV = "Final_Augmented_dataset_Diseases_and_Symptoms.csv"
URGENT_AT = 3.0        # your call: score above this -> "urgent"
EMERGENCY_AT = 6.0     # your call: score above this -> "emergency"
UNKNOWN_SEVERITY = 7   # your call: severity used for diseases missing from the file


def add_n(node, pool):
    """Route the dataset through the existing tree so every node gets its pool size."""
    node["n"] = len(pool)
    if "is leaf" in node:
        return
    has = pool[node["symptom"]] == 1
    add_n(node["yes"], pool[has])
    add_n(node["no"], pool[~has])


def urgency(pairs, sev):
    score = max(conf * sev.get(name, UNKNOWN_SEVERITY) for name, conf in pairs)
    if score > EMERGENCY_AT:
        return "emergency"
    if score > URGENT_AT:
        return "urgent"
    return "routine"


def convert(node, sev):
    if "is leaf" in node:
        pairs = sorted(node["diseases"].items(), key=lambda kv: kv[1], reverse=True)
        return {"leaf": [[name, conf] for name, conf in pairs],
                "n": node["n"],
                "urgency": urgency(pairs, sev)}
    return {"symptom": node["symptom"], "n": node["n"],
            "yes": convert(node["yes"], sev), "no": convert(node["no"], sev)}


if __name__ == "__main__":
    tree = json.load(open("starter_tree.json", encoding="utf-8"))
    sev = json.load(open("disease_severities", encoding="utf-8"))
    add_n(tree, pd.read_csv(CSV))
    with open("ui_tree.json", "w", encoding="utf-8") as f:
        json.dump(convert(tree, sev), f)
    print("root n:", tree["n"])