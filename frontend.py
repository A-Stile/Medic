from nicegui import ui
from json_reader import symptom_check
import json

with open('starter_tree.json', 'r', encoding='utf-8') as file:
        full_tree = json.load(file)

@ui.page("/")
def user():
    user = symptom_check(full_tree)
    symptom = user.current_node["symptom"]

    def y_answer_change():
        with content_container_2: 
            ui.chat_message("y")
        user.user_input("y")
        if "is leaf" in user.current_node:
            with content_container_2:
                ui.chat_message(user.current_node["diseases"])
            content_container_1.clear()
        if "symptom" in user.current_node.keys():
            symptom = user.current_node["symptom"]
        with content_container_2: 
            ui.chat_message(f"You got {symptom}")
    
    def n_answer_change():
        with content_container_2: 
            ui.chat_message("n")
        user.user_input("n")
        if "is leaf" in user.current_node:
            with content_container_2:
                ui.chat_message(user.current_node["diseases"])
            content_container_1.clear()
        if "symptom" in user.current_node.keys():
            symptom = user.current_node["symptom"]
        with content_container_2: 
            ui.chat_message(f"You got {symptom}")

    content_container_1 = ui.column()
    content_container_2 = ui.column()

    with content_container_1:
        ui.button("yes", on_click = lambda: y_answer_change())
        ui.button("no", on_click = lambda: n_answer_change())

    with content_container_2:
        ui.chat_message(f"You got {symptom}")

ui.run()