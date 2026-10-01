from nicegui import ui
from json_reader import symptom_check
import json

with open('starter_tree.json', 'r', encoding='utf-8') as file:
        full_tree = json.load(file)

user = symptom_check(full_tree)

answer = "n"

def on_click(): 
    ui.chat_message("Do you have this symptom?\n" + user.user_input(answer) + answer, name = "Bot", stamp = "now", avatar = "https://robohash.org/a dog with a cigar").classes("my-custom-chat")

with ui.column().classes("w-full h-screen items-center justify-center"):

    ui.label("Slide this")
    ui.label("|")
    ui.label("V")

    with ui.list().props('bordered separator'):
        with ui.slide_item('Do u got this symptom?') as slide_item_1:
            slide_item_1.left('Yes', color='green', on_slide = lambda: (answer == "y", slide_item_1.reset))
            slide_item_1.right('No', color='red', on_slide = lambda: (answer == "n", slide_item_1.reset))

    ui.button('Reset', on_click=slide_item_1.reset)

    button = ui.button("Button")
ui.row().classes('w-full justify-end')

button.on("click", on_click)

