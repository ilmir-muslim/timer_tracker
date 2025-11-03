<template>
    <div class="project-detail">

        <div class="header-section">
            <div class="header-top">
                <div class="left-actions">
                    <button @click="$router.push('/')" class="btn back-btn">← Назад к проектам</button>
                </div>
                <div class="header-actions">
                    <button @click="exportToTxt" class="btn btn-export">
                        <span class="btn-icon">📄</span> Экспорт TXT
                    </button>
                    <button @click="copyToClipboard" class="btn btn-copy">
                        <span class="btn-icon">📋</span> Копировать отчет
                    </button>
                    <button @click="stopAllTimers" class="btn btn-warning" v-if="hasActiveTimers">
                        <span class="btn-icon">⏹️</span> Остановить все таймеры
                    </button>
                    <button @click="deleteProjectHandler" class="btn btn-danger">
                        <span class="btn-icon">🗑️</span> Удалить проект
                    </button>
                </div>
            </div>

            <div class="project-info-card">
                <h2 class="project-title">{{ project.name }}</h2>
                <div class="total-time">
                    <span class="label">Общее время проекта:</span>
                    <span class="time">{{ formatTime(localTotalTime) }}</span>
                </div>
            </div>
        </div>

        <div v-if="loading" class="loading">Загрузка...</div>

        <div class="card task-input-card">
            <h3>Добавить новую задачу</h3>
            <div class="task-form">
                <div class="form-group full-width-input">
                    <textarea v-model="newTaskTitle" placeholder="Опишите задачу подробно..."
                        class="form-control task-input" rows="4" @keyup.enter.prevent="addTask">
                    </textarea>
                </div>
                <button @click="addTask" class="btn btn-primary add-task-btn" :disabled="!newTaskTitle.trim()">
                    + Добавить задачу
                </button>
            </div>
        </div>

        <div v-if="projectTasks.length === 0" class="card empty-state">
            <div class="empty-icon">📝</div>
            <h3>Пока нет задач</h3>
            <p>Добавьте первую задачу для отслеживания времени</p>
        </div>

        <div v-else>
            <div class="tasks-header">
                <h3>Задачи ({{ projectTasks.length }})</h3>
                <div class="tasks-summary">
                    Активных таймеров: {{ activeTimersCount }}
                </div>
            </div>
            <div class="tasks-list">
                <div v-for="task in projectTasks" :key="task.id" class="task-item card"
                    :class="{ 'task-active': task.is_timer_running }">
                    <div class="task-content">
                        <div class="task-header">
                            <h4>{{ task.title }}</h4>
                            <span class="task-time">{{ formatTime(task.total_time) }}</span>
                        </div>

                        <div class="task-controls">
                            <div class="timer-controls">
                                <button v-if="!task.is_timer_running" @click="startTaskTimer(task.id)"
                                    class="btn btn-start" :disabled="task.is_timer_running">
                                    <span class="btn-icon">▶</span> Старт
                                </button>
                                <button v-else @click="pauseTaskTimer(task.id)" class="btn btn-pause">
                                    <span class="btn-icon">⏸</span> Пауза
                                </button>
                            </div>

                            <div v-if="task.is_timer_running" class="timer-active-indicator">
                                <span class="pulse"></span>
                                Таймер запущен...
                            </div>

                            <div class="task-actions">
                                <button @click="openEditModal(task)" class="btn btn-edit btn-sm">
                                    <span class="btn-icon">✏️</span>
                                </button>
                                <button @click="deleteTaskHandler(task.id)" class="btn btn-danger btn-sm">
                                    <span class="btn-icon">🗑️</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Модальное окно редактирования задачи -->
        <div v-if="editingTask" class="modal-overlay" @click="closeEditModal">
            <div class="modal-content" @click.stop>
                <h3>Редактировать задачу</h3>

                <div class="form-group">
                    <label>Название задачи:</label>
                    <textarea v-model="editingTask.title" class="form-control" rows="3"></textarea>
                </div>

                <div class="form-group">
                    <label>Время (часы:минуты:секунды):</label>
                    <div class="time-inputs">
                        <input v-model.number="editHours" type="number" min="0" placeholder="ч" class="time-input">
                        <span>:</span>
                        <input v-model.number="editMinutes" type="number" min="0" max="59" placeholder="м"
                            class="time-input">
                        <span>:</span>
                        <input v-model.number="editSeconds" type="number" min="0" max="59" placeholder="с"
                            class="time-input">
                    </div>
                    <div class="time-summary">
                        Всего секунд: {{ totalEditSeconds }} ({{ formatTime(totalEditSeconds) }})
                    </div>
                </div>

                <div class="modal-actions">
                    <button @click="saveTaskEdit" class="btn btn-primary" :disabled="!editingTask.title.trim()">
                        Сохранить
                    </button>
                    <button @click="closeEditModal" class="btn btn-secondary">Отмена</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'

