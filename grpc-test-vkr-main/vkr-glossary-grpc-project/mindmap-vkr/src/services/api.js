// API сервис для работы с глоссарием
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://mindmap-vkr-backend.vercel.app/api'
  : 'http://localhost:8000/api'

class GlossaryAPI {
  // Получить все термины с пагинацией и поиском
  async getTerms(page = 1, perPage = 10, search = '') {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    })
    
    if (search) {
      params.append('search', search)
    }
    
    const response = await fetch(`${API_BASE}/terms?${params}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  }

  // Получить термина по ID
  async getTerm(id) {
    const response = await fetch(`${API_BASE}/terms/${id}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  }

  // Создать новый термина
  async createTerm(termData) {
    const response = await fetch(`${API_BASE}/terms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(termData)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка создания термина')
    }
    
    return await response.json()
  }

  // Обновить термина
  async updateTerm(id, termData) {
    const response = await fetch(`${API_BASE}/terms/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(termData)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка обновления термина')
    }
    
    return await response.json()
  }

  // Удалить термина
  async deleteTerm(id) {
    const response = await fetch(`${API_BASE}/terms/${id}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка удаления термина')
    }
    
    return await response.json()
  }

  // Поиск терминов
  async searchTerms(query) {
    const response = await fetch(`${API_BASE}/terms/search/${encodeURIComponent(query)}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  }

  // Проверка состояния API
  async healthCheck() {
    const response = await fetch(`${API_BASE}/health`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  }
}

export default new GlossaryAPI()
