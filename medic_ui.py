import asyncio
import json
import os

from nicegui import run, ui

# ───────────── ENGINE CONTRACT: swap this block for your own engine ─────────────
# Question node: {"symptom": str, "n": int, "yes": node, "no": node}
# Leaf node:     {"leaf": [[disease, confidence 0-1], ...], "n": int,
#                 "urgency": "emergency" | "urgent" | "routine"}
# "n" = number of patient rows still in the candidate pool at that node.

with open('ui_tree.json', 'r', encoding='utf-8') as file:
    DEMO_TREE = json.load(file)

class Engine:
    def __init__(self, path='ui_tree.json'):
        if os.path.exists(path):
            with open(path) as f:
                self.tree = json.load(f)
        else:
            self.tree = DEMO_TREE
        self.total = self.tree['n']
        self.red_flags = {
            "chest tightness":     "Chest tightness or pressure can be a sign of a heart attack.",
            "sharp chest pain":    "Chest pain can be a sign of a heart attack or another life-threatening problem.",
            "shortness of breath": "Shortness of breath can signal a heart or lung emergency.",
            "difficulty breathing": "Trouble breathing can be life-threatening.",
            "fainting":            "Fainting can signal a heart or brain emergency.",
            "seizures":            "A seizure needs emergency evaluation, especially a first one or one that does not stop.",
            "vomiting blood":      "Vomiting blood can mean serious internal bleeding.",
            "slurring words":      "Slurred speech can be a sign of a stroke. Note the time symptoms started.",
            "focal weakness":      "Sudden weakness on one side of the body can be a sign of a stroke.",
            "throat swelling":     "Swelling in the throat can block your airway.",
        }

    def step(self, node, yes):
        return node['yes' if yes else 'no']

    def red_flag(self, symptom):
        return self.red_flags.get(symptom)


def phrase(symptom):
    return f'Are you experiencing {symptom}?'


engine = Engine()
# ────────────────────────────── END ENGINE CONTRACT ──────────────────────────────

URGENCY = {
    'emergency': ('Get emergency care now', 'Call 911 or go to the nearest emergency room.'),
    'urgent': ('See a clinician today', 'Visit urgent care or call your doctor for a same-day appointment.'),
    'routine': ('Book a regular visit', 'Schedule a visit with your doctor in the coming days.'),
}
DISCLAIMER = 'Medic estimates likely conditions and urgency. It is not a diagnosis and does not suggest treatment.'

FONT = ('<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700'
        '&display=swap" rel="stylesheet">')

CSS = """
:root{--ink:#12303B;--mist:#E8F1F3;--teal:#1B7A86;--red:#C42B3F;--amber:#D4821F;--green:#2E8B6B;--muted:#5C7882}
body{font-family:'Instrument Sans',system-ui,sans-serif;color:var(--ink);background:var(--mist)}
.shell{width:100%;max-width:640px;margin:0 auto;padding:28px 16px 40px;gap:20px}
.brand{gap:10px}.brand-icon{font-size:30px;color:var(--teal)}
.brand-name{font-size:26px;font-weight:700;letter-spacing:-.02em}
.card{width:100%;background:#fff;border-radius:22px;padding:28px;gap:16px;
      box-shadow:0 10px 30px rgba(18,48,59,.10)}
.swap{animation:swap .35s ease-out}
@keyframes swap{from{opacity:0;transform:translateX(26px)}to{opacity:1;transform:none}}
.meta{font-size:14px;color:var(--muted)}
.track{width:100%;height:10px;border-radius:6px;background:#DCE8EB;overflow:hidden}
.fill{height:100%;border-radius:6px;background:var(--teal);transition:width .8s cubic-bezier(.2,.8,.2,1)}
.q-num{font-size:14px;font-weight:600;color:var(--teal)}
.q-text{font-size:28px;line-height:1.25;font-weight:600;letter-spacing:-.01em;max-width:30ch}
.answers{gap:12px;width:100%}
.answer-btn{flex:1;min-height:56px;font-size:18px;font-weight:600;border-radius:14px}
.sec{font-size:15px;font-weight:600;margin-top:4px}
.cond{width:100%;gap:6px}
.cond-row{width:100%;justify-content:space-between}
.cond-name{font-weight:500}.cond-pct{font-weight:700;font-variant-numeric:tabular-nums}
.urg-title{font-size:30px;font-weight:700;line-height:1.15;letter-spacing:-.02em}
.urg-advice{font-size:17px;line-height:1.45}.strong{font-weight:700}
.urg-emergency{border-top:6px solid var(--red)}
.urg-urgent{border-top:6px solid var(--amber)}
.urg-routine{border-top:6px solid var(--green)}
.urg-emergency .fill{background:var(--red)}.urg-urgent .fill{background:var(--amber)}
.urg-routine .fill{background:var(--green)}
.alarm{background:var(--red);color:#fff;animation:swap .35s ease-out,pulse 1.8s ease-out 0.4s infinite}
.alarm .q-text,.alarm .urg-advice{color:#fff}
.alarm-icon{font-size:44px}
.call-btn{min-height:56px;font-size:20px;font-weight:700;border-radius:14px;background:#fff!important;color:var(--red)!important}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(196,43,63,.5)}100%{box-shadow:0 0 0 22px rgba(196,43,63,0)}}
.fine{font-size:13px;color:var(--muted);line-height:1.4}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:480px){.q-text{font-size:24px}.card{padding:22px}}
"""


