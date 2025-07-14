from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from routes.chat import router as chat_router

# 環境変数の読み込み
load_dotenv()

# FastAPIアプリケーションの初期化
app = FastAPI(title="Azure AI Chat Tool")

# ミドルウェアの設定
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your-secret-key-here")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルの設定
import os
from pathlib import Path

# プロジェクトのルートディレクトリを取得
BASE_DIR = Path(__file__).resolve().parent.parent

# 静的ファイルの設定
static_dir = BASE_DIR / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# テンプレートの設定
template_dir = BASE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=str(template_dir))

# ルーターの登録
app.include_router(chat_router)

# ルートエンドポイント
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Azure AI Chat Tool"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )