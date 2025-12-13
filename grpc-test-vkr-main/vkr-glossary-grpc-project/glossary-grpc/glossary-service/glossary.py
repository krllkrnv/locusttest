# glossary-service/glossary.py
from concurrent import futures
import json
import os
import logging

import grpc

from glossary_pb2 import (
    Term,
    GetTermsResponse,
    DeleteTermResponse,
    SearchTermsResponse,
    HealthCheckResponse,
)
import glossary_pb2_grpc


class Database:
    """Простая база данных на основе JSON файла"""
    
    def __init__(self, file_path: str = "data/terms.json"):
        self.file_path = file_path
        self.ensure_data_directory()
        self.load_data()
        
    def ensure_data_directory(self):
        """Создает директорию data если её нет"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def load_data(self):
        """Загружает данные из JSON файла"""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = []
            self.save_data()
    
    def save_data(self):
        """Сохраняет данные в JSON файл"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_next_id(self) -> int:
        """Возвращает следующий доступный ID"""
        if not self.data:
            return 1
        return max(term.get('id', 0) for term in self.data) + 1
    
    def create_term(self, term: str, definition: str, category: str = "", related_terms: list = None):
        """Создает новый термина"""
        term_id = self.get_next_id()
        
        term_dict = {
            "id": term_id,
            "term": term,
            "definition": definition,
            "category": category or None,
            "related_terms": related_terms or []
        }
        
        self.data.append(term_dict)
        self.save_data()
        
        return term_dict
    
    def get_term(self, term_id: int):
        """Получает термина по ID"""
        for term_data in self.data:
            if term_data.get('id') == term_id:
                return term_data
        return None
    
    def get_all_terms(self, page: int = 1, per_page: int = 10, search: str = ""):
        """Получает все термины с пагинацией и поиском"""
        terms = []
        
        for term_data in self.data:
            if search:
                search_lower = search.lower()
                if (search_lower not in term_data["term"].lower() and 
                    search_lower not in term_data["definition"].lower()):
                    continue
            
            terms.append(term_data)
        
        # Сортировка по ID (новые термины сверху)
        terms.sort(key=lambda x: x.get('id', 0), reverse=True)
        
        # Пагинация
        total = len(terms)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_terms = terms[start:end]
        
        return {
            "terms": paginated_terms,
            "total": total,
            "page": page,
            "per_page": per_page
        }
    
    def update_term(self, term_id: int, term: str = None, definition: str = None, 
                   category: str = None, related_terms: list = None):
        """Обновляет термина"""
        for existing_term in self.data:
            if existing_term.get('id') == term_id:
                if term is not None:
                    existing_term["term"] = term
                if definition is not None:
                    existing_term["definition"] = definition
                if category is not None:
                    existing_term["category"] = category if category else None
                if related_terms is not None:
                    existing_term["related_terms"] = related_terms
                
                self.save_data()
                return existing_term
        return None
    
    def delete_term(self, term_id: int) -> bool:
        """Удаляет термина"""
        for i, term_data in enumerate(self.data):
            if term_data.get('id') == term_id:
                del self.data[i]
                self.save_data()
                return True
        return False
    
    def search_terms(self, query: str):
        """Поиск терминов по запросу"""
        results = []
        query_lower = query.lower()
        
        for term_data in self.data:
            if (query_lower in term_data["term"].lower() or 
                query_lower in term_data["definition"].lower() or
                (term_data.get("category") and query_lower in term_data.get("category", "").lower())):
                results.append(term_data)
        
        return results


class GlossaryService(glossary_pb2_grpc.GlossaryServiceServicer):
    def __init__(self):
        self.db = Database()
    
    def GetTerm(self, request, context):
        """Получить информацию о конкретном термине"""
        term_data = self.db.get_term(request.term_id)
        if not term_data:
            context.abort(grpc.StatusCode.NOT_FOUND, "Термин не найден")
        
        return Term(
            id=term_data["id"],
            term=term_data["term"],
            definition=term_data["definition"],
            category=term_data.get("category") or "",
            related_terms=term_data.get("related_terms", [])
        )
    
    def GetTerms(self, request, context):
        """Получить список всех терминов с пагинацией и поиском"""
        page = request.page if request.page > 0 else 1
        per_page = request.per_page if request.per_page > 0 else 10
        search = request.search if request.search else ""
        
        result = self.db.get_all_terms(page=page, per_page=per_page, search=search)
        
        terms = []
        for term_data in result["terms"]:
            terms.append(Term(
                id=term_data["id"],
                term=term_data["term"],
                definition=term_data["definition"],
                category=term_data.get("category") or "",
                related_terms=term_data.get("related_terms", [])
            ))
        
        return GetTermsResponse(
            terms=terms,
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"]
        )
    
    def CreateTerm(self, request, context):
        """Добавить новый термина в глоссарий"""
        term_data = self.db.create_term(
            term=request.term,
            definition=request.definition,
            category=request.category if request.category else "",
            related_terms=list(request.related_terms)
        )
        
        return Term(
            id=term_data["id"],
            term=term_data["term"],
            definition=term_data["definition"],
            category=term_data.get("category") or "",
            related_terms=term_data.get("related_terms", [])
        )
    
    def UpdateTerm(self, request, context):
        """Обновить существующий термина"""
        term_data = self.db.update_term(
            term_id=request.term_id,
            term=request.term if request.term else None,
            definition=request.definition if request.definition else None,
            category=request.category if request.category else None,
            related_terms=list(request.related_terms) if request.related_terms else None
        )
        
        if not term_data:
            context.abort(grpc.StatusCode.NOT_FOUND, "Термин не найден")
        
        return Term(
            id=term_data["id"],
            term=term_data["term"],
            definition=term_data["definition"],
            category=term_data.get("category") or "",
            related_terms=term_data.get("related_terms", [])
        )
    
    def DeleteTerm(self, request, context):
        """Удалить термина из глоссария"""
        success = self.db.delete_term(request.term_id)
        if not success:
            context.abort(grpc.StatusCode.NOT_FOUND, "Термин не найден")
        
        return DeleteTermResponse(message="Термин успешно удален")
    
    def SearchTerms(self, request, context):
        """Поиск терминов по запросу"""
        results = self.db.search_terms(request.query)
        
        term_list = []
        for term_data in results:
            term_list.append(Term(
                id=term_data["id"],
                term=term_data["term"],
                definition=term_data["definition"],
                category=term_data.get("category") or "",
                related_terms=term_data.get("related_terms", [])
            ))
        
        return SearchTermsResponse(
            results=term_list,
            query=request.query,
            count=len(term_list)
        )
    
    def HealthCheck(self, request, context):
        """Проверка состояния API"""
        return HealthCheckResponse(
            status="healthy",
            message="API работает корректно"
        )


def serve():
    port = "50052"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(
        GlossaryService(), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Glossary gRPC Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()

