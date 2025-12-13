<template>
  <div class="app">
    <header class="app-header">
      <h1>Глоссарий терминов ВКР</h1>
    </header>

    <nav class="main-nav">
      <router-link to="/terms" class="nav-link">
        Список терминов
      </router-link>
      <router-link to="/terms/create" class="nav-link">
        Добавить термин
      </router-link>
      <router-link to="/graph" class="nav-link">
        Граф связей
      </router-link>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// Простой App.vue с роутером
</script>

<style scoped>
.app {
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.app-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #ecf0f1;
}

.app-header h1 {
  color: #2c3e50;
  font-size: 2.5em;
  margin-bottom: 10px;
}

.app-header p {
  color: #7f8c8d;
  font-size: 1.1em;
}

.main-nav {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #ecf0f1;
}

.nav-link {
  padding: 12px 24px;
  text-decoration: none;
  color: #7f8c8d;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.nav-link:hover {
  color: #3498db;
  background: #f8f9fa;
  border-color: #3498db;
}

.nav-link.router-link-active {
  color: #3498db;
  background: #e3f2fd;
  border-color: #3498db;
}

.main-content {
  min-height: 60vh;
}

@media (max-width: 768px) {
  .app {
    padding: 15px;
  }
  
  .main-nav {
    flex-direction: column;
    gap: 10px;
  }
  
  .nav-link {
    text-align: center;
  }
}
</style>