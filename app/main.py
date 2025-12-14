from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = BASE_DIR / "questions"

app.mount("/static", StaticFiles(directory=BASE_DIR / "app/static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "app/templates")

@app.head("/")
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/go")
def go(question_id: str = Form(...)):
    return RedirectResponse(f"/question/{question_id}", status_code=303)

@app.get("/question/{qid}", response_class=HTMLResponse)
def question(request: Request, qid: str):
    file_path = QUESTIONS_DIR / f"{qid}.txt"
    if not file_path.exists():
        return HTMLResponse("題目不存在", status_code=404)

    lines = file_path.read_text(encoding="utf-8").splitlines()

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "qid": qid,
            "lines": lines,
            "display": {},
        },
    )

@app.post("/question/{qid}", response_class=HTMLResponse)
async def question_action(request: Request, qid: str, command: str = Form(...)):
    file_path = QUESTIONS_DIR / f"{qid}.txt"
    lines = file_path.read_text(encoding="utf-8").splitlines()

    form = await request.form()
    existing_display = form.get("existing_display", "{}")
    import ast
    display = ast.literal_eval(existing_display)  # 將字串轉回 dict

    if command == "all":
        display = {i + 1: line for i, line in enumerate(lines)}
    elif command == "back":
        return RedirectResponse("/", status_code=303)
    else:
        try:
            i = int(command)
            if 1 <= i <= len(lines):
                display[i] = lines[i - 1]  # 新增到 display，不會覆蓋舊的
        except ValueError:
            pass

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "qid": qid,
            "lines": lines,
            "display": display,
        },
    )
