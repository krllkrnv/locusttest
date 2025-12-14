"""
Locust тесты для gRPC API глоссария
Тестирует gRPC сервис на порту 50052
"""
import os
import random
import string
import time
import grpc
from locust import User, task, between, events


def random_string(length=8):
    """Генерирует случайную строку"""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


# Импорт сгенерированных protobuf файлов
from grpc_gen.glossary_pb2 import (
    HealthCheckRequest,
    GetTermsRequest,
    GetTermRequest,
    CreateTermRequest,
    SearchTermsRequest
)
from grpc_gen.glossary_pb2_grpc import GlossaryServiceStub


class GlossaryGrpcUser(User):
    """
    Класс пользователя для тестирования gRPC API глоссария
    Моделирует реалистичное поведение: чтение терминов, поиск, создание
    """
    wait_time = between(0.2, 1.2)  # Пауза между запросами 0.2-1.2 секунды
    
    def on_start(self):
        """Инициализация при старте пользователя"""
        # Получаем адрес gRPC сервера из переменной окружения или используем по умолчанию
        target = os.getenv("GRPC_TARGET", "127.0.0.1:50052")
        self.channel = grpc.insecure_channel(target)
        self.stub = GlossaryServiceStub(self.channel)
        self.term_ids = []
        self.created_ids = []
        self.search_queries = ["vue", "dom", "api", "react", "data", "json", "component", "state"]
        # Загружаем список ID терминов для использования в тестах
        self.refresh_term_ids()
    
    def on_stop(self):
        """Закрытие соединения при остановке пользователя"""
        try:
            self.channel.close()
        except Exception:
            pass
    
    def _fire_request(self, name, start_time, response=None, exception=None):
        """
        Записывает метрику запроса в Locust
        """
        request_type = "gRPC"
        response_time = (time.perf_counter() - start_time) * 1000  # в миллисекундах
        response_length = 0
        
        if response is not None:
            try:
                response_length = len(response.SerializeToString())
            except Exception:
                pass
        
        events.request.fire(
            request_type=request_type,
            name=name,
            response_time=response_time,
            response_length=response_length,
            exception=exception,
        )
    
    def refresh_term_ids(self):
        """Обновляет список доступных ID терминов"""
        start_time = time.perf_counter()
        try:
            request = GetTermsRequest(page=1, per_page=100, search="")
            response = self.stub.GetTerms(request, timeout=3.0)
            self.term_ids = [term.id for term in response.terms]
            self._fire_request("GetTerms [refresh_ids]", start_time, response=response)
        except grpc.RpcError as e:
            self._fire_request("GetTerms [refresh_ids]", start_time, exception=e)
        except Exception as e:
            self._fire_request("GetTerms [refresh_ids]", start_time, exception=e)
    
    @task(10)
    def health_check(self):
        """
        Легкий тест: проверка здоровья сервиса
        Вес: 10 (50% нагрузки)
        """
        start_time = time.perf_counter()
        try:
            request = HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=3.0)
            self._fire_request("HealthCheck", start_time, response=response)
        except grpc.RpcError as e:
            self._fire_request("HealthCheck", start_time, exception=e)
        except Exception as e:
            self._fire_request("HealthCheck", start_time, exception=e)
    
    @task(4)
    def get_terms(self):
        """
        Получение списка терминов с пагинацией
        Вес: 4 (20% нагрузки)
        """
        start_time = time.perf_counter()
        try:
            page = random.randint(1, 3)
            per_page = random.choice([10, 20, 50])
            request = GetTermsRequest(page=page, per_page=per_page, search="")
            response = self.stub.GetTerms(request, timeout=3.0)
            self._fire_request("GetTerms", start_time, response=response)
        except grpc.RpcError as e:
            self._fire_request("GetTerms", start_time, exception=e)
        except Exception as e:
            self._fire_request("GetTerms", start_time, exception=e)
    
    @task(3)
    def get_term(self):
        """
        Получение конкретного термина по ID
        Вес: 3 (15% нагрузки)
        """
        if not self.term_ids:
            self.refresh_term_ids()
            return
        
        start_time = time.perf_counter()
        try:
            term_id = random.choice(self.term_ids)
            request = GetTermRequest(term_id=term_id)
            response = self.stub.GetTerm(request, timeout=3.0)
            self._fire_request("GetTerm", start_time, response=response)
        except grpc.RpcError as e:
            self._fire_request("GetTerm", start_time, exception=e)
        except Exception as e:
            self._fire_request("GetTerm", start_time, exception=e)
    
    @task(2)
    def search_terms(self):
        """
        Поиск терминов по запросу
        Вес: 2 (10% нагрузки)
        """
        start_time = time.perf_counter()
        try:
            query = random.choice(self.search_queries)
            request = SearchTermsRequest(query=query)
            response = self.stub.SearchTerms(request, timeout=3.0)
            self._fire_request("SearchTerms", start_time, response=response)
        except grpc.RpcError as e:
            self._fire_request("SearchTerms", start_time, exception=e)
        except Exception as e:
            self._fire_request("SearchTerms", start_time, exception=e)
    
    @task(1)
    def create_term(self):
        """
        Тяжелый тест: создание нового термина (запись в JSON файл)
        Вес: 1 (5% нагрузки)
        """
        start_time = time.perf_counter()
        try:
            request = CreateTermRequest(
                term=f"loadtest-{random_string()}",
                definition=f"Test definition for load testing: {random_string(16)}",
                category="loadtest",
                related_terms=["test1", "test2", "test3"]
            )
            response = self.stub.CreateTerm(request, timeout=3.0)
            if response.id:
                self.created_ids.append(response.id)
                # Обновляем список ID для использования в других тестах
                if response.id not in self.term_ids:
                    self.term_ids.append(response.id)
            self._fire_request("CreateTerm", start_time, response=response)
        except grpc.RpcError as e:
            self._fire_request("CreateTerm", start_time, exception=e)
        except Exception as e:
            self._fire_request("CreateTerm", start_time, exception=e)

