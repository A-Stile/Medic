# Medic

Medic is a symptom-triage app. It asks a series of yes/no questions, Akinator-style, to narrow down likely conditions and how urgent they are. It identifies conditions and urgency only, not treatments.

**Medic is not a medical device and does not provide a diagnosis. It is not a substitute for a doctor. If you think you are having an emergency, call 911 (or your local emergency number).**

## How it works

1. **Tree builder (offline).** Reads a Kaggle dataset of ~247,000 patient cases (773 diseases, 377 symptoms) and builds a decision tree using entropy and information gain. At each step it picks the symptom question that best splits the remaining cases. The output is a JSON file.
2. **Runtime engine.** Walks the JSON tree one question at a time based on the user's answers, and ends at a result: the top likely conditions with confidence percentages.
3. **Red-flag overrides.** Certain dangerous symptoms trigger an emergency warning at a lower confidence threshold than normal results.
4. **Interface.** Built with NiceGUI.
5. **Phrasing layer (optional).** [An LLM / template system] rewords questions conversationally. It never makes triage decisions. All medical reasoning lives in the deterministic tree.

## Project files

| `medic_ui.py` | Starts the web app |
| `json_reader.py` | Walks the decision tree |
| `starter_tree.json` | The decision tree used by the app |
| `decision_Tree.py` | Builds the tree from the dataset (not needed to run the app) |
| `requirements.txt` | Python packages the app needs |

## Run it locally

1. Install Python 3.[10 or newer].
2. Open a terminal in the project folder.
3. (Recommended) Create a virtual environment:
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
4. Install the packages: `pip install -r requirements.txt`
5. Start the app: `python [main.py]`
6. Open http://localhost:8080 in your browser.

## Rebuild the tree (optional)

Only needed if you change the tree-building logic.

1. Download `Final_Augmented_dataset_Diseases_and_Symptoms.csv` from Kaggle and place it in [folder].
2. Run `python decision_Tree.py`.
3. It writes a new JSON tree to `starter_tree.json`.

## Deployment

Hosted on [Render/Railway] at [URL]. The start command is `python [main.py]`, and the port comes from the `PORT` environment variable.

## Limitations

- Results are statistical guesses from a dataset, not a clinical assessment.
- The dataset is synthetic, so it may not reflect real-world case frequencies.
- Not tested or validated by medical professionals.

## Built by

Remi Sabbe, for the Congressional App Challenge 2026.