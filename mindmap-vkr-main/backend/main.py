from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import TermCreate, TermUpdate, TermResponse, TermListResponse
from app.database import db

# Создаем приложение FastAPI
app = FastAPI(
    title="Глоссарий терминов ВКР",
    description="API для управления глоссарием терминов выпускной квалификационной работы",
    version="1.0.0"
)

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Локальная разработка
        "https://mindmap-vkr.vercel.app",  # Продакшен фронтенд
        "https://mindmap-vkr-git-main.vercel.app",  # Vercel preview
        "https://mindmap-vkr-git-*.vercel.app"  # Vercel branch deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "Глоссарий терминов ВКР API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/terms", response_model=TermListResponse)
async def get_terms(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество терминов на странице"),
    search: Optional[str] = Query(None, description="Поисковый запрос")
):
    """Получить список всех терминов с пагинацией и поиском"""
    result = db.get_all_terms(page=page, per_page=per_page, search=search)
    return TermListResponse(**result)


@app.get("/api/terms/{term_id}", response_model=TermResponse)
async def get_term(term_id: int):
    """Получить информацию о конкретном термине"""
    term = db.get_term(term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term


@app.post("/api/terms", response_model=TermResponse)
async def create_term(term_data: TermCreate):
    """Добавить новый термина в глоссарий"""
    return db.create_term(term_data)


@app.put("/api/terms/{term_id}", response_model=TermResponse)
async def update_term(term_id: int, term_data: TermUpdate):
    """Обновить существующий термина"""
    term = db.update_term(term_id, term_data)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term


@app.delete("/api/terms/{term_id}")
async def delete_term(term_id: int):
    """Удалить термина из глоссария"""
    success = db.delete_term(term_id)
    if not success:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return {"message": "Термин успешно удален"}


@app.get("/api/terms/search/{query}")
async def search_terms(query: str):
    """Поиск терминов по запросу"""
    results = db.search_terms(query)
    return {"results": results, "query": query, "count": len(results)}


@app.get("/api/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy", "message": "API работает корректно"}


# Это важно для Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
