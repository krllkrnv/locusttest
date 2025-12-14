"""
Locust тесты для REST API глоссария
Тестирует FastAPI сервис на порту 8000
"""
import random
import string
from locust import HttpUser, task, between


def random_string(length=8):
    """Генерирует случайную строку"""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


class GlossaryRestUser(HttpUser):
    """
    Класс пользователя для тестирования REST API глоссария
    Моделирует реалистичное поведение: чтение терминов, поиск, создание
    """
    wait_time = between(0.2, 1.2)  # Пауза между запросами 0.2-1.2 секунды
    
    def on_start(self):
        """Инициализация при старте пользователя"""
        self.term_ids = []
        self.created_ids = []
        self.search_queries = ["vue", "dom", "api", "react", "data", "json", "component", "state"]
        # Загружаем список ID терминов для использования в тестах
        self.refresh_term_ids()
    
    def refresh_term_ids(self):
        """Обновляет список доступных ID терминов"""
        try:
            response = self.client.get(
                "/api/terms",
                params={"page": 1, "per_page": 100},
                name="GET /api/terms [refresh_ids]"
            )
            if response.status_code == 200:
                data = response.json()
                self.term_ids = [term["id"] for term in data.get("terms", []) if "id" in term]
        except Exception as e:
            print(f"Ошибка при обновлении списка терминов: {e}")
    
    @task(10)
    def health_check(self):
        """
        Легкий тест: проверка здоровья сервиса
        Вес: 10 (50% нагрузки)
        """
        self.client.get("/api/health", name="GET /api/health")
    
    @task(4)
    def list_terms(self):
        """
        Получение списка терминов с пагинацией
        Вес: 4 (20% нагрузки)
        """
        page = random.randint(1, 3)
        per_page = random.choice([10, 20, 50])
        self.client.get(
            "/api/terms",
            params={"page": page, "per_page": per_page},
            name="GET /api/terms"
        )
    
    @task(3)
    def get_term(self):
        """
        Получение конкретного термина по ID
        Вес: 3 (15% нагрузки)
        """
        if not self.term_ids:
            self.refresh_term_ids()
            return
        
        term_id = random.choice(self.term_ids)
        self.client.get(f"/api/terms/{term_id}", name="GET /api/terms/{id}")
    
    @task(2)
    def search_terms(self):
        """
        Поиск терминов по запросу
        Вес: 2 (10% нагрузки)
        """
        query = random.choice(self.search_queries)
        self.client.get(f"/api/terms/search/{query}", name="GET /api/terms/search/{query}")
    
    @task(1)
    def create_term(self):
        """
        Тяжелый тест: создание нового термина (запись в JSON файл)
        Вес: 1 (5% нагрузки)
        """
        payload = {
            "term": f"loadtest-{random_string()}",
            "definition": f"Test definition for load testing: {random_string(16)}",
            "category": "loadtest",
            "related_terms": ["test1", "test2", "test3"]
        }
        response = self.client.post(
            "/api/terms",
            json=payload,
            name="POST /api/terms"
        )
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                self.created_ids.append(data["id"])
                # Обновляем список ID для использования в других тестах
                if data["id"] not in self.term_ids:
                    self.term_ids.append(data["id"])