export default {
    name: 'ProjectDetail',
    data() {
        return {
            newTaskTitle: '',
            project: {},
            updateInterval: null,
            loading: true,
            debugMode: false,
            localTotalTime: 0,
            editingTask: null,
            editHours: 0,
            editMinutes: 0,
            editSeconds: 0
        }
    },
    computed: {
        ...mapState(['projects', 'tasks']),
        ...mapGetters(['getTasksByProjectId']),
        projectId() {
            return parseInt(this.$route.params.id)
        },
        projectTasks() {
            return this.getTasksByProjectId(this.projectId)
        },
        activeTimersCount() {
            return this.projectTasks.filter(task => task.is_timer_running).length
        },
        hasActiveTimers() {
            return this.activeTimersCount > 0
        },
        totalEditSeconds() {
            return this.editHours * 3600 + this.editMinutes * 60 + this.editSeconds
        }
    },
    watch: {
        projectTasks: {
            handler(tasks) {
                this.localTotalTime = tasks.reduce((total, task) => total + (task.total_time || 0), 0)

                const projectIndex = this.projects.findIndex(p => p.id === this.projectId)
                if (projectIndex !== -1) {
                    this.$store.state.projects[projectIndex].total_time = this.localTotalTime
                }
            },
            deep: true,
            immediate: true
        }
    },
    methods: {
        ...mapActions([
            'fetchProjects',
            'fetchTasks',
            'startTimer',
            'pauseTimer',
            'createTask',
            'deleteProject',
            'deleteTask',
            'updateTask'
        ]),
        async addTask() {
            if (this.newTaskTitle.trim()) {
                try {
                    await this.createTask({
                        title: this.newTaskTitle,
                        project_id: this.projectId
                    })
                    this.newTaskTitle = ''
                    if (this.$toast) {
                        this.$toast.success('Задача успешно добавлена!')
                    }
                } catch (error) {
                    console.error('Ошибка создания задачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось создать задачу')
                    }
                }
            }
        },
        formatTime(seconds) {
            if (!seconds) return '0ч 0м 0с'
            const hours = Math.floor(seconds / 3600)
            const minutes = Math.floor((seconds % 3600) / 60)
            const secs = Math.floor(seconds % 60)
            return `${hours}ч ${minutes}м ${secs}с`
        },
        async startTaskTimer(taskId) {
            try {
                await this.startTimer(taskId)
                if (this.$toast) {
                    this.$toast.success('Таймер запущен')
                }
            } catch (error) {
                console.error('Ошибка запуска таймера:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось запустить таймер')
                }
            }
        },
        async pauseTaskTimer(taskId) {
            try {
                await this.pauseTimer(taskId)
                if (this.$toast) {
                    this.$toast.info('Таймер на паузе')
                }
            } catch (error) {
                console.error('Ошибка остановки таймера:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось остановить таймер')
                }
            }
        },
        async stopAllTimers() {
            if (this.activeTimersCount === 0) return

            if (confirm(`Остановить все активные таймеры (${this.activeTimersCount})?`)) {
                try {
                    // Останавливаем каждый активный таймер
                    const activeTasks = this.projectTasks.filter(task => task.is_timer_running)
                    for (const task of activeTasks) {
                        await this.pauseTimer(task.id)
                    }

                    if (this.$toast) {
                        this.$toast.success(`Остановлено ${this.activeTimersCount} таймеров`)
                    }
                } catch (error) {
                    console.error('Ошибка остановки таймеров:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось остановить таймеры')
                    }
                }
            }
        },
        generateReportText() {
            let report = `Проект: ${this.project.name}\n`
            report += `Общее время: ${this.formatTime(this.localTotalTime)}\n`
            report += `Сгенерировано: ${new Date().toLocaleString('ru-RU')}\n\n`
            report += 'Задачи:\n'
            report += '='.repeat(50) + '\n\n'

            this.projectTasks.forEach((task, index) => {
                report += `${index + 1}. ${task.title}\n`
                report += `   Время: ${this.formatTime(task.total_time)}\n`
                report += `   Статус: ${task.is_timer_running ? 'Запущен' : 'На паузе'}\n`
                report += '-'.repeat(30) + '\n'
            })

            return report
        },
        exportToTxt() {
            const reportText = this.generateReportText()
            const blob = new Blob([reportText], { type: 'text/plain' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${this.project.name.replace(/\s+/g, '_')}_отчет.txt`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)

            if (this.$toast) {
                this.$toast.success('Отчет успешно экспортирован!')
            }
        },
        async copyToClipboard() {
            try {
                const reportText = this.generateReportText()
                await navigator.clipboard.writeText(reportText)

                if (this.$toast) {
                    this.$toast.success('Отчет скопирован в буфер обмена!')
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось скопировать в буфер обмена')
                }
            }
        },
        async deleteProjectHandler() {
            if (confirm('Вы уверены, что хотите удалить проект? Все задачи будут удалены.')) {
                try {
                    await this.deleteProject(this.projectId)
                    if (this.$toast) {
                        this.$toast.success('Проект удален')
                    }
                    this.$router.push('/')
                } catch (error) {
                    console.error('Ошибка удаления проекта:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить проект')
                    }
                }
            }
        },
        async deleteTaskHandler(taskId) {
            if (confirm('Вы уверены, что хотите удалить задачу?')) {
                try {
                    await this.deleteTask(taskId)
                    if (this.$toast) {
                        this.$toast.success('Задача удалена')
                    }
                } catch (error) {
                    console.error('Ошибка удаления задачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить задачу')
                    }
                }
            }
        },
        openEditModal(task) {
            this.editingTask = { ...task }
            // Конвертируем секунды в часы, минуты, секунды
            const totalSeconds = task.total_time || 0
            this.editHours = Math.floor(totalSeconds / 3600)
            this.editMinutes = Math.floor((totalSeconds % 3600) / 60)
            this.editSeconds = Math.floor(totalSeconds % 60)
        },
        closeEditModal() {
            this.editingTask = null
            this.editHours = 0
            this.editMinutes = 0
            this.editSeconds = 0
        },
        async saveTaskEdit() {
            if (!this.editingTask) return

            try {
                await this.updateTask({
                    taskId: this.editingTask.id,
                    taskData: {
                        title: this.editingTask.title,
                        total_time: this.totalEditSeconds
                    }
                })

                if (this.$toast) {
                    this.$toast.success('Задача успешно обновлена!')
                }

                this.closeEditModal()
                await this.fetchTasks() // Обновляем список задач
            } catch (error) {
                console.error('Ошибка обновления задачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить задачу')
                }
            }
        }
    },
    async mounted() {
        try {
            this.loading = true
            await this.fetchProjects()
            await this.fetchTasks()
            this.project = this.projects.find(p => p.id === this.projectId) || {}

            console.log('Проекты:', this.projects)
            console.log('Задачи:', this.tasks)
            console.log('Задачи проекта:', this.projectTasks)

            // Обновляем задачи каждую секунду, если есть активные таймеры
            this.updateInterval = setInterval(async () => {
                const activeTasks = this.projectTasks.filter(task => task.is_timer_running)
                if (activeTasks.length > 0) {
                    await this.fetchTasks()
                }
            }, 1000)
        } catch (error) {
            console.error('Ошибка загрузки деталей проекта:', error)
            if (this.$toast) {
                this.$toast.error('Не удалось загрузить детали проекта')
            }
        } finally {
            this.loading = false
        }
    },
    beforeUnmount() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval)
        }
    }
}
</script>

<style scoped>
.project-detail {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 20px;
}

.header-section {
    margin-bottom: 2rem;
}

.header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.left-actions {
    display: flex;
    align-items: center;
}

.header-actions {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
}

.project-info-card {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    padding: 2rem;
    border-radius: 16px;
    color: white;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    text-align: center;
    width: 100%;
    margin: 0 auto;
}

.project-info-card h2 {
    font-size: 2.2rem;
    margin-bottom: 1.2rem;
    font-weight: 600;
}

.project-info-card .project-title {
    font-size: 2.2rem;
    margin-bottom: 1.2rem;
    font-weight: 800 !important;
    color: #ffffff !important;
}

.back-btn {
    background-color: #6c757d;
    color: white;
    padding: 12px 24px;
    font-size: 18px;
    border-radius: 8px;
}

.back-btn:hover {
    background-color: #5a6268;
    transform: translateY(-2px);
}

.btn-export {
    background-color: #17a2b8;
    color: white;
}

.btn-export:hover {
    background-color: #138496;
}

.btn-copy {
    background-color: #6f42c1;
    color: white;
}

.btn-copy:hover {
    background-color: #5a2d9c;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-danger:hover {
    background-color: #c82333;
}

.btn-warning {
    background-color: #ffc107;
    color: #212529;
}

.btn-warning:hover {
    background-color: #e0a800;
}

.btn-sm {
    padding: 8px 12px;
    font-size: 14px;
}

.header-section h2 {
    font-size: 2.4rem;
    color: #343a40;
    margin-bottom: 1.5rem;
    font-weight: 600;
}

.total-time {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.total-time .label {
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    opacity: 0.9;
}

.total-time .time {
    font-size: 2rem;
    font-weight: bold;
}

.total-time .time {
    font-size: 2.4rem;
    font-weight: bold;
}

.task-form {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

.full-width-input {
    width: 100%;
}

.task-input {
    min-height: 140px;
    resize: vertical;
    font-size: 18px;
    padding: 15px;
    border-radius: 8px;
    border: 2px solid #e9ecef;
    transition: border-color 0.2s;
    width: 100%;
}

.task-input:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

.add-task-btn {
    padding: 15px 25px;
    font-size: 18px;
    border-radius: 8px;
    align-self: flex-end;
    min-width: 150px;
}

.tasks-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.tasks-header h3 {
    font-size: 1.8rem;
    color: #343a40;
    font-weight: 600;
    margin: 0;
}

.tasks-summary {
    background-color: #e9ecef;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 500;
    color: #495057;
    font-size: 1rem;
}

.tasks-list {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}

.task-item {
    transition: all 0.3s ease;
    padding: 1.8rem;
    border-radius: 12px;
}

.task-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.task-content {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
}

.task-header h4 {
    margin: 0;
    color: #343a40;
    font-size: 1.4rem;
    font-weight: 500;
    flex: 1;
    line-height: 1.4;
}

.task-time {
    background-color: #e9ecef;
    padding: 0.6rem 1.2rem;
    border-radius: 20px;
    font-weight: bold;
    color: #495057;
    font-size: 1.2rem;
    white-space: nowrap;
}

.task-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.timer-controls {
    display: flex;
    gap: 0.8rem;
}

.task-actions {
    display: flex;
    gap: 0.5rem;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 16px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn:active {
    transform: translateY(0);
}

.btn-start {
    background-color: #28a745;
    color: white;
}

.btn-start:hover {
    background-color: #218838;
}

.btn-pause {
    background-color: #ffc107;
    color: #212529;
}

.btn-pause:hover {
    background-color: #e0a800;
}

.btn-edit {
    background-color: #ffc107;
    color: #212529;
}

.btn-edit:hover {
    background-color: #e0a800;
}

.btn-icon {
    margin-right: 8px;
    font-size: 14px;
}

.timer-active-indicator {
    display: flex;
    align-items: center;
    color: #28a745;
    font-weight: 500;
    font-size: 16px;
    padding: 10px 15px;
    background-color: rgba(40, 167, 69, 0.1);
    border-radius: 6px;
}

.pulse {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #28a745;
    margin-right: 0.5rem;
    box-shadow: 0 0 0 rgba(40, 167, 69, 0.4);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(40, 167, 69, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(40, 167, 69, 0);
    }
}

.empty-state {
    text-align: center;
    padding: 3.5rem;
    border-radius: 12px;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
}

.empty-state h3 {
    margin-bottom: 0.5rem;
    color: #6c757d;
    font-size: 1.8rem;
}

.empty-state p {
    color: #6c757d;
    font-size: 1.2rem;
}

.debug-info {
    margin-bottom: 1.5rem;
    padding: 1.5rem;
    border-radius: 12px;
    background-color: #f8f9fa;
}

.debug-btn {
    margin-bottom: 1.5rem;
    font-size: 16px;
}

.loading {
    text-align: center;
    padding: 2rem;
    font-size: 1.4rem;
    color: #6c757d;
}

/* Стили для модального окна редактирования */
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

.time-inputs {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: center;
}

.time-input {
    width: 80px;
    padding: 0.75rem;
    text-align: center;
    border: 2px solid #e9ecef;
    border-radius: 6px;
    font-size: 1rem;
}

.time-input:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.time-summary {
    margin-top: 0.5rem;
    color: #666;
    font-size: 0.9rem;
    text-align: center;
    font-style: italic;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 1.5rem;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5a6268;
}

@media (max-width: 768px) {
    .project-detail {
        padding: 0 15px;
    }

    .header-section h2 {
        font-size: 2rem;
    }

    .header-top {
        flex-direction: column;
        gap: 1rem;
    }

    .header-actions {
        width: 100%;
        justify-content: center;
    }

    .project-info-card {
        padding: 1.5rem;
    }

    .project-info-card h2 {
        font-size: 1.8rem;
    }

    .total-time {
        padding: 1.2rem;
    }

    .total-time .time {
        font-size: 2rem;
    }

    .task-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.8rem;
    }

    .task-controls {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .timer-controls {
        width: 100%;
        justify-content: space-between;
    }

    .btn {
        flex: 1;
        min-width: 120px;
    }

    .back-btn {
        align-self: center;
    }

    .tasks-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .modal-content {
        padding: 1.5rem;
        margin: 1rem;
    }

    .time-inputs {
        flex-wrap: wrap;
    }

    .time-input {
        width: 70px;
    }

    .modal-actions {
        flex-direction: column;
    }
}

@media (max-width: 480px) {
    .header-section h2 {
        font-size: 1.8rem;
    }

    .header-actions {
        flex-direction: column;
    }

    .task-item {
        padding: 1.2rem;
    }

    .task-header h4 {
        font-size: 1.2rem;
    }

    .task-time {
        font-size: 1rem;
        padding: 0.4rem 0.8rem;
    }

    .timer-controls {
        flex-direction: column;
        width: 100%;
    }

    .btn {
        width: 100%;
    }

    .time-input {
        width: 60px;
        padding: 0.5rem;
    }
}
</style>