def grow(el, pct):
    """Animate a bar to pct: it was created at its old width; CSS transition does the rest."""
    ui.timer(0.05, lambda: el.style(f'width:{pct}%'), once=True)


@ui.page('/')
def index():
    ui.add_head_html(FONT)
    ui.add_css(CSS)
    ui.colors(primary='#1B7A86', negative='#C42B3F')

    s = {'node': engine.tree, 'trail': [], 'text': None, 'alarm': None, 'pct': 0}

    # ---- actions -------------------------------------------------------------
    async def load_text():
        node = s['node']
        if 'leaf' not in node and not s['alarm']:
            s['text'] = None            # shows skeleton while the phrasing layer works
            stage.refresh()
            try:
                s['text'] = await asyncio.wait_for(run.io_bound(phrase, node['symptom']), 3)
            except Exception:           # LLM slow or down: triage must never block on it
                s['text'] = f"Are you experiencing {node['symptom']}?"
        stage.refresh()

    async def answer(yes):
        node = s['node']
        if yes and (msg := engine.red_flag(node['symptom'])):
            s['alarm'] = msg
            stage.refresh()
            return
        s['trail'].append(node)
        s['node'] = engine.step(node, yes)
        await load_text()

    async def back():
        if s['alarm']:
            s['alarm'] = None
        elif s['trail']:
            s['node'] = s['trail'].pop()
        await load_text()

    async def restart():
        s.update(node=engine.tree, trail=[], alarm=None, pct=0)
        await load_text()

    # ---- views ---------------------------------------------------------------
    def narrowing(node):
        pct = round(100 * (1 - node['n'] / engine.total))
        ui.label(f"{node['n']:,} of {engine.total:,} records in the dataset still match").classes('meta')
        with ui.element('div').classes('track'):
            fill = ui.element('div').classes('fill').style(f"width:{s['pct']}%")
        grow(fill, pct)
        s['pct'] = pct

    def question_view(node):
        with ui.element('div').classes('card swap'):
            narrowing(node)
            ui.label(f"Question {len(s['trail']) + 1}").classes('q-num')
            if s['text'] is None:
                ui.skeleton('text', width='90%', height='34px')
                ui.skeleton('text', width='60%', height='34px')
            else:
                ui.label(s['text']).classes('q-text')
            with ui.row().classes('answers'):
                busy = s['text'] is None
                ui.button('Yes', on_click=lambda: answer(True)).props('unelevated no-caps').classes('answer-btn').set_enabled(not busy)
                ui.button('No', on_click=lambda: answer(False)).props('outline no-caps').classes('answer-btn').set_enabled(not busy)
            if s['trail']:
                ui.button('Back', icon='arrow_back', on_click=back).props('flat no-caps')

    def result_view(node):
        level = node.get('urgency', 'urgent')
        title, advice = URGENCY[level]
        with ui.element('div').classes(f'card swap urg-{level}'):
            ui.label(title).classes('urg-title')
            ui.label(advice).classes('urg-advice')
            ui.label('Most likely conditions').classes('sec')
            for name, conf in node['leaf']:
                with ui.column().classes('cond'):
                    with ui.row().classes('cond-row'):
                        ui.label(name).classes('cond-name')
                        ui.label(f'{conf:.0%}').classes('cond-pct')
                    with ui.element('div').classes('track'):
                        fill = ui.element('div').classes('fill').style('width:0%')
                    grow(fill, round(conf * 100))
            narrowing(node)
            ui.label(DISCLAIMER).classes('fine')
            with ui.row():
                ui.button('Start over', icon='restart_alt', on_click=restart).props('unelevated no-caps')
                if s['trail']:
                    ui.button('Back', icon='arrow_back', on_click=back).props('flat no-caps')

    def alarm_view():
        with ui.element('div').classes('card alarm'):
            ui.icon('emergency').classes('alarm-icon')
            ui.label('This may be an emergency').classes('urg-title')
            ui.label(s['alarm']).classes('urg-advice')
            ui.label('Call 911 or go to the nearest emergency room now.').classes('urg-advice strong')
            ui.button('Call 911', icon='call', on_click=lambda: ui.navigate.to('tel:911')).props('unelevated no-caps').classes('call-btn')
            ui.button('Go back and change my answer', on_click=back).props('flat no-caps color=white')

    @ui.refreshable
    def stage():
        node = s['node']
        if s['alarm']:
            alarm_view()
        elif 'leaf' in node:
            result_view(node)
        else:
            question_view(node)

    # ---- layout --------------------------------------------------------------
    with ui.column().classes('shell'):
        with ui.row().classes('brand items-center'):
            ui.icon('monitor_heart').classes('brand-icon')
            ui.label('Medic').classes('brand-name')
        stage()
        ui.label(DISCLAIMER).classes('fine')

    ui.timer(0, load_text, once=True)


ui.run(title='Medic', favicon='🩺', reload=False, show=False, host = "0.0.0.0")