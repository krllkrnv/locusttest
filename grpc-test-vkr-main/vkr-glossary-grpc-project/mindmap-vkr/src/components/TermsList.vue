<template>
  <div class="terms-list">
    <div class="header">
      <h1>Словарь терминов</h1>
      <div class="actions">
        <button @click="$router.push('/terms/create')" class="btn btn-primary">
          Добавить термин
        </button>
        <button @click="$router.push('/graph')" class="btn btn-secondary">
          Граф связей
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      Загрузка терминов...
    </div>

    <div v-else-if="error" class="error">
      Ошибка: {{ error }}
    </div>

    <div v-else class="terms-grid">
      <TermCard 
        v-for="term in terms" 
        :key="term.id" 
        :term="term"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'
import TermCard from './TermCard.vue'

export default {
  name: 'TermsList',
  components: {
    TermCard
  },
  setup() {
    const router = useRouter()
    const terms = ref([])
    const loading = ref(true)
    const error = ref(null)

    const loadTerms = async () => {
      try {
        loading.value = true
        error.value = null
        const data = await api.getTerms(1, 100) // Запрашиваем все термины
        terms.value = data.terms // Берем массив терминов из ответа
      } catch (err) {
        error.value = err.message
        console.error('Ошибка загрузки терминов:', err)
      } finally {
        loading.value = false
      }
    }

    const handleEdit = (term) => {
      router.push(`/terms/${term.id}/edit`)
    }

    const handleDelete = async (termId) => {
      if (confirm('Вы уверены, что хотите удалить этот термин?')) {
        try {
          await api.deleteTerm(termId)
          // Удаляем термин из локального списка
          terms.value = terms.value.filter(term => term.id !== termId)
          alert('Термин успешно удален')
        } catch (err) {
          error.value = err.message
          console.error('Ошибка удаления термина:', err)
          alert('Ошибка при удалении термина: ' + err.message)
        }
      }
    }

    onMounted(() => {
      loadTerms()
    })

    return {
      terms,
      loading,
      error,
      handleEdit,
      handleDelete
    }
  }
}
</script>

<style scoped>
.terms-list {
  max-width: 1200px;
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

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #e74c3c;
}

.terms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

/* Стили для TermCard теперь в самом компоненте TermCard.vue */
</style>
