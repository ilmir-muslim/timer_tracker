<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <!-- Блок ставки слева -->
        <div class="rate-display" v-if="$store.getters.isAuthenticated">
          <span>💰 Ставка: {{ $store.getters.defaultHourlyRate }} ₽/час</span>
          <button @click="openRateModal" class="btn-rate-edit">✏️</button>
        </div>

        <!-- Заголовок -->
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

    <!-- Модальное окно изменения ставки -->
    <div v-if="showRateModal" class="modal-overlay" @click="closeRateModal">
      <div class="modal-content" @click.stop>
        <h3>Изменить ставку</h3>
        <div class="form-group">
          <label>Ставка (₽/час):</label>
          <input v-model.number="newRate" type="number" min="0" step="0.01" class="form-control">
        </div>
        <div class="modal-actions">
          <button @click="updateRate" class="btn btn-primary">Сохранить</button>
          <button @click="closeRateModal" class="btn btn-secondary">Отмена</button>
        </div>
      </div>
    </div>

    <div class="main-layout" v-if="$store.getters.isAuthenticated">
      <main class="app-main">
        <div class="container content-area">
          <!-- Левая колонка со статистикой заработка -->
          <aside class="left-column">
            <EarningsSummary />
          </aside>

          <!-- Центральная колонка с проектами -->
          <div class="content-column main-column">
            <router-view />
          </div>

          <!-- Правая колонка со статистикой работы -->
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
import { mapActions, mapGetters } from 'vuex'
import DailyStats from './components/DailyStats.vue'
import EarningsSummary from './components/EarningsSummary.vue'

export default {
  name: 'App',
  components: { DailyStats, EarningsSummary },
  data() {
    return {
      fetchInterval: null,
      showRateModal: false,
      newRate: 0
    }
  },
  computed: {
    ...mapGetters(['isDailyTimerRunning', 'defaultHourlyRate'])
  },
  watch: {
    isDailyTimerRunning(newVal) {
      if (newVal) {
        this.startFetching()
      } else {
        this.stopFetching()
      }
    }
  },
  methods: {
    ...mapActions([
      'logout',
      'pauseTimer',
      'fetchCurrentDailySession',
      'fetchDailyStats',
      'updateDefaultRate',
      'fetchEarningsSummary',
      'fetchUser'                     // ← ADDED
    ]),

    async handleLogout() {
      await this.logout()
      this.$router.push('/login')
    },

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
      const activeTasks = this.$store.state.tasks.filter(task => task.is_timer_running)
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
      const activeTasks = this.$store.state.tasks.filter(task => task.is_timer_running)
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
    },

    openRateModal() {
      this.newRate = this.defaultHourlyRate
      this.showRateModal = true
    },

    closeRateModal() {
      this.showRateModal = false
    },

    async updateRate() {
      try {
        await this.updateDefaultRate(this.newRate)
        await this.fetchEarningsSummary()
        if (this.$toast) {
          this.$toast.success('Ставка обновлена')
        } else {
          console.log('Ставка обновлена')
        }
        this.closeRateModal()
      } catch (error) {
        console.error('Ошибка обновления ставки:', error)
        if (this.$toast) {
          this.$toast.error('Не удалось обновить ставку')
        } else {
          alert('Не удалось обновить ставку')
        }
      }
    }
  },

  mounted() {
    // Загружаем данные пользователя и статистику, если есть токен
    if (this.$store.getters.isAuthenticated) {
      this.fetchUser()                // ← ADDED – загружает пользователя (включая ставку)
      this.fetchEarningsSummary()      // ← ADDED – обновляет статистику заработка
    }

    this.fetchCurrentDailySession()
    this.fetchDailyStats(30)

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
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 30px;
}

.app-header {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.rate-display {
  position: absolute;
  left: 20px;
  top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 15px;
  border-radius: 30px;
  color: white;
  font-weight: 500;
  font-size: 1rem;
}

.btn-rate-edit {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 5px;
  transition: transform 0.2s;
}

.btn-rate-edit:hover {
  transform: scale(1.1);
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
  display: flex;
  width: 100%;
}

.app-main {
  width: 100%;
}

.content-area {
  display: grid;
  grid-template-columns: 350px 1fr 350px;
  gap: 2rem;
  padding: 2rem 0;
  width: 100%;
}

.left-column {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}

.main-column {
  min-width: 0;
}

.content-column {
  flex: 1;
  min-width: 0;
}

.app-footer {
  background-color: #343a40;
  color: white;
  text-align: center;
  padding: 1rem 0;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #343a40;
  font-size: 1.5rem;
  text-align: center;
}

.modal-content .form-group {
  margin-bottom: 1.5rem;
}

.modal-content label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .content-area {
    gap: 1rem;
    grid-template-columns: 280px 1fr 280px;
  }
}

@media (max-width: 1000px) {
  .container {
    padding: 0 20px;
  }

  .content-area {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .left-column {
    order: 1;
    width: 100%;
  }

  .main-column {
    order: 2;
    width: 100%;
  }

  .stats-column {
    order: 3;
    width: 100%;
  }

  .nav {
    position: static;
    margin-top: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .rate-display {
    position: static;
    justify-content: center;
    margin-bottom: 1rem;
  }
}

@media (max-width: 600px) {
  .container {
    padding: 0 15px;
  }

  .title-section h1 {
    font-size: 2rem;
  }
}

/* Общие стили компонентов */
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