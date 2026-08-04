"""绝对最小化应用 - 验证 Render 基本运行"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="景区投资")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Hello!"}
