<template>
  <div class="term-card">
    <div class="term-header">
      <h3 class="term-title">{{ term.term }}</h3>
      <span v-if="term.category" class="term-category">{{ term.category }}</span>
    </div>
    
    <p class="term-definition">{{ term.definition }}</p>
    
    <div v-if="term.related_terms && term.related_terms.length > 0" class="related-terms">
      <strong>Связанные термины:</strong>
      <span v-for="(related, index) in term.related_terms" :key="index" class="related-tag">
        {{ related }}
      </span>
    </div>
    
    
    <div class="term-actions">
      <button @click="$emit('edit', term)" class="btn btn-edit">Редактировать</button>
      <button @click="$emit('delete', term.id)" class="btn btn-delete">Удалить</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  term: {
    type: Object,
    required: true
  }
})

defineEmits(['edit', 'delete'])

</script>

<style scoped>
.term-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.term-card:hover {
  /* Убрали все hover эффекты */
}

.term-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.term-title {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3em;
  font-weight: bold;
}

.term-category {
  background: #3498db;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
}

.term-definition {
  color: #555;
  line-height: 1.6;
  margin-bottom: 15px;
}

.related-terms {
  margin-bottom: 15px;
}

.related-terms strong {
  color: #2c3e50;
  margin-right: 8px;
}

.related-tag {
  background: #ecf0f1;
  color: #2c3e50;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  margin-right: 6px;
  display: inline-block;
  margin-bottom: 4px;
}

.term-meta {
  color: #7f8c8d;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.term-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-edit {
  background: #f39c12;
  color: white;
}

.btn-edit:hover {
  background: #e67e22;
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background: #c0392b;
}
</style>
