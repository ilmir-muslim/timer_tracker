<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <!-- Заголовок (таймер убран, остался только заголовок) -->
        <div class="title-section">
          <h1>⏱️ Учёт времени</h1>
          <p>Эффективно отслеживайте время ваших проектов</p>
        </div>

        <!-- Навигация -->
        <nav v-if="$store.getters.isAuthenticated" class="nav">
          <router-link to="/daily-tasks" class="nav-link">📅 Ежедневные задачи</router-link>
          <router-link to="/" class="nav-link">📁 Проекты</router-link>
          <button @click="handleLogout" class="btn btn-logout">Выйти</button>
        </nav>
        <nav v-else class="nav">
          <router-link to="/login" class="nav-link">Войти</router-link>
          <router-link to="/register" class="nav-link">Регистрация</router-link>
        </nav>
      </div>
    </header>

    <!-- Основной контент с двумя колонками (для авторизованных) -->
    <div class="main-layout" v-if="$store.getters.isAuthenticated">
      <main class="app-main">
        <div class="container content-area">
          <div class="content-column">
            <router-view />
          </div>
          <aside class="stats-column">
            <DailyStats />
          </aside>
        </div>
      </main>
    </div>

    <!-- Для неавторизованных просто router-view -->
    <main class="app-main" v-else>
      <div class="container">
        <router-view />
      </div>
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 Учёт времени</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex'
import DailyStats from './components/DailyStats.vue'

export default {
  name: 'App',
  components: { DailyStats },
  data() {
    return {
      fetchInterval: null  // интервал для обновления daily сессии (когда таймер запущен)
    }
  },
  computed: {
    ...mapState(['tasks']),
    ...mapGetters(['currentDailySeconds', 'isDailyTimerRunning'])
  },
  watch: {
    // При изменении статуса таймера запускаем/останавливаем интервал обновления
    isDailyTimerRunning(newVal) {
      if (newVal) {
        this.startFetching()
      } else {
        this.stopFetching()
      }
    }
  },
  methods: {
    ...mapActions(['logout', 'pauseTimer', 'fetchCurrentDailySession', 'fetchDailyStats']),

    async handleLogout() {
      await this.logout()
      this.$router.push('/login')
    },

    // Запуск периодического обновления daily сессии (раз в секунду)
    startFetching() {
      if (this.fetchInterval) clearInterval(this.fetchInterval)
      this.fetchInterval = setInterval(() => {
        this.fetchCurrentDailySession()
      }, 1000)
    },

    stopFetching() {
      if (this.fetchInterval) {
        clearInterval(this.fetchInterval)
        this.fetchInterval = null
      }
    },

    async stopAllActiveTimers() {
      const activeTasks = this.tasks.filter(task => task.is_timer_running)
      for (const task of activeTasks) {
        try {
          await this.pauseTimer(task.id)
          console.log(`Автоматически остановлен таймер задачи: ${task.title}`)
        } catch (error) {
          console.error('Ошибка при остановке таймера:', error)
        }
      }
    },

    handleBeforeUnload(event) {
      const activeTasks = this.tasks.filter(task => task.is_timer_running)
      if (activeTasks.length > 0) {
        event.preventDefault()
        event.returnValue = 'У вас есть активные таймеры. Они будут автоматически остановлены.'
        activeTasks.forEach(task => {
          const data = JSON.stringify({ task_id: task.id })
          navigator.sendBeacon(
            `${process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'}/timer/pause/${task.id}`,
            data
          )
        })
      }
    }
  },

  mounted() {
    // Загружаем начальное состояние
    this.fetchCurrentDailySession()
    this.fetchDailyStats(30)

    // Если таймер уже запущен (например, после логина), запускаем интервал
    if (this.isDailyTimerRunning) {
      this.startFetching()
    }

    window.addEventListener('beforeunload', this.handleBeforeUnload)
    window.addEventListener('unload', this.stopAllActiveTimers)
  },

  beforeUnmount() {
    this.stopFetching()
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
    window.removeEventListener('unload', this.stopAllActiveTimers)
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f8f9fa;
  font-size: 16px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-header {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.title-section {
  text-align: center;
  margin-bottom: 0.5rem;
}

.title-section h1 {
  font-size: 2.5rem;
  margin-bottom: 0.2rem;
}

.title-section p {
  font-size: 1rem;
  opacity: 0.9;
}

.nav {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.btn-logout {
  background-color: transparent;
  border: 1px solid white;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-logout:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.main-layout {
  min-height: calc(100vh - 200px);
}

.content-area {
  display: flex;
  gap: 2rem;
  padding: 2rem 0;
}

.content-column {
  flex: 1;
  min-width: 0;
  /* предотвращает переполнение */
}

.stats-column {
  width: 350px;
  flex-shrink: 0;
}

.app-footer {
  background-color: #343a40;
  color: white;
  text-align: center;
  padding: 1rem 0;
}

/* Адаптивность */
@media (max-width: 1000px) {
  .content-area {
    flex-direction: column;
  }

  .stats-column {
    width: 100%;
  }

  .nav {
    position: static;
    margin-top: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 600px) {
  .title-section h1 {
    font-size: 2rem;
  }
}

/* Остальные общие стили */
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 18px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #1e7e34;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 18px;
}

.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}
</style>