<template>
  <div class="term-form">
    <div class="header">
      <h1>{{ isEdit ? 'Редактировать термин' : 'Создать новый термин' }}</h1>
      <button @click="$router.push('/terms')" class="btn btn-secondary">
        Назад к списку
      </button>
    </div>

    <form @submit.prevent="saveTerm" class="form">
      <div class="form-group">
        <label for="term">Термин *</label>
        <input 
          id="term"
          v-model="form.term" 
          type="text" 
          required 
          class="form-control"
          placeholder="Введите термин"
        />
      </div>

      <div class="form-group">
        <label for="definition">Определение *</label>
        <textarea 
          id="definition"
          v-model="form.definition" 
          required 
          class="form-control"
          rows="4"
          placeholder="Введите определение термина"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="category">Категория *</label>
        <select id="category" v-model="form.category" required class="form-control">
          <option value="">Выберите категорию</option>
          <option value="Фреймворки">Фреймворки</option>
          <option value="Рендеринг">Рендеринг</option>
          <option value="Концепции">Концепции</option>
          <option value="API">API</option>
          <option value="Оптимизация">Оптимизация</option>
          <option value="Библиотеки">Библиотеки</option>
          <option value="Инструменты">Инструменты</option>
          <option value="Метрики">Метрики</option>
          <option value="Инфраструктура">Инфраструктура</option>
          <option value="Синтаксис">Синтаксис</option>
          <option value="Основы">Основы</option>
          <option value="Технологии визуализации">Технологии визуализации</option>
          <option value="Общее">Общее</option>
          <option value="Верстка">Верстка</option>
        </select>
      </div>

      <div class="form-group">
        <label for="related_terms">Связанные термины</label>
        <div class="related-terms">
          <div v-for="(related, index) in form.related_terms" :key="index" class="related-term">
            <input 
              v-model="form.related_terms[index]" 
              type="text" 
              class="form-control"
              placeholder="Связанный термин"
            />
            <button 
              type="button" 
              @click="removeRelatedTerm(index)" 
              class="btn btn-danger btn-sm"
            >
              ×
            </button>
          </div>
          <button 
            type="button" 
            @click="addRelatedTerm" 
            class="btn btn-outline btn-sm"
          >
            Добавить связь
          </button>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" :disabled="loading" class="btn btn-primary">
          {{ loading ? 'Сохранение...' : (isEdit ? 'Обновить' : 'Создать') }}
        </button>
        <button type="button" @click="$router.push('/terms')" class="btn btn-secondary">
          Отмена
        </button>
      </div>
    </form>

    <div v-if="error" class="error">
      Ошибка: {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api.js'

export default {
  name: 'TermForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const form = ref({
      term: '',
      definition: '',
      category: '',
      related_terms: []
    })
    
    const loading = ref(false)
    const error = ref(null)
    const isEdit = computed(() => !!route.params.id)

    const loadTerm = async (id) => {
      try {
        loading.value = true
        error.value = null
        const data = await api.getTerms(1, 100) // Запрашиваем все термины
        const term = data.terms.find(t => t.id === parseInt(id)) // Ищем в массиве terms
        if (term) {
          form.value = {
            term: term.term,
            definition: term.definition,
            category: term.category,
            related_terms: [...(term.related_terms || [])]
          }
        } else {
          error.value = 'Термин не найден'
        }
      } catch (err) {
        error.value = err.message
        console.error('Ошибка загрузки термина:', err)
      } finally {
        loading.value = false
      }
    }

    const saveTerm = async () => {
      try {
        loading.value = true
        error.value = null
        
        const termData = {
          ...form.value,
          related_terms: form.value.related_terms.filter(term => term.trim())
        }

        if (isEdit.value) {
          await api.updateTerm(route.params.id, termData)
        } else {
          await api.createTerm(termData)
        }

        router.push('/terms')
      } catch (err) {
        error.value = err.message
        console.error('Ошибка сохранения термина:', err)
      } finally {
        loading.value = false
      }
    }

    const addRelatedTerm = () => {
      form.value.related_terms.push('')
    }

    const removeRelatedTerm = (index) => {
      form.value.related_terms.splice(index, 1)
    }

    onMounted(() => {
      if (isEdit.value) {
        loadTerm(route.params.id)
      }
    })

    return {
      form,
      loading,
      error,
      isEdit,
      saveTerm,
      addRelatedTerm,
      removeRelatedTerm
    }
  }
}
</script>

<style scoped>
.term-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.header h1 {
  margin: 0;
  color: #2c3e50;
}

.form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.related-terms {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.related-term {
  display: flex;
  gap: 10px;
  align-items: center;
}

.related-term .form-control {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  width: 30px;
  height: 30px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-outline {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline:hover {
  background-color: #3498db;
  color: white;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}
</style>