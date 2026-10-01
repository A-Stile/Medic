import json
import random

user_inputs = ["y", "n"]

with open('starter_tree.json', 'r', encoding='utf-8') as file:
        full_tree = json.load(file)

with open('disease_severities', 'r', encoding='utf-8') as file:
        severity_list = json.load(file)

class symptom_check():

    def __init__(self, current_node):
        self.user_answers = []
        self.current_node = current_node
        self.dangerous_diseases = []

    def check(self):
        if "symptom" in self.current_node.keys():
            y = self.current_node["symptom"]
            return y
        elif "is leaf" in self.current_node.keys():
            return self.current_node["diseases"]

    def user_input(self, answer):
        x = answer
        self.user_answers.append((self.check(),x))
        if x == "y":
            if "yes" in self.current_node.keys():
                self.current_node = self.current_node["yes"]
        elif x == "n":
            if "no" in self.current_node.keys():
                self.current_node = self.current_node["no"]
        return self.current_node["symptom"]

    def severity_check(self):
        print(self.current_node["diseases"])
        for disease, freq in self.current_node["diseases"].items():
            if freq * severity_list[disease] * 100 > 500:
                self.dangerous_diseases.append(disease)
        return self.dangerous_diseases