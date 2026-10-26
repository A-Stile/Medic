import asyncio
import json
import os
import re
 
from nicegui import run, ui
 
# ───────────── ENGINE CONTRACT: swap this block for your own engine ─────────────
# Question node: {"symptom": str, "n": int, "yes": node, "no": node}
# Leaf node:     {"leaf": [[disease, confidence 0-1], ...], "n": int,
#                 "urgency": "emergency" | "urgent" | "routine"}
# "n" = number of patient rows still in the candidate pool at that node.
 
with open('ui_tree.json', 'r', encoding='utf-8') as file:
    DEMO_TREE = json.load(file)
 
 
class Engine:
    def __init__(self, path='tree.json'):
        if os.path.exists(path):
            with open(path) as f:
                self.tree = json.load(f)
        else:
            self.tree = DEMO_TREE
        self.total = self.tree['n']
        self.red_flags = {'chest pain': 'Chest pain can be a sign of a heart attack.'}
 
    def step(self, node, yes):
        return node['yes' if yes else 'no']
 
    def red_flag(self, symptom):
        return self.red_flags.get(symptom)
 
engine = Engine()
# ────────────────────────────── END ENGINE CONTRACT ──────────────────────────────
 
URGENCY = {
    'emergency': ('Get emergency care now', 'Call 911 or go to the nearest emergency room.'),
    'urgent': ('See a clinician today', 'Visit urgent care or call your doctor for a same-day appointment.'),
    'routine': ('Book a regular visit', 'Schedule a visit with your doctor in the coming days.'),
}
# Plain-language subtexts: {"symptoms": {name: text}, "diseases": {name: text}}
try:
    with open('definitions.json', 'r', encoding='utf-8') as f:
        DEFS = json.load(f)
except OSError:
    DEFS = {'symptoms': {}, 'diseases': {}}
 
 
def clean(name):
    """Dataset artifact: duplicate columns come through as 'regurgitation.1'."""
    return re.sub(r'\.\d+$', '', name)
 
 
def blurb(kind, name):
    return DEFS.get(kind, {}).get(name) or DEFS.get(kind, {}).get(clean(name))
 
 
DISCLAIMER = 'Medic estimates likely conditions and urgency. It is not a diagnosis and does not suggest treatment.'
 
FONT = ('<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700'
        '&display=swap" rel="stylesheet">')
 
CSS = """
:root{--ink:#12303B;--mist:#EEF4F6;--teal:#1B7A86;--red:#C42B3F;--amber:#D4821F;--green:#2E8B6B;--muted:#64808A;--line:#E1ECEF}
body{font-family:'Instrument Sans',system-ui,sans-serif;color:var(--ink);background:var(--mist)}
.shell{width:100%;max-width:600px;margin:0 auto;padding:32px 16px 48px;gap:24px}
.brand{gap:8px}.brand-icon{font-size:26px;color:var(--teal)}
.brand-name{font-size:22px;font-weight:700;letter-spacing:-.02em}
.card{display:flex;flex-direction:column;width:100%;background:#fff;border:1px solid var(--line);border-radius:20px;padding:32px;gap:18px;
      box-shadow:0 1px 2px rgba(18,48,59,.05),0 16px 32px -16px rgba(18,48,59,.20)}
.swap{animation:swap .35s ease-out}
@keyframes swap{from{opacity:0;transform:translateX(24px)}to{opacity:1;transform:none}}
.meta{font-size:13px;color:var(--muted)}
.track{width:100%;height:6px;border-radius:4px;background:var(--line);overflow:hidden}
.fill{height:100%;border-radius:4px;background:var(--teal);transition:width .8s cubic-bezier(.2,.8,.2,1)}
.q-num{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);margin-top:6px}
.q-text{font-size:26px;line-height:1.25;font-weight:600;letter-spacing:-.01em;max-width:28ch}
.sub{font-size:15px;font-weight:400;line-height:1.45;color:inherit;opacity:.7;max-width:46ch;margin-top:2px}
.answers{gap:12px;width:100%;margin-top:6px;flex-wrap:nowrap}
.answer-btn{flex:1;min-height:52px;font-size:17px;font-weight:600;border-radius:12px}
.sec{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:6px}
.cond{width:100%;gap:6px;padding-top:14px;border-top:1px solid var(--line)}
.cond-row{width:100%;justify-content:space-between;align-items:baseline;flex-wrap:nowrap}
.cond-name{font-weight:600;font-size:17px;text-transform:capitalize}
.cond-pct{font-weight:700;font-variant-numeric:tabular-nums;color:var(--muted)}
.cond .sub{margin-top:0;font-size:14px}
.urg-title{font-size:28px;font-weight:700;line-height:1.15;letter-spacing:-.02em}
.urg-advice{font-size:16px;line-height:1.5;color:var(--muted)}.strong{font-weight:700}
.urg-emergency{background-image:linear-gradient(var(--red),var(--red));background-size:100% 5px;background-repeat:no-repeat}
.urg-urgent{background-image:linear-gradient(var(--amber),var(--amber));background-size:100% 5px;background-repeat:no-repeat}
.urg-routine{background-image:linear-gradient(var(--green),var(--green));background-size:100% 5px;background-repeat:no-repeat}
.urg-emergency .fill{background:var(--red)}.urg-urgent .fill{background:var(--amber)}
.urg-routine .fill{background:var(--green)}
.alarm{background:var(--red);border-color:var(--red);color:#fff;animation:swap .35s ease-out,pulse 1.8s ease-out 0.4s infinite}
.alarm .q-text,.alarm .urg-advice{color:#fff}.alarm .sub{color:#fff;opacity:.85}
.alarm-icon{font-size:44px}
.call-btn{min-height:56px;font-size:20px;font-weight:700;border-radius:12px;background:#fff!important;color:var(--red)!important}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(196,43,63,.5)}100%{box-shadow:0 0 0 22px rgba(196,43,63,0)}}
.fine{font-size:12px;color:var(--muted);line-height:1.4;text-align:center;max-width:46ch;align-self:center}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:480px){.q-text{font-size:23px}.card{padding:24px}}
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
                s['text'] = await asyncio.wait_for(run.io_bound(phrase, clean(node['symptom'])), 3)
            except Exception:           # LLM slow or down: triage must never block on it
                s['text'] = f"Are you experiencing {clean(node['symptom'])}?"
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
    def narrowing(node, bar=True):
        pct = round(100 * (1 - node['n'] / engine.total))
        ui.label(f"{node['n']:,} of {engine.total:,} records in the dataset still match").classes('meta')
        if bar:
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
                if text := blurb('symptoms', node['symptom']):
                    ui.label(text).classes('sub')
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
                    if text := blurb('diseases', name):
                        ui.label(text).classes('sub')
                    with ui.element('div').classes('track'):
                        fill = ui.element('div').classes('fill').style('width:0%')
                    grow(fill, round(conf * 100))
            narrowing(node, bar=False)
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
 
 
ui.run(title='Medic', favicon='🩺', reload=False)