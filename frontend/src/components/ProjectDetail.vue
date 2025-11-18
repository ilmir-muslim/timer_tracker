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
                    <button @click="generateDailyReport" class="btn btn-daily">
                        <span class="btn-icon">📅</span> Сформировать дейлик
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
                <div class="project-title-section">
                    <h2 class="project-title" v-if="!isEditingProject" @dblclick="startEditingProjectName">
                        {{ project.name }}
                        <button @click="startEditingProjectName" class="btn-edit-project">✏️</button>
                    </h2>
                    <div v-else class="project-name-edit">
                        <input v-model="editingProjectName" @keyup.enter="saveProjectName"
                            @keyup.escape="cancelEditingProjectName" class="project-name-input" type="text">
                        <button @click="saveProjectName" class="btn btn-primary btn-sm">✅</button>
                        <button @click="cancelEditingProjectName" class="btn btn-secondary btn-sm">❌</button>
                    </div>
                </div>
                <div class="total-time">
                    <span class="label">Общее время проекта:</span>
                    <span class="time">{{ formatTime(localTotalTime) }}</span>
                </div>

                <!-- Обновленная статистика с учетом подзадач -->
                <div class="project-stats">
                    <div class="stat-item">
                        <span class="stat-number">{{ totalTasks }}</span>
                        <span class="stat-label">Всего задач</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{{ completedTasks }}</span>
                        <span class="stat-label">Выполнено задач</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{{ totalSubTasks }}</span>
                        <span class="stat-label">Всего подзадач</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{{ completedSubTasks }}</span>
                        <span class="stat-label">Выполнено подзадач</span>
                    </div>
                    <div class="stat-item progress-stat">
                        <span class="stat-number">{{ overallCompletionRate }}%</span>
                        <span class="stat-label">Общий прогресс</span>
                        <div class="progress-bar-mini">
                            <div class="progress-fill" :style="{ width: overallCompletionRate + '%' }"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="task-management-tabs">
            <button @click="activeTab = 'timer'" :class="['tab-btn', { active: activeTab === 'timer' }]">
                ⏱️ Трекер времени
            </button>
            <button @click="activeTab = 'tasks'" :class="['tab-btn', { active: activeTab === 'tasks' }]">
                ✅ Трекер задач
            </button>
        </div>

        <!-- Трекер времени (существующий функционал) -->
        <div v-if="activeTab === 'timer'" class="timer-tab">
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
        </div>

        <!-- Трекер задач (новый функционал) -->
        <div v-else class="tasks-tab">
            <div class="card task-input-card">
                <h3>Добавить новую задачу</h3>
                <div class="task-form">
                    <div class="form-group full-width-input">
                        <textarea v-model="newTaskTitle" placeholder="Опишите задачу подробно..."
                            class="form-control task-input" rows="3">
                        </textarea>
                    </div>
                    <div class="task-options">
                        <select v-model="newTaskPriority" class="form-control priority-select">
                            <option value="1">🔴 Высокий приоритет</option>
                            <option value="2">🟡 Средний приоритет</option>
                            <option value="3">🟢 Низкий приоритет</option>
                        </select>
                        <input v-model="newTaskDueDate" type="date" class="form-control date-input">
                    </div>
                    <button @click="addTask" class="btn btn-primary add-task-btn" :disabled="!newTaskTitle.trim()">
                        ➕ Добавить задачу
                    </button>
                </div>
            </div>  
            <!-- Фильтры задач -->
            <div class="task-filters card">
                <button @click="taskView = 'all'" :class="['filter-btn', { active: taskView === 'all' }]">
                    Все
                </button>
                <button @click="taskView = 'active'" :class="['filter-btn', { active: taskView === 'active' }]">
                    Активные
                </button>
                <button @click="taskView = 'completed'" :class="['filter-btn', { active: taskView === 'completed' }]">
                    Завершенные
                </button>
            </div>

            <!-- Список задач -->
            <div v-if="sortedTasks.length === 0" class="card empty-state">
                <div class="empty-icon">📝</div>
                <h3>Пока нет задач</h3>
                <p>Добавьте первую задачу для отслеживания прогресса</p>
            </div>

            <div v-else class="tasks-list">
                <div v-for="task in sortedTasks" :key="task.id" class="task-item card" :class="{
                    'task-completed': task.is_completed,
                    'priority-high': task.priority === 1,
                    'priority-medium': task.priority === 2,
                    'priority-low': task.priority === 3
                }">

                    <!-- Заголовок задачи -->
                    <div class="task-header">
                        <div class="task-main-info">
                            <input type="checkbox" :checked="task.is_completed"
                                @change="toggleTaskCompletion(task.id, $event.target.checked)" class="task-checkbox">
                            <h4 :class="{ 'completed-text': task.is_completed }">{{ task.title }}</h4>
                        </div>
                        <div class="task-meta">
                            <span class="task-priority" :class="`priority-${task.priority}`">
                                {{ getPriorityLabel(task.priority) }}
                            </span>
                            <span v-if="task.due_date" class="task-due-date">
                                📅 {{ formatDate(task.due_date) }}
                            </span>
                            <div class="task-header-actions">
                                <button @click="copySingleTaskToClipboard(task)" class="btn btn-sm btn-copy">
                                    📋 Копировать
                                </button>
                                <button @click="openEditTaskModal(task)" class="btn btn-sm btn-edit">
                                    ✏️
                                </button>
                                <button @click="deleteTaskHandler(task.id)" class="btn btn-sm btn-danger">
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Прогресс подзадач -->
                    <div v-if="getTotalSubTasksCount(task.id) > 0" class="subtasks-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: getSubTasksProgress(task.id) + '%' }"></div>
                        </div>
                        <span class="progress-text">
                            {{ getCompletedSubTasksCount(task.id) }}/{{ getTotalSubTasksCount(task.id) }} подзадач
                        </span>
                    </div>

                    <!-- Подзадачи -->
                    <div class="subtasks-section">
                        <div v-for="subTask in getSubTasks(task.id)" :key="subTask.id" class="subtask-item">
                            <input type="checkbox" :checked="subTask.is_completed"
                                @change="toggleSubTaskCompletion(task.id, subTask.id, $event.target.checked)"
                                class="subtask-checkbox">
                            <span :class="{ 'completed-text': subTask.is_completed }"
                                @dblclick="startEditingSubTask(subTask)" v-if="!editingSubTasks[subTask.id]">
                                {{ subTask.title }}
                            </span>
                            <input v-else v-model="editingSubTaskTitles[subTask.id]"
                                @blur="saveSubTaskEdit(task.id, subTask.id)"
                                @keyup.enter="saveSubTaskEdit(task.id, subTask.id)"
                                @keyup.escape="cancelSubTaskEdit(subTask.id)" class="subtask-edit-input" type="text">
                            
                            <!-- Комментарии подзадачи -->
                            <div class="subtask-comments">
                                <div v-for="comment in getSubTaskComments(subTask.id)" :key="comment.id" class="subtask-comment">
                                    <div class="comment-content">
                                        {{ comment.content }}
                                    </div>
                                    <div class="comment-meta">
                                        <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                                        <button @click="deleteSubTaskComment(subTask.id, comment.id)" class="btn btn-sm btn-danger">
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                                
                                <div class="add-subtask-comment">
                                    <textarea v-model="newSubTaskCommentContents[subTask.id]" 
                                        @keyup.ctrl.enter="addSubTaskComment(subTask.id)"
                                        placeholder="Комментарий к подзадаче (Ctrl+Enter для отправки)..."
                                        class="form-control subtask-comment-input" rows="2"></textarea>
                                    <button @click="addSubTaskComment(subTask.id)" class="btn btn-sm btn-primary">
                                        💬
                                    </button>
                                </div>
                            </div>
                            
                            <div class="subtask-actions">
                                <button v-if="!editingSubTasks[subTask.id]" @click="startEditingSubTask(subTask)"
                                    class="btn btn-sm btn-edit">
                                    ✏️
                                </button>
                                <button @click="deleteSubTaskHandler(task.id, subTask.id)"
                                    class="btn btn-sm btn-danger">
                                    🗑️
                                </button>
                            </div>
                        </div>

                        <div class="add-subtask">
                            <input v-model="newSubTaskTitles[task.id]" @keyup.enter="addSubTask(task.id)"
                                placeholder="Добавить подзадачу..." class="form-control subtask-input">
                            <button @click="addSubTask(task.id)" class="btn btn-sm btn-primary">
                                +
                            </button>
                        </div>
                    </div>

                    <!-- Комментарии -->
                    <div class="comments-section">
                        <div class="comments-list">
                            <div v-for="comment in getTaskComments(task.id)" :key="comment.id" class="comment-item">
                                <div class="comment-content">
                                    {{ comment.content }}
                                </div>
                                <div class="comment-meta">
                                    <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                                    <button @click="deleteComment(task.id, comment.id)" class="btn btn-sm btn-danger">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div class="add-comment">
                            <textarea v-model="newCommentContents[task.id]" @keyup.ctrl.enter="addComment(task.id)"
                                placeholder="Добавить комментарий (Ctrl+Enter для отправки)..."
                                class="form-control comment-input" rows="2"></textarea>
                            <button @click="addComment(task.id)" class="btn btn-sm btn-primary">
                                💬
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Кнопки экспорта -->
        <div class="export-actions">
            <button @click="exportTaskReport" class="btn btn-export">
                📊 Экспорт отчета по задачам
            </button>
            <button @click="copyTaskReport" class="btn btn-copy">
                📋 Копировать отчет
            </button>
        </div>

        <!-- Модальное окно редактирования задачи (для трекера времени) -->
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

        <!-- Модальное окно редактирования задачи (для трекера задач) -->
        <div v-if="editingTaskModal" class="modal-overlay" @click="closeEditTaskModal">
            <div class="modal-content" @click.stop>
                <h3>Редактировать задачу</h3>

                <div class="form-group">
                    <label>Название задачи:</label>
                    <textarea v-model="editingTaskData.title" class="form-control" rows="3"></textarea>
                </div>

                <div class="form-group">
                    <label>Приоритет:</label>
                    <select v-model="editingTaskData.priority" class="form-control">
                        <option value="1">🔴 Высокий приоритет</option>
                        <option value="2">🟡 Средний приоритет</option>
                        <option value="3">🟢 Низкий приоритет</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Срок выполнения:</label>
                    <input v-model="editingTaskData.due_date" type="date" class="form-control">
                </div>

                <div class="modal-actions">
                    <button @click="saveTaskEditModal" class="btn btn-primary"
                        :disabled="!editingTaskData.title.trim()">
                        Сохранить
                    </button>
                    <button @click="closeEditTaskModal" class="btn btn-secondary">Отмена</button>
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
            editSeconds: 0,

            // Новые данные для трекера задач
            activeTab: 'timer', // 'timer' или 'tasks'
            newTaskPriority: 2,
            newTaskDueDate: '',
            newSubTaskTitles: {},
            newCommentContents: {},
            newSubTaskCommentContents: {}, // Новое поле для комментариев подзадач
            taskView: 'all', // 'all', 'active', 'completed'

            // Редактирование подзадач
            editingSubTasks: {},
            editingSubTaskTitles: {},

            // Редактирование задачи
            editingTaskModal: false,
            editingTaskData: null,

            // Редактирование проекта
            editingProjectName: '',
            isEditingProject: false
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

        // Новые computed для учета подзадач в прогрессе
        totalSubTasks() {
            let total = 0
            this.projectTasks.forEach(task => {
                total += this.getTotalSubTasksCount(task.id)
            })
            return total
        },

        completedSubTasks() {
            let completed = 0
            this.projectTasks.forEach(task => {
                completed += this.getCompletedSubTasksCount(task.id)
            })
            return completed
        },

        // Общий прогресс с учетом подзадач
        overallCompletionRate() {
            const totalItems = this.totalTasks + this.totalSubTasks
            const completedItems = this.completedTasks + this.completedSubTasks
            return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0
        },

        activeTimersCount() {
            return this.projectTasks.filter(task => task.is_timer_running).length
        },
        hasActiveTimers() {
            return this.activeTimersCount > 0
        },
        totalEditSeconds() {
            return this.editHours * 3600 + this.editMinutes * 60 + this.editSeconds
        },

        // Новые computed для трекера задач
        taskTrackerTasks() {
            return this.projectTasks.filter(task => {
                if (this.taskView === 'active') return !task.is_completed
                if (this.taskView === 'completed') return task.is_completed
                return true
            })
        },

        // Сортировка задач по дате и приоритету
        sortedTasks() {
            return [...this.taskTrackerTasks].sort((a, b) => {
                // Сначала незавершенные, затем завершенные
                if (a.is_completed !== b.is_completed) {
                    return a.is_completed ? 1 : -1
                }

                // Затем по дате выполнения (ближайшие сверху)
                const aDate = a.due_date ? new Date(a.due_date) : new Date('9999-12-31')
                const bDate = b.due_date ? new Date(b.due_date) : new Date('9999-12-31')

                if (aDate.getTime() !== bDate.getTime()) {
                    return aDate - bDate
                }

                // Затем по приоритету (высокий сначала)
                if (a.priority !== b.priority) {
                    return a.priority - b.priority
                }

                // Затем по дате создания (новые сначала)
                return new Date(b.created_at) - new Date(a.created_at)
            })
        },

        // Статистика
        totalTasks() {
            return this.projectTasks.length
        },
        completedTasks() {
            return this.projectTasks.filter(task => task.is_completed).length
        },
        pendingTasks() {
            return this.totalTasks - this.completedTasks
        },
        completionRate() {
            return this.totalTasks > 0 ? Math.round((this.completedTasks / this.totalTasks) * 100) : 0
        },

        // Геттеры из store
        ...mapGetters([
            'getTaskComments',
            'getSubTasks',
            'getCompletedSubTasksCount',
            'getTotalSubTasksCount',
            'getSubTaskComments' // Новый геттер для комментариев подзадач
        ])
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
            'updateTask',
            'updateProject',
            'fetchTaskComments',
            'createTaskComment',
            'deleteTaskComment',
            'fetchSubTasks',
            'createSubTask',
            'updateSubTask',
            'deleteSubTask',
            'updateTaskStatus',
            'fetchSubTaskComments', // Новые actions для комментариев подзадач
            'createSubTaskComment',
            'deleteSubTaskComment'
        ]),

        // Новые методы для редактирования названия проекта
        startEditingProjectName() {
            this.editingProjectName = this.project.name
            this.isEditingProject = true
        },

        async saveProjectName() {
            if (this.editingProjectName.trim() && this.editingProjectName !== this.project.name) {
                try {
                    await this.updateProject({
                        projectId: this.projectId,
                        projectData: {
                            name: this.editingProjectName.trim()
                        }
                    })
                    await this.fetchProjects() // Обновляем список проектов
                    this.project = this.projects.find(p => p.id === this.projectId) || {}
                    if (this.$toast) {
                        this.$toast.success('Название проекта успешно обновлено!')
                    }
                } catch (error) {
                    console.error('Ошибка обновления проекта:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось обновить название проекта')
                    }
                }
            }
            this.cancelEditingProjectName()
        },

        cancelEditingProjectName() {
            this.editingProjectName = ''
            this.isEditingProject = false
        },

        async addTask() {
            if (this.newTaskTitle.trim()) {
                try {
                    const taskData = {
                        title: this.newTaskTitle,
                        project_id: this.projectId
                    }

                    // Если мы в режиме трекера задач, добавляем дополнительные поля
                    if (this.activeTab === 'tasks') {
                        taskData.priority = parseInt(this.newTaskPriority)
                        if (this.newTaskDueDate) {
                            // Преобразуем дату в правильный формат для бэкенда
                            taskData.due_date = this.formatDateForBackend(this.newTaskDueDate)
                        }
                    }

                    await this.createTask(taskData)
                    this.newTaskTitle = ''
                    this.newTaskDueDate = ''
                    this.newTaskPriority = 2

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
        },

        // Новые методы для трекера задач
        getPriorityLabel(priority) {
            const labels = {
                1: '🔴 Высокий',
                2: '🟡 Средний',
                3: '🟢 Низкий'
            }
            return labels[priority] || '🟢 Низкий'
        },

        async toggleTaskCompletion(taskId, isCompleted) {
            try {
                await this.updateTaskStatus({ taskId, isCompleted })
                if (this.$toast) {
                    this.$toast.success(isCompleted ? 'Задача выполнена!' : 'Задача возобновлена')
                }
            } catch (error) {
                console.error('Ошибка обновления статуса задачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить статус задачи')
                }
            }
        },

        async addSubTask(taskId) {
            const title = this.newSubTaskTitles[taskId]?.trim()
            if (!title) return

            try {
                await this.createSubTask({ taskId, title })
                this.newSubTaskTitles[taskId] = ''
                if (this.$toast) {
                    this.$toast.success('Подзадача добавлена')
                }
            } catch (error) {
                console.error('Ошибка создания подзадачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось добавить подзадачу')
                }
            }
        },

        async toggleSubTaskCompletion(taskId, subTaskId, isCompleted) {
            try {
                await this.updateSubTask({
                    taskId,
                    subTaskId,
                    subTaskData: { is_completed: isCompleted }
                })
            } catch (error) {
                console.error('Ошибка обновления подзадачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить подзадачу')
                }
            }
        },

        async deleteSubTaskHandler(taskId, subTaskId) {
            if (confirm('Удалить подзадачу?')) {
                try {
                    await this.deleteSubTask({ taskId, subTaskId })
                    if (this.$toast) {
                        this.$toast.success('Подзадача удалена')
                    }
                } catch (error) {
                    console.error('Ошибка удаления подзадачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить подзадачу')
                    }
                }
            }
        },

        // Исправленные методы для Vue 3 (без $set)
        startEditingSubTask(subTask) {
            this.editingSubTasks = {
                ...this.editingSubTasks,
                [subTask.id]: true
            }
            this.editingSubTaskTitles = {
                ...this.editingSubTaskTitles,
                [subTask.id]: subTask.title
            }
        },

        async saveSubTaskEdit(taskId, subTaskId) {
            const title = this.editingSubTaskTitles[subTaskId]?.trim()
            if (!title) {
                this.cancelSubTaskEdit(subTaskId)
                return
            }

            try {
                await this.updateSubTask({
                    taskId,
                    subTaskId,
                    subTaskData: { title }
                })

                // Создаем новые объекты без удаляемых свойств
                const newEditingSubTasks = { ...this.editingSubTasks }
                delete newEditingSubTasks[subTaskId]
                this.editingSubTasks = newEditingSubTasks

                const newEditingSubTaskTitles = { ...this.editingSubTaskTitles }
                delete newEditingSubTaskTitles[subTaskId]
                this.editingSubTaskTitles = newEditingSubTaskTitles

                if (this.$toast) {
                    this.$toast.success('Подзадача обновлена')
                }
            } catch (error) {
                console.error('Ошибка обновления подзадачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить подзадачу')
                }
            }
        },

        cancelSubTaskEdit(subTaskId) {
            // Создаем новые объекты без удаляемых свойств
            const newEditingSubTasks = { ...this.editingSubTasks }
            delete newEditingSubTasks[subTaskId]
            this.editingSubTasks = newEditingSubTasks

            const newEditingSubTaskTitles = { ...this.editingSubTaskTitles }
            delete newEditingSubTaskTitles[subTaskId]
            this.editingSubTaskTitles = newEditingSubTaskTitles
        },

        async addComment(taskId) {
            const content = this.newCommentContents[taskId]?.trim()
            if (!content) return

            try {
                await this.createTaskComment({ taskId, content })
                this.newCommentContents[taskId] = ''
                if (this.$toast) {
                    this.$toast.success('Комментарий добавлен')
                }
            } catch (error) {
                console.error('Ошибка создания комментария:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось добавить комментарий')
                }
            }
        },

        async deleteComment(taskId, commentId) {
            if (confirm('Удалить комментарий?')) {
                try {
                    await this.deleteTaskComment({ taskId, commentId })
                    if (this.$toast) {
                        this.$toast.success('Комментарий удален')
                    }
                } catch (error) {
                    console.error('Ошибка удаления комментария:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить комментарий')
                    }
                }
            }
        },

        // Новые методы для комментариев подзадач
        async addSubTaskComment(subTaskId) {
            const content = this.newSubTaskCommentContents[subTaskId]?.trim();
            if (!content) return;

            try {
                await this.createSubTaskComment({ subTaskId, content });
                this.newSubTaskCommentContents[subTaskId] = '';
                if (this.$toast) {
                    this.$toast.success('Комментарий к подзадаче добавлен');
                }
            } catch (error) {
                console.error('Ошибка создания комментария подзадачи:', error);
                if (this.$toast) {
                    this.$toast.error('Не удалось добавить комментарий к подзадаче');
                }
            }
        },

        async deleteSubTaskComment(subTaskId, commentId) {
            if (confirm('Удалить комментарий к подзадаче?')) {
                try {
                    await this.deleteSubTaskComment({ subTaskId, commentId });
                    if (this.$toast) {
                        this.$toast.success('Комментарий к подзадаче удален');
                    }
                } catch (error) {
                    console.error('Ошибка удаления комментария подзадачи:', error);
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить комментарий к подзадаче');
                    }
                }
            }
        },

        // Вспомогательные методы для комментариев подзадач в дейлике
        getSubTaskCommentsForDate(subTaskId, date) {
            const comments = this.getSubTaskComments(subTaskId);
            return comments.filter(comment => {
                const commentDate = new Date(comment.created_at);
                return commentDate.toDateString() === date.toDateString();
            });
        },

        getRecentSubTaskComments(subTaskId, days = 2) {
            const comments = this.getSubTaskComments(subTaskId);
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - days);

            return comments.filter(comment => {
                const commentDate = new Date(comment.created_at);
                return commentDate >= cutoffDate;
            });
        },

        getSubTasksProgress(taskId) {
            const total = this.getTotalSubTasksCount(taskId)
            const completed = this.getCompletedSubTasksCount(taskId)
            return total > 0 ? Math.round((completed / total) * 100) : 0
        },

        // Редактирование задачи с правильной обработкой дат
        openEditTaskModal(task) {
            this.editingTaskData = {
                ...task,
                priority: task.priority || 2,
                // Правильно преобразуем дату для input type="date"
                due_date: task.due_date ? this.formatDateForInput(task.due_date) : ''
            }
            this.editingTaskModal = true
        },

        closeEditTaskModal() {
            this.editingTaskData = null
            this.editingTaskModal = false
        },

        async saveTaskEditModal() {
            if (!this.editingTaskData) return

            try {
                const taskData = {
                    title: this.editingTaskData.title,
                    priority: parseInt(this.editingTaskData.priority)
                }

                if (this.editingTaskData.due_date) {
                    taskData.due_date = this.formatDateForBackend(this.editingTaskData.due_date)
                } else {
                    // Если дата удалена, отправляем null
                    taskData.due_date = null
                }

                await this.updateTask({
                    taskId: this.editingTaskData.id,
                    taskData
                })

                if (this.$toast) {
                    this.$toast.success('Задача успешно обновлена!')
                }

                this.closeEditTaskModal()
                await this.fetchTasks()
            } catch (error) {
                console.error('Ошибка обновления задачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить задачу')
                }
            }
        },

        // Вспомогательные методы для работы с датами
        formatDateForInput(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            // Корректируем дату для правильного отображения в input type="date"
            const localDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
            return localDate.toISOString().split('T')[0]
        },

        formatDateForBackend(dateString) {
            if (!dateString) return null
            // Преобразуем дату из формата input в ISO строку
            const date = new Date(dateString)
            return date.toISOString()
        },

        // Метод для получения даты вчера (игнорируя выходные)
        getYesterdayDate() {
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(today.getDate() - 1);

            // Если вчера была суббота (6) или воскресенье (0), берем пятницу
            if (yesterday.getDay() === 0) { // Воскресенье
                yesterday.setDate(today.getDate() - 2);
            } else if (yesterday.getDay() === 6) { // Суббота
                yesterday.setDate(today.getDate() - 1);
            }

            return yesterday;
        },

        // Метод для форматирования даты в читаемый вид
        formatDateForReport(date) {
            return date.toLocaleDateString('ru-RU', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        // Метод для получения дат за которые нужно отчитаться (рабочие дни + выходные если работали)
        getReportDates() {
            const today = new Date();
            const dayOfWeek = today.getDay(); // 0 - воскресенье, 1 - понедельник, etc

            // Если сегодня понедельник (1), показываем пятницу, субботу и воскресенье
            if (dayOfWeek === 1) {
                const friday = new Date(today);
                friday.setDate(today.getDate() - 3);
                const saturday = new Date(today);
                saturday.setDate(today.getDate() - 2);
                const sunday = new Date(today);
                sunday.setDate(today.getDate() - 1);
                return {
                    yesterday: friday, // Показываем как "вчера" пятницу
                    additionalDays: [saturday, sunday], // Дополнительные дни (выходные)
                    isWeekendIncluded: true
                };
            }

            // Если сегодня воскресенье (0) или суббота (6) - работа в выходные
            if (dayOfWeek === 0 || dayOfWeek === 6) {
                const yesterday = new Date(today);
                yesterday.setDate(today.getDate() - 1);
                return {
                    yesterday,
                    additionalDays: [],
                    isWeekendIncluded: true
                };
            }

            // Обычный рабочий день
            const yesterday = new Date(today);
            yesterday.setDate(today.getDate() - 1);

            // Если вчера была пятница (5), включаем информацию о предстоящих выходных
            if (yesterday.getDay() === 5) {
                return {
                    yesterday,
                    additionalDays: [],
                    isWeekendWarning: true
                };
            }

            return {
                yesterday,
                additionalDays: [],
                isWeekendIncluded: false
            };
        },

        // МЕТОД ГЕНЕРАЦИИ ДЕЙЛИКА С КОММЕНТАРИЯМИ ПОДЗАДАЧ
        async generateDailyReport() {
            try {
                const today = new Date();
                const yesterday = new Date(today);
                yesterday.setDate(today.getDate() - 1);

                let report = `📅 Дейлик ${this.formatDateForReport(today)}\n`;
                report += `📋 Проект: ${this.project.name}\n\n`;

                // Раздел "СДЕЛАЛ ВЧЕРА"
                report += `✅ СДЕЛАЛ ВЧЕРА (${this.formatDateForReport(yesterday)}):\n`;

                let hasYesterdayProgress = false;

                // Проходим по всем задачам проекта
                for (const task of this.projectTasks) {
                    const subTasks = this.getSubTasks(task.id);
                    let hasTaskProgress = false;
                    let taskReport = '';

                    // Проверяем завершенные подзадачи за вчера
                    const completedSubTasksYesterday = subTasks.filter(subTask =>
                        subTask.completed_at &&
                        new Date(subTask.completed_at).toDateString() === yesterday.toDateString()
                    );

                    // Если есть завершенные подзадачи вчера
                    if (completedSubTasksYesterday.length > 0) {
                        hasYesterdayProgress = true;
                        hasTaskProgress = true;
                        taskReport += `- ${task.title}\n`;

                        completedSubTasksYesterday.forEach(subTask => {
                            taskReport += `  └─ ✅ ${subTask.title}\n`;

                            // ВЫВОДИМ ВСЕ КОММЕНТАРИИ ПОДЗАДАЧИ БЕЗ ФИЛЬТРАЦИИ ПО ДАТЕ
                            const subTaskComments = this.getSubTaskComments(subTask.id);
                            if (subTaskComments.length > 0) {
                                taskReport += `    💬 Комментарии к подзадаче:\n`;
                                subTaskComments.forEach(comment => {
                                    taskReport += `      └─ ${comment.content}\n`;
                                });
                            }
                        });

                        // ВЫВОДИМ ВСЕ КОММЕНТАРИИ ЗАДАЧИ БЕЗ ФИЛЬТРАЦИИ ПО ДАТЕ
                        const taskComments = this.getTaskComments(task.id);
                        if (taskComments.length > 0) {
                            taskReport += `  💬 Комментарии к задаче:\n`;
                            taskComments.forEach(comment => {
                                taskReport += `    └─ ${comment.content}\n`;
                            });
                        }

                        taskReport += '\n';
                    }

                    // Проверяем завершенные задачи за вчера
                    if (task.completed_at && new Date(task.completed_at).toDateString() === yesterday.toDateString()) {
                        hasYesterdayProgress = true;
                        // Если задача уже была выведена с подзадачами, не дублируем
                        if (!hasTaskProgress) {
                            taskReport += `- ${task.title}\n`;

                            // ВЫВОДИМ ВСЕ КОММЕНТАРИИ ЗАДАЧИ БЕЗ ФИЛЬТРАЦИИ ПО ДАТЕ
                            const taskComments = this.getTaskComments(task.id);
                            if (taskComments.length > 0) {
                                taskComments.forEach(comment => {
                                    taskReport += `  💬 ${comment.content}\n`;
                                });
                            }
                            taskReport += '\n';
                        }
                    }

                    report += taskReport;
                }

                if (!hasYesterdayProgress) {
                    report += "- Не было выполненных задач\n";
                }

                // Раздел "ДЕЛАЮ СЕГОДНЯ"
                report += `\n🎯 ДЕЛАЮ СЕГОДНЯ (${this.formatDateForReport(today)}):\n`;

                // Берем незавершенные задачи с высоким приоритетом или с сегодняшним сроком
                const todayTasks = this.sortedTasks.filter(task =>
                    !task.is_completed &&
                    (task.priority === 1 || (task.due_date && this.isDueToday(task.due_date)))
                ).slice(0, 5); // Ограничиваем количество

                if (todayTasks.length === 0) {
                    report += "- Нет активных задач\n";
                } else {
                    todayTasks.forEach(task => {
                        const subTasks = this.getSubTasks(task.id);
                        const pendingSubTasks = subTasks.filter(st => !st.is_completed);
                        const completedSubTasksYesterday = subTasks.filter(subTask =>
                            subTask.completed_at &&
                            new Date(subTask.completed_at).toDateString() === yesterday.toDateString()
                        );

                        // Проверяем, есть ли вчерашний прогресс по этой задаче
                        const hasYesterdayProgress = completedSubTasksYesterday.length > 0 ||
                            (task.completed_at && new Date(task.completed_at).toDateString() === yesterday.toDateString());

                        if (hasYesterdayProgress) {
                            report += `- ${task.title} (продолжение)\n`;
                        } else {
                            report += `- ${task.title}\n`;
                        }

                        if (pendingSubTasks.length > 0) {
                            report += `  └─ Осталось выполнить:\n`;
                            pendingSubTasks.forEach(subTask => {
                                report += `    ⭕️ ${subTask.title}\n`;
                            });
                        }

                        // ВЫВОДИМ ВСЕ КОММЕНТАРИИ ЗАДАЧИ БЕЗ ФИЛЬТРАЦИИ ПО ДАТЕ
                        const taskComments = this.getTaskComments(task.id);
                        if (taskComments.length > 0) {
                            report += `  💬 Комментарии к задаче:\n`;
                            taskComments.forEach(comment => {
                                report += `    └─ ${comment.content}\n`;
                            });
                        }

                        // Информация о приоритете и сроке (только для новых задач)
                        if (!hasYesterdayProgress) {
                            report += `  └─ Приоритет: ${this.getPriorityLabel(task.priority)}\n`;

                            if (task.due_date && this.isDueToday(task.due_date)) {
                                report += `  └─ ⚠️ Срок: СЕГОДНЯ\n`;
                            }
                        }

                        report += '\n';
                    });
                }

                // Статистика
                report += `📊 СТАТИСТИКА:\n`;
                report += `├─ Выполнено задач: ${this.completedTasks}/${this.totalTasks}\n`;
                report += `├─ Выполнено подзадач: ${this.completedSubTasks}/${this.totalSubTasks}\n`;
                report += `└─ Общий прогресс: ${this.overallCompletionRate}%\n`;

                await this.copyToClipboardCustom(report, 'Дейлик успешно скопирован в буфер обмена!');

            } catch (error) {
                console.error('Ошибка генерации дейлика:', error);
                if (this.$toast) {
                    this.$toast.error('Не удалось сформировать дейлик');
                }
            }
        },

        // Исправленный метод получения задач на сегодня
        getTodayTasks(yesterdayProgress) {
            const todayTasks = [];
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            // 1. В первую очередь добавляем задачи, которые не доделали вчера
            yesterdayProgress.forEach(item => {
                if (item.type === 'completed_subtasks') {
                    const task = this.projectTasks.find(t => t.id === item.taskId);
                    if (task && !task.is_completed) {
                        todayTasks.push({
                            ...task,
                            isContinuation: true
                        });
                    }
                }
            });

            // 2. Добавляем срочные задачи на сегодня (максимум 2-3, чтобы не перегружать)
            const urgentTasks = this.sortedTasks
                .filter(task => {
                    if (task.is_completed) return false;
                    if (todayTasks.find(t => t.id === task.id)) return false; // Не дублируем

                    // Включаем задачи с высоким приоритетом ИЛИ сроком на сегодня
                    return task.priority === 1 ||
                        (task.due_date && this.isDueToday(task.due_date));
                })
                .slice(0, 3); // Ограничиваем количество

            urgentTasks.forEach(task => {
                todayTasks.push({
                    ...task,
                    isContinuation: false
                });
            });

            return todayTasks;
        },

        // Вспомогательный метод для проверки срока сегодня
        isDueToday(dueDate) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const due = new Date(dueDate);
            due.setHours(0, 0, 0, 0);

            return due.getTime() === today.getTime();
        },

        // Исправленный метод получения вчерашнего прогресса
        getYesterdayProgress(yesterday) {
            const progress = [];
            const processedTasks = new Set();

            // 1. Завершенные задачи вчера
            this.projectTasks.forEach(task => {
                if (task.completed_at && new Date(task.completed_at).toDateString() === yesterday.toDateString()) {
                    progress.push({
                        type: 'completed_task',
                        title: task.title,
                        taskId: task.id,
                        comments: this.getCommentsForDate(task.id, yesterday)
                    });
                    processedTasks.add(task.id);
                }
            });

            // 2. Подзадачи, завершенные вчера (для незавершенных задач)
            this.projectTasks.forEach(task => {
                if (processedTasks.has(task.id)) return;

                const subTasks = this.getSubTasks(task.id);
                const yesterdaySubTasks = subTasks.filter(subTask => {
                    if (!subTask.completed_at) return false;
                    const completedDate = new Date(subTask.completed_at);
                    return completedDate.toDateString() === yesterday.toDateString();
                });

                if (yesterdaySubTasks.length > 0) {
                    progress.push({
                        type: 'completed_subtasks',
                        taskTitle: task.title,
                        taskId: task.id,
                        subTasks: yesterdaySubTasks,
                        comments: this.getCommentsForDate(task.id, yesterday)
                    });
                }
            });

            return progress;
        },

        // Вспомогательные методы для дейлика
        getCommentsForDate(taskId, date) {
            const comments = this.getTaskComments(taskId);
            return comments.filter(comment => {
                const commentDate = new Date(comment.created_at);
                return commentDate.toDateString() === date.toDateString();
            });
        },

        getRecentComments(taskId, days = 2) {
            const comments = this.getTaskComments(taskId);
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - days);

            return comments.filter(comment => {
                const commentDate = new Date(comment.created_at);
                return commentDate >= cutoffDate;
            });
        },

        // Вспомогательный метод для копирования с кастомным сообщением
        async copyToClipboardCustom(text, successMessage) {
            try {
                await navigator.clipboard.writeText(text);
                if (this.$toast) {
                    this.$toast.success(successMessage);
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error);
                // Fallback для старых браузеров
                this.showCopyFallbackWithMessage(text, successMessage);
            }
        },

        // Обновленный метод showCopyFallback с поддержкой кастомного сообщения
        showCopyFallbackWithMessage(text, successMessage) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                document.execCommand('copy');
                if (this.$toast) {
                    this.$toast.success(successMessage);
                }
            } catch (e) {
                this.showManualCopyPrompt(text);
            } finally {
                document.body.removeChild(textArea);
            }
        },

        // Копирование отдельной задачи в буфер обмена
        async copySingleTaskToClipboard(task) {
            try {
                const reportText = this.generateSingleTaskReport(task)
                await navigator.clipboard.writeText(reportText)

                if (this.$toast) {
                    this.$toast.success('Отчет по задаче скопирован в буфер обмена!')
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error)
                this.showCopyFallback(this.generateSingleTaskReport(task))
            }
        },

        // Альтернативный метод копирования (используется в copySingleTaskToClipboard)
        showCopyFallback(text) {
            // Создаем временный textarea для копирования
            const textArea = document.createElement('textarea')
            textArea.value = text
            textArea.style.position = 'fixed'
            textArea.style.left = '-999999px'
            textArea.style.top = '-999999px'
            document.body.appendChild(textArea)
            textArea.focus()
            textArea.select()

            try {
                // Пытаемся использовать современный Clipboard API
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        if (this.$toast) {
                            this.$toast.success('Отчет по задаче скопирован в буфер обмена!')
                        }
                    }).catch(() => {
                        this.showManualCopyPrompt(text)
                    })
                } else {
                    this.showManualCopyPrompt(text)
                }
            } catch (e) {
                this.showManualCopyPrompt(text)
            } finally {
                document.body.removeChild(textArea)
            }
        },

        showManualCopyPrompt(text) {
            // Показываем пользователю текст и просим скопировать вручную
            const shouldCopy = confirm('Не удалось автоматически скопировать текст. Нажмите OK, чтобы увидеть текст для ручного копирования.')
            if (shouldCopy) {
                const textWindow = window.open('', '_blank')
                textWindow.document.write(`
                    <html>
                        <head><title>Текст для копирования</title></head>
                        <body>
                            <textarea style="width: 100%; height: 80vh; margin: 20px 0;">${text}</textarea>
                            <p>Скопируйте текст выше и закройте это окно</p>
                        </body>
                    </html>
                `)
                textWindow.document.close()
            }
        },

        // Генерация отчета для одной задачи (без финального сообщения)
        generateSingleTaskReport(task) {
            const status = task.is_completed ? '✅ ВЫПОЛНЕНО' : '🟡 В РАБОТЕ'
            const priority = this.getPriorityLabel(task.priority)
            const dueDate = task.due_date ? `📅 Срок: ${this.formatDate(task.due_date)}` : ''

            let report = `📋 ОТЧЕТ ПО ЗАДАЧЕ\n`
            report += `Проект: ${this.project.name}\n`
            report += `Дата формирования: ${new Date().toLocaleString('ru-RU')}\n\n`

            report += `ЗАДАЧА: ${task.title}\n`
            report += `Статус: ${status}\n`
            report += `Приоритет: ${priority}\n`
            report += `${dueDate}\n`
            report += `Создана: ${this.formatDate(task.created_at)}\n\n`

            // Подзадачи
            const subTasks = this.getSubTasks(task.id)
            if (subTasks.length > 0) {
                const completedCount = this.getCompletedSubTasksCount(task.id)
                report += `📌 ПОДЗАДАЧИ (${completedCount}/${subTasks.length}):\n`
                subTasks.forEach((subTask, index) => {
                    const subStatus = subTask.is_completed ? '✅' : '⭕'
                    report += `  ${index + 1}. ${subStatus} ${subTask.title}\n`

                    // Комментарии подзадачи
                    const subTaskComments = this.getSubTaskComments(subTask.id)
                    if (subTaskComments.length > 0) {
                        report += `    💬 Комментарии к подзадаче:\n`
                        subTaskComments.forEach(comment => {
                            report += `      └─ ${this.formatDate(comment.created_at)}: ${comment.content}\n`
                        })
                    }
                })
                report += '\n'
            }

            // Комментарии
            const comments = this.getTaskComments(task.id)
            if (comments.length > 0) {
                report += `💬 КОММЕНТАРИИ (${comments.length}):\n`
                comments.forEach(comment => {
                    report += `  └─ ${this.formatDate(comment.created_at)}: ${comment.content}\n`
                })
            }

            return report
        },

        // Генерация отчета по всем задачам
        generateTaskReport() {
            let report = `📊 ОТЧЕТ ПО ЗАДАЧАМ\n`
            report += `Проект: ${this.project.name}\n`
            report += `Дата формирования: ${new Date().toLocaleString('ru-RU')}\n`
            report += `Общий прогресс: ${this.completionRate}% (${this.completedTasks}/${this.totalTasks} задач)\n\n`

            report += `📈 СТАТИСТИКА:\n`
            report += `├─ Всего задач: ${this.totalTasks}\n`
            report += `├─ Выполнено: ${this.completedTasks}\n`
            report += `├─ В работе: ${this.pendingTasks}\n`
            report += `└─ Прогресс: ${this.completionRate}%\n\n`

            report += `📋 ЗАДАЧИ:\n`
            report += '='.repeat(60) + '\n\n'

            this.sortedTasks.forEach((task, index) => {
                const status = task.is_completed ? '✅ ВЫПОЛНЕНО' : '🟡 В РАБОТЕ'
                const priority = this.getPriorityLabel(task.priority)
                const dueDate = task.due_date ? `📅 Срок: ${this.formatDate(task.due_date)}` : ''

                report += `${index + 1}. ${task.title}\n`
                report += `   └─ Статус: ${status} | Приоритет: ${priority} ${dueDate}\n`

                // Подзадачи
                const subTasks = this.getSubTasks(task.id)
                if (subTasks.length > 0) {
                    const completedCount = this.getCompletedSubTasksCount(task.id)
                    report += `      📌 Подзадачи (${completedCount}/${subTasks.length}):\n`
                    subTasks.forEach(subTask => {
                        const subStatus = subTask.is_completed ? '✅' : '⭕'
                        report += `      ${subStatus} ${subTask.title}\n`

                        // Комментарии подзадачи
                        const subTaskComments = this.getSubTaskComments(subTask.id)
                        if (subTaskComments.length > 0) {
                            report += `      💬 Комментарии к подзадаче:\n`
                            subTaskComments.forEach(comment => {
                                report += `        └─ ${this.formatDate(comment.created_at)}: ${comment.content}\n`
                            })
                        }
                    })
                }

                // Комментарии
                const comments = this.getTaskComments(task.id)
                if (comments.length > 0) {
                    report += `      💬 Комментарии:\n`
                    comments.forEach(comment => {
                        report += `      └─ ${this.formatDate(comment.created_at)}: ${comment.content}\n`
                    })
                }

                report += '\n' + '─'.repeat(60) + '\n\n'
            })

            report += `\nСформировано системой учёта времени и задач\n`

            return report
        },

        async exportTaskReport() {
            const reportText = this.generateTaskReport()
            const blob = new Blob([reportText], { type: 'text/plain; charset=utf-8' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${this.project.name.replace(/\s+/g, '_')}_отчет_задач_${new Date().toISOString().split('T')[0]}.txt`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)

            if (this.$toast) {
                this.$toast.success('Отчет по задачам успешно экспортирован!')
            }
        },

        async copyTaskReport() {
            try {
                const reportText = this.generateTaskReport()
                await navigator.clipboard.writeText(reportText)

                if (this.$toast) {
                    this.$toast.success('Отчет по задачам скопирован в буфер обмена!')
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось скопировать отчет')
                }
            }
        },

        formatDate(dateString) {
            if (!dateString) return ''
            return new Date(dateString).toLocaleDateString('ru-RU')
        }
    },
    async mounted() {
        try {
            this.loading = true
            await this.fetchProjects()
            await this.fetchTasks()
            this.project = this.projects.find(p => p.id === this.projectId) || {}

            // Загружаем комментарии и подзадачи для всех задач
            for (const task of this.projectTasks) {
                await this.fetchTaskComments(task.id)
                await this.fetchSubTasks(task.id)

                // Загружаем комментарии для всех подзадач
                const subTasks = this.getSubTasks(task.id)
                for (const subTask of subTasks) {
                    await this.fetchSubTaskComments(subTask.id)
                }
            }

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

/* Новые стили для редактирования названия проекта */
.project-title-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 1rem;
}

.project-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 2.2rem;
    font-weight: 800 !important;
    color: #ffffff !important;
}

.project-title:hover {
    color: #e0e0ff !important;
}

.btn-edit-project {
    background: none;
    border: none;
    font-size: 0.8em;
    cursor: pointer;
    opacity: 0.7;
    transition: opacity 0.3s ease;
    padding: 5px;
    border-radius: 4px;
    color: white;
}

.btn-edit-project:hover {
    opacity: 1;
    background-color: rgba(255, 255, 255, 0.2);
}

.project-name-edit {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: center;
}

.project-name-input {
    padding: 8px 12px;
    border: 2px solid #007bff;
    border-radius: 6px;
    font-size: 1.5rem;
    font-weight: bold;
    text-align: center;
    min-width: 300px;
}

/* Стили для статистики проекта */
.project-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-item {
    text-align: center;
    padding: 0.5rem;
}

.progress-stat {
    grid-column: 1 / -1;
    margin-top: 0.5rem;
}

.stat-number {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    margin-bottom: 0.25rem;
}

.stat-label {
    display: block;
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.8);
}

.progress-bar-mini {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    margin-top: 0.5rem;
    overflow: hidden;
}

.progress-bar-mini .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745, #20c997);
    transition: width 0.3s ease;
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
    font-size: 2.4rem;
    font-weight: bold;
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

.btn-daily {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    color: white;
    font-weight: 600;
}

.btn-daily:hover {
    background: linear-gradient(135deg, #ff5252, #e74c3c);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
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

.task-management-tabs {
    display: flex;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e9ecef;
}

.tab-btn {
    padding: 12px 24px;
    border: none;
    background: none;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
}

.tab-btn.active {
    border-bottom-color: #007bff;
    color: #007bff;
    background-color: #f8f9fa;
}

.tab-btn:hover {
    background-color: #f8f9fa;
}

/* Стили для трекера времени */
.timer-tab {
    animation: fadeIn 0.3s ease;
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

/* Стили для трекера задач */
.tasks-tab {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.task-options {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.priority-select,
.date-input {
    flex: 1;
}

/* Статистика */
.tasks-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
    text-align: center;
}

.stat-item {
    padding: 1rem;
}

.stat-number {
    display: block;
    font-size: 2rem;
    font-weight: bold;
    color: #007bff;
}

.stat-label {
    color: #6c757d;
    font-size: 0.9rem;
}

/* Фильтры задач */
.task-filters {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
}

.filter-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #e9ecef;
    background: white;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
}

.filter-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.filter-btn:hover {
    background: #e9ecef;
}

.filter-btn.active:hover {
    background: #0056b3;
}

/* Стили для задач в трекере задач */
.task-item {
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    border-left: 4px solid #6c757d;
}

.task-item.priority-high {
    border-left-color: #dc3545;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
}

.task-item.priority-medium {
    border-left-color: #ffc107;
    background: linear-gradient(135deg, #fffbf0 0%, #ffffff 100%);
}

.task-item.priority-low {
    border-left-color: #28a745;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
}

.task-item.task-completed {
    opacity: 0.7;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.task-main-info {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    flex: 1;
}

.task-checkbox {
    margin-top: 0.25rem;
    transform: scale(1.2);
}

.task-main-info h4 {
    margin: 0;
    line-height: 1.4;
}

.completed-text {
    text-decoration: line-through;
    color: #6c757d;
}

.task-meta {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-end;
}

.task-priority {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

.priority-1 {
    background: #dc3545;
    color: white;
}

.priority-2 {
    background: #ffc107;
    color: #212529;
}

.priority-3 {
    background: #28a745;
    color: white;
}

.task-due-date {
    font-size: 0.8rem;
    color: #6c757d;
}

/* Прогресс подзадач */
.subtasks-progress {
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.progress-bar {
    flex: 1;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745, #20c997);
    transition: width 0.3s ease;
}

.progress-text {
    font-size: 0.8rem;
    color: #6c757d;
    min-width: 100px;
}

/* Подзадачи */
.subtasks-section {
    margin: 1rem 0;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.subtask-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e9ecef;
    flex-direction: column;
}

.subtask-item:last-child {
    border-bottom: none;
}

.subtask-checkbox {
    transform: scale(1.1);
    margin-top: 0.25rem;
}

.add-subtask {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.subtask-input {
    flex: 1;
}

.delete-subtask {
    margin-left: auto;
    opacity: 0.7;
}

.delete-subtask:hover {
    opacity: 1;
}

/* Комментарии подзадач */
.subtask-comments {
    margin-top: 0.5rem;
    padding-left: 1rem;
    border-left: 2px solid #e9ecef;
    width: 100%;
}

.subtask-comment {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.subtask-comment .comment-content {
    margin-bottom: 0.25rem;
}

.subtask-comment .comment-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: #6c757d;
}

.add-subtask-comment {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.subtask-comment-input {
    flex: 1;
    resize: vertical;
    min-height: 60px;
    font-size: 14px;
}

/* Комментарии */
.comments-section {
    margin: 1rem 0;
}

.comments-list {
    margin-bottom: 1rem;
}

.comment-item {
    padding: 0.75rem;
    background: white;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border-left: 3px solid #007bff;
}

.comment-content {
    margin-bottom: 0.5rem;
    line-height: 1.4;
}

.comment-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: #6c757d;
}

.add-comment {
    display: flex;
    gap: 0.5rem;
}

.comment-input {
    flex: 1;
    resize: vertical;
    min-height: 60px;
}

/* Действия с задачей */
.task-actions {
    display: flex;
    justify-content: flex-end;
    padding-top: 1rem;
    border-top: 1px solid #e9ecef;
}

/* Кнопки экспорта */
.export-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid #e9ecef;
}

.subtask-edit-input {
    flex: 1;
    padding: 4px 8px;
    border: 1px solid #007bff;
    border-radius: 4px;
    font-size: 14px;
}

.subtask-actions {
    display: flex;
    gap: 4px;
    margin-left: auto;
}

.task-header-actions {
    display: flex;
    gap: 8px;
}

/* Адаптивность */
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

    .task-management-tabs {
        flex-direction: column;
    }

    .task-header {
        flex-direction: column;
        gap: 1rem;
    }

    .task-meta {
        align-items: flex-start;
        flex-direction: row;
        flex-wrap: wrap;
    }

    .tasks-stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .export-actions {
        flex-direction: column;
    }

    .task-options {
        flex-direction: column;
    }

    .task-header-actions {
        flex-direction: column;
        gap: 4px;
    }

    .subtask-actions {
        flex-direction: column;
    }

    .project-stats {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }

    .project-name-input {
        min-width: 200px;
        font-size: 1.2rem;
    }

    .project-title-section {
        flex-direction: column;
        gap: 5px;
    }

    .subtask-comments {
        padding-left: 0.5rem;
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

    .tasks-stats {
        grid-template-columns: 1fr;
    }

    .task-filters {
        flex-direction: column;
    }

    .project-stats {
        grid-template-columns: 1fr;
    }

    .project-name-input {
        min-width: 150px;
        font-size: 1.1rem;
    }

    .subtask-item {
        flex-direction: column;
        align-items: flex-start;
    }

    .subtask-actions {
        align-self: flex-end;
    }
}
</style>    