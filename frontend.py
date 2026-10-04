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
            ui.chat_message("Yes")
        user.user_input("y")
        if "is leaf" in user.current_node:
            with content_container_2:
                ui.chat_message(f"Pretty sure you got {user.current_node["diseases"]}")
                user.severity_check()
                ui.chat_message(f"Your dangerous diseases are {user.dangerous_diseases}")
            content_container_1.clear()
            with content_container_1:
                ui.button()
            return
        if "symptom" in user.current_node.keys():
            symptom = user.current_node["symptom"]
        with content_container_2: 
            ui.chat_message(f"You got {symptom}")
    
    def n_answer_change():
        with content_container_2: 
            ui.chat_message("No")
        user.user_input("n")
        if "is leaf" in user.current_node:
            with content_container_2:
                ui.chat_message(f"Pretty sure you got {user.current_node["diseases"]}")
                user.severity_check()
                ui.chat_message(f"Your dangerous diseases are {user.dangerous_diseases}")
            content_container_1.clear()
            with content_container_1:
                ui.button()
            return
        if "symptom" in user.current_node.keys():
            symptom = user.current_node["symptom"]
        with content_container_2: 
            ui.chat_message(f"You got {symptom}")

    content_container_1 = ui.column()
    content_container_2 = ui.column()

    content_container_1.style('position: fixed; bottom: 0; left: 0; width: 100%; background: white; z-index: 10; display: flex; justify-content: center; gap: 10px; padding: 10px;')
    content_container_2.style('padding-bottom: 100px;') 

    with content_container_1:
        ui.button("yes", on_click = lambda: y_answer_change())
        ui.button("no", on_click = lambda: n_answer_change())
        ui.button("reset", on_click=lambda: reset())

    with content_container_2:
        ui.chat_message(f"You got {symptom}")

    def reset():
        nonlocal user
        user = symptom_check(full_tree)
        content_container_2.clear()
        content_container_1.clear()
        with content_container_1:
            ui.button("yes", on_click=lambda: y_answer_change())
            ui.button("no", on_click=lambda: n_answer_change())
            ui.button("reset", on_click=lambda: reset())
        with content_container_2:
            ui.chat_message(f"You got {user.current_node['symptom']}")

ui.run()