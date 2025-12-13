# web-service/web.py
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import grpc

from glossary_pb2 import (
    GetTermRequest,
    GetTermsRequest,
    CreateTermRequest,
    UpdateTermRequest,
    DeleteTermRequest,
    SearchTermsRequest,
    HealthCheckRequest,
)
from glossary_pb2_grpc import GlossaryServiceStub

# Создаем приложение FastAPI
app = FastAPI(
    title="Глоссарий терминов ВКР",
    description="API для управления глоссарием терминов выпускной квалификационной работы (gRPC прокси)",
    version="1.0.0"
)

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к gRPC серверу
glossary_host = os.getenv("GLOSSARY_HOST", "localhost")
glossary_channel = grpc.insecure_channel(f"{glossary_host}:50052")
glossary_client = GlossaryServiceStub(glossary_channel)


def term_to_dict(term):
    """Преобразует protobuf Term в словарь"""
    return {
        "id": term.id,
        "term": term.term,
        "definition": term.definition,
        "category": term.category if term.category else None,
        "related_terms": list(term.related_terms)
    }


@app.get("/")
async def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "Глоссарий терминов ВКР API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/terms")
async def get_terms(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество терминов на странице"),
    search: Optional[str] = Query(None, description="Поисковый запрос")
):
    """Получить список всех терминов с пагинацией и поиском"""
    try:
        request = GetTermsRequest(
            page=page,
            per_page=per_page,
            search=search if search else ""
        )
        response = glossary_client.GetTerms(request)
        
        terms = [term_to_dict(term) for term in response.terms]
        
        return {
            "terms": terms,
            "total": response.total,
            "page": response.page,
            "per_page": response.per_page
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/terms/{term_id}")
async def get_term(term_id: int):
    """Получить информацию о конкретном термине"""
    try:
        request = GetTermRequest(term_id=term_id)
        response = glossary_client.GetTerm(request)
        return term_to_dict(response)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Термин не найден")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/terms")
async def create_term(term_data: dict):
    """Добавить новый термина в глоссарий"""
    try:
        request = CreateTermRequest(
            term=term_data.get("term", ""),
            definition=term_data.get("definition", ""),
            category=term_data.get("category", ""),
            related_terms=term_data.get("related_terms", [])
        )
        response = glossary_client.CreateTerm(request)
        return term_to_dict(response)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/terms/{term_id}")
async def update_term(term_id: int, term_data: dict):
    """Обновить существующий термина"""
    try:
        request = UpdateTermRequest(
            term_id=term_id,
            term=term_data.get("term", ""),
            definition=term_data.get("definition", ""),
            category=term_data.get("category", ""),
            related_terms=term_data.get("related_terms", [])
        )
        response = glossary_client.UpdateTerm(request)
        return term_to_dict(response)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Термин не найден")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/terms/{term_id}")
async def delete_term(term_id: int):
    """Удалить термина из глоссария"""
    try:
        request = DeleteTermRequest(term_id=term_id)
        response = glossary_client.DeleteTerm(request)
        return {"message": response.message}
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Термин не найден")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/terms/search/{query}")
async def search_terms(query: str):
    """Поиск терминов по запросу"""
    try:
        request = SearchTermsRequest(query=query)
        response = glossary_client.SearchTerms(request)
        
        results = [term_to_dict(term) for term in response.results]
        
        return {
            "results": results,
            "query": response.query,
            "count": response.count
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Проверка состояния API"""
    try:
        request = HealthCheckRequest()
        response = glossary_client.HealthCheck(request)
        return {
            "status": response.status,
            "message": response.message
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

