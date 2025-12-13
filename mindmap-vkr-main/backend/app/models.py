from pydantic import BaseModel
from typing import Optional, List


class TermBase(BaseModel):
    """Базовая модель термина"""
    term: str
    definition: str
    category: Optional[str] = None
    related_terms: Optional[List[str]] = []


class TermCreate(TermBase):
    """Модель для создания нового термина"""
    pass


class TermUpdate(BaseModel):
    """Модель для обновления термина"""
    term: Optional[str] = None
    definition: Optional[str] = None
    category: Optional[str] = None
    related_terms: Optional[List[str]] = None


class TermResponse(TermBase):
    """Модель ответа с термином"""
    id: int

    class Config:
        from_attributes = True


class TermListResponse(BaseModel):
    """Модель для списка терминов"""
    terms: List[TermResponse]
    total: int
    page: int
    per_page: int
