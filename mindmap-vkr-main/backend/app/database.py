import json
import os
from typing import Dict, List, Optional
from app.models import TermCreate, TermUpdate, TermResponse


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
    
    def create_term(self, term_data: TermCreate) -> TermResponse:
        """Создает новый термина"""
        term_id = self.get_next_id()
        
        term_dict = {
            "id": term_id,
            "term": term_data.term,
            "definition": term_data.definition,
            "category": term_data.category,
            "related_terms": term_data.related_terms or []
        }
        
        self.data.append(term_dict)
        self.save_data()
        
        return TermResponse(**term_dict)
    
    def get_term(self, term_id: int) -> Optional[TermResponse]:
        """Получает термина по ID"""
        for term_data in self.data:
            if term_data.get('id') == term_id:
                return TermResponse(**term_data)
        return None
    
    def get_all_terms(self, page: int = 1, per_page: int = 10, 
                     search: Optional[str] = None) -> Dict:
        """Получает все термины с пагинацией и поиском"""
        terms = []
        
        for term_data in self.data:
            if search:
                search_lower = search.lower()
                if (search_lower not in term_data["term"].lower() and 
                    search_lower not in term_data["definition"].lower()):
                    continue
            
            terms.append(TermResponse(**term_data))
        
        # Сортировка по ID (новые термины сверху)
        terms.sort(key=lambda x: x.id, reverse=True)
        
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
    
    def update_term(self, term_id: int, term_data: TermUpdate) -> Optional[TermResponse]:
        """Обновляет термина"""
        for i, existing_term in enumerate(self.data):
            if existing_term.get('id') == term_id:
                # Обновляем только переданные поля
                update_data = term_data.dict(exclude_unset=True)
                for field, value in update_data.items():
                    existing_term[field] = value
                
                self.save_data()
                return TermResponse(**existing_term)
        return None
    
    def delete_term(self, term_id: int) -> bool:
        """Удаляет термина"""
        for i, term_data in enumerate(self.data):
            if term_data.get('id') == term_id:
                del self.data[i]
                self.save_data()
                return True
        return False
    
    def search_terms(self, query: str) -> List[TermResponse]:
        """Поиск терминов по запросу"""
        results = []
        query_lower = query.lower()
        
        for term_data in self.data:
            if (query_lower in term_data["term"].lower() or 
                query_lower in term_data["definition"].lower() or
                (term_data.get("category") and query_lower in term_data["category"].lower())):
                results.append(TermResponse(**term_data))
        
        return results


# Глобальный экземпляр базы данных
db = Database()
