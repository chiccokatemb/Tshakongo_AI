
from pathlib import Path
from jinja2 import Template

TEMPLATES = {
"flask_app_py": Template('''
from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello from {{ app_name }}!"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port={{ port }}, debug=True)
'''),
"fastapi_app_py": Template('''
from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get("/")
def read_root():
    return {"msg": "Hello from {{ app_name }}!"}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={{ port }})
'''),
"cli_py": Template('''
import argparse
def main():
    p = argparse.ArgumentParser(description="{{ app_name }} CLI")
    p.add_argument("--name", default="World")
    args = p.parse_args()
    print(f"Hello, {args.name}! from {{ app_name }}")
if __name__ == "__main__":
    main()
'''),
"requirements_flask": Template("flask\n"),
"requirements_fastapi": Template("fastapi\nuvicorn\n")
}
def scaffold(kind:str, target_dir:str, app_name:str="MyApp", port:int=5000):
    root = Path(target_dir).resolve(); root.mkdir(parents=True, exist_ok=True)
    if kind=="flask":
        (root/"app.py").write_text(TEMPLATES["flask_app_py"].render(app_name=app_name, port=port), encoding="utf-8")
        (root/"requirements.txt").write_text(TEMPLATES["requirements_flask"].render(), encoding="utf-8")
        return f"Projet Flask créé dans {root}"
    if kind=="fastapi":
        (root/"app.py").write_text(TEMPLATES["fastapi_app_py"].render(app_name=app_name, port=port), encoding="utf-8")
        (root/"requirements.txt").write_text(TEMPLATES["requirements_fastapi"].render(), encoding="utf-8")
        return f"Projet FastAPI créé dans {root}"
    if kind=="cli":
        (root/"main.py").write_text(TEMPLATES["cli_py"].render(app_name=app_name), encoding="utf-8")
        return f"Projet CLI créé dans {root}"
    return "Type inconnu. Utilise: flask | fastapi | cli"
