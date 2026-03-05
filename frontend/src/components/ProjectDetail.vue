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

                <!-- Блок заработка проекта (живой) -->
                <div class="project-earnings">
                    <!-- Ставка проекта с возможностью редактирования -->
                    <div class="earnings-item" v-if="!editingProjectRate">
                        <span class="label">Ставка:</span>
                        <span class="value" @dblclick="startEditingProjectRate">
                            {{ project.hourly_rate || 0 }} ₽/час
                            <button @click="startEditingProjectRate" class="btn-edit-project">✏️</button>
                        </span>
                    </div>
                    <div class="earnings-item" v-else>
                        <span class="label">Ставка:</span>
                        <div class="rate-edit">
                            <input v-model.number="newProjectRate" type="number" min="0" step="0.01" class="rate-input">
                            <button @click="saveProjectRate" class="btn btn-primary btn-sm">✅</button>
                            <button @click="cancelEditingProjectRate" class="btn btn-secondary btn-sm">❌</button>
                        </div>
                    </div>
                    <div class="earnings-item">
                        <span class="label">Заработано:</span>
                        <span class="value">{{ formatMoney(liveEarnedAmount) }}</span>
                    </div>
                </div>

                <div class="total-time">
                    <span class="label">Общее время проекта:</span>
                    <span class="time">{{ formatTime(totalLiveTime) }}</span>
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

        <!-- Трекер времени (с живым временем) -->
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

            <div v-if="sortedTimerTasks.length === 0" class="card empty-state">
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
                    <div v-for="task in sortedTimerTasks" :key="task.id" class="task-item card"
                        :class="{ 'task-active': task.is_timer_running }">
                        <div class="task-content">
                            <div class="task-header">
                                <h4>{{ task.title }}</h4>
                                <span class="task-time">{{ formatTime(task.live_total_time) }}</span>
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

        <!-- Трекер задач (полный функционал) -->
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
                                <div v-for="comment in getSubTaskComments(subTask.id)" :key="comment.id"
                                    class="subtask-comment">
                                    <div class="comment-content">
                                        {{ comment.content }}
                                    </div>
                                    <div class="comment-meta">
                                        <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                                        <button @click="deleteSubTaskComment(subTask.id, comment.id)"
                                            class="btn btn-sm btn-danger">
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
            loading: true,
            editingTask: null,
            editHours: 0,
            editMinutes: 0,
            editSeconds: 0,
            now: Date.now(), // для живого времени
            activeTab: 'timer',
            newTaskPriority: 2,
            newTaskDueDate: '',
            newSubTaskTitles: {},
            newCommentContents: {},
            newSubTaskCommentContents: {},
            taskView: 'all',
            editingSubTasks: {},
            editingSubTaskTitles: {},
            editingTaskModal: false,
            editingTaskData: null,
            editingProjectName: '',
            isEditingProject: false,
            // Новые поля для редактирования ставки проекта
            editingProjectRate: false,
            newProjectRate: 0,
            timerInterval: null
        }
    },
    computed: {
        ...mapState(['projects', 'tasks']),
        ...mapGetters([
            'getTasksByProjectId',
            'getTaskComments',
            'getSubTasks',
            'getCompletedSubTasksCount',
            'getTotalSubTasksCount',
            'getSubTaskComments'
        ]),
        projectId() {
            return parseInt(this.$route.params.id)
        },
        projectTasks() {
            return this.getTasksByProjectId(this.projectId)
        },
        tasksWithLiveTime() {
            return this.projectTasks.map(task => {
                let total = task.total_time || 0;
                if (task.is_timer_running && task.last_start_time) {
                    const lastStart = this.parseUTCDate(task.last_start_time).getTime();
                    if (!isNaN(lastStart)) {
                        const elapsed = (this.now - lastStart) / 1000;
                        total += elapsed;
                    }
                }
                return { ...task, live_total_time: total };
            });
        },
        sortedTimerTasks() {
            return [...this.tasksWithLiveTime].sort((a, b) =>
                new Date(b.created_at) - new Date(a.created_at)
            );
        },
        taskTrackerTasks() {
            return this.projectTasks.filter(task => {
                if (this.taskView === 'active') return !task.is_completed
                if (this.taskView === 'completed') return task.is_completed
                return true
            })
        },
        sortedTasks() {
            return [...this.taskTrackerTasks].sort((a, b) => {
                if (a.is_completed !== b.is_completed) {
                    return a.is_completed ? 1 : -1
                }
                return new Date(b.created_at) - new Date(a.created_at)
            })
        },
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
        totalTasks() {
            return this.projectTasks.length
        },
        completedTasks() {
            return this.projectTasks.filter(task => task.is_completed).length
        },
        totalLiveTime() {
            return this.tasksWithLiveTime.reduce(
                (total, task) => total + (task.live_total_time || 0),
                0
            );
        },
        liveEarnedAmount() {
            return (this.totalLiveTime * (this.project.hourly_rate || 0)) / 3600;
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
            'fetchSubTaskComments',
            'createSubTaskComment',
            'deleteSubTaskComment'
        ]),

        // Редактирование проекта
        startEditingProjectName() {
            this.editingProjectName = this.project.name
            this.isEditingProject = true
        },
        async saveProjectName() {
            if (this.editingProjectName.trim() && this.editingProjectName !== this.project.name) {
                try {
                    await this.updateProject({
                        projectId: this.projectId,
                        projectData: { name: this.editingProjectName.trim() }
                    })
                    await this.fetchProjects()
                    this.project = this.projects.find(p => p.id === this.projectId) || {}
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Название проекта обновлено!')
                    } else {
                        console.log('Название проекта обновлено!')
                    }
                } catch (error) {
                    console.error('Ошибка обновления проекта:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось обновить название проекта')
                    } else {
                        alert('Не удалось обновить название проекта')
                    }
                }
            }
            this.cancelEditingProjectName()
        },
        cancelEditingProjectName() {
            this.editingProjectName = ''
            this.isEditingProject = false
        },

        // Редактирование ставки проекта
        startEditingProjectRate() {
            this.newProjectRate = this.project.hourly_rate || 0
            this.editingProjectRate = true
        },
        async saveProjectRate() {
            if (this.newProjectRate !== this.project.hourly_rate) {
                try {
                    await this.updateProject({
                        projectId: this.projectId,
                        projectData: { hourly_rate: parseFloat(this.newProjectRate) }
                    })
                    await this.fetchProjects()
                    this.project = this.projects.find(p => p.id === this.projectId) || {}
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Ставка проекта обновлена')
                    } else {
                        console.log('Ставка проекта обновлена')
                    }
                } catch (error) {
                    console.error('Ошибка обновления ставки проекта:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось обновить ставку проекта')
                    } else {
                        alert('Не удалось обновить ставку проекта')
                    }
                }
            }
            this.cancelEditingProjectRate()
        },
        cancelEditingProjectRate() {
            this.editingProjectRate = false
            this.newProjectRate = 0
        },

        async addTask() {
            if (this.newTaskTitle.trim()) {
                try {
                    const taskData = {
                        title: this.newTaskTitle,
                        project_id: this.projectId
                    }
                    if (this.activeTab === 'tasks') {
                        taskData.priority = parseInt(this.newTaskPriority)
                        if (this.newTaskDueDate) {
                            taskData.due_date = this.formatDateForBackend(this.newTaskDueDate)
                        }
                    }
                    await this.createTask(taskData)
                    this.newTaskTitle = ''
                    this.newTaskDueDate = ''
                    this.newTaskPriority = 2
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Задача успешно добавлена!')
                    } else {
                        console.log('Задача успешно добавлена!')
                    }
                } catch (error) {
                    console.error('Ошибка создания задачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось создать задачу')
                    } else {
                        alert('Не удалось создать задачу')
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

        formatMoney(amount) {
            return (amount || 0).toFixed(2) + ' ₽';
        },

        parseUTCDate(dateString) {
            if (!dateString) return new Date(NaN);
            if (dateString.endsWith('Z')) {
                return new Date(dateString);
            }
            return new Date(dateString + 'Z');
        },

        async startTaskTimer(taskId) {
            try {
                await this.startTimer(taskId)
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Таймер запущен')
                } else {
                    console.log('Таймер запущен')
                }
            } catch (error) {
                console.error('Ошибка запуска таймера:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось запустить таймер')
                } else {
                    alert('Не удалось запустить таймер')
                }
            }
        },

        async pauseTaskTimer(taskId) {
            try {
                await this.pauseTimer(taskId)
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.info('Таймер на паузе')
                } else {
                    console.log('Таймер на паузе')
                }
            } catch (error) {
                console.error('Ошибка остановки таймера:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось остановить таймер')
                } else {
                    alert('Не удалось остановить таймер')
                }
            }
        },

        async stopAllTimers() {
            if (this.activeTimersCount === 0) return
            if (confirm(`Остановить все активные таймеры (${this.activeTimersCount})?`)) {
                try {
                    const activeTasks = this.projectTasks.filter(task => task.is_timer_running)
                    for (const task of activeTasks) {
                        await this.pauseTimer(task.id)
                    }
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success(`Остановлено ${this.activeTimersCount} таймеров`)
                    } else {
                        console.log(`Остановлено ${this.activeTimersCount} таймеров`)
                    }
                } catch (error) {
                    console.error('Ошибка остановки таймеров:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось остановить таймеры')
                    } else {
                        alert('Не удалось остановить таймеры')
                    }
                }
            }
        },

        generateReportText() {
            let report = `Проект: ${this.project.name}\n`
            report += `Общее время: ${this.formatTime(this.totalLiveTime)}\n`
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

            // FIXED: проверка this.$toast
            if (this.$toast) {
                this.$toast.success('Отчет успешно экспортирован!')
            } else {
                console.log('Отчет успешно экспортирован!')
            }
        },

        async copyToClipboard() {
            try {
                const reportText = this.generateReportText()
                await navigator.clipboard.writeText(reportText)
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Отчет скопирован в буфер обмена!')
                } else {
                    console.log('Отчет скопирован в буфер обмена!')
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось скопировать в буфер обмена')
                } else {
                    alert('Не удалось скопировать в буфер обмена')
                }
            }
        },

        async deleteProjectHandler() {
            if (confirm('Вы уверены, что хотите удалить проект? Все задачи будут удалены.')) {
                try {
                    await this.deleteProject(this.projectId)
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Проект удален')
                    } else {
                        console.log('Проект удален')
                    }
                    this.$router.push('/')
                } catch (error) {
                    console.error('Ошибка удаления проекта:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить проект')
                    } else {
                        alert('Не удалось удалить проект')
                    }
                }
            }
        },

        async deleteTaskHandler(taskId) {
            if (confirm('Вы уверены, что хотите удалить задачу?')) {
                try {
                    await this.deleteTask(taskId)
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Задача удалена')
                    } else {
                        console.log('Задача удалена')
                    }
                } catch (error) {
                    console.error('Ошибка удаления задачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить задачу')
                    } else {
                        alert('Не удалось удалить задачу')
                    }
                }
            }
        },

        openEditModal(task) {
            this.editingTask = { ...task }
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
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Задача успешно обновлена!')
                } else {
                    console.log('Задача успешно обновлена!')
                }
                this.closeEditModal()
                await this.fetchTasks()
            } catch (error) {
                console.error('Ошибка обновления задачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить задачу')
                } else {
                    alert('Не удалось обновить задачу')
                }
            }
        },

        // Методы для трекера задач
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
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success(isCompleted ? 'Задача выполнена!' : 'Задача возобновлена')
                } else {
                    console.log(isCompleted ? 'Задача выполнена!' : 'Задача возобновлена')
                }
            } catch (error) {
                console.error('Ошибка обновления статуса задачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить статус задачи')
                } else {
                    alert('Не удалось обновить статус задачи')
                }
            }
        },

        async addSubTask(taskId) {
            const title = this.newSubTaskTitles[taskId]?.trim()
            if (!title) return
            try {
                await this.createSubTask({ taskId, title })
                this.newSubTaskTitles[taskId] = ''
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Подзадача добавлена')
                } else {
                    console.log('Подзадача добавлена')
                }
            } catch (error) {
                console.error('Ошибка создания подзадачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось добавить подзадачу')
                } else {
                    alert('Не удалось добавить подзадачу')
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
                } else {
                    alert('Не удалось обновить подзадачу')
                }
            }
        },

        async deleteSubTaskHandler(taskId, subTaskId) {
            if (confirm('Удалить подзадачу?')) {
                try {
                    await this.deleteSubTask({ taskId, subTaskId })
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Подзадача удалена')
                    } else {
                        console.log('Подзадача удалена')
                    }
                } catch (error) {
                    console.error('Ошибка удаления подзадачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить подзадачу')
                    } else {
                        alert('Не удалось удалить подзадачу')
                    }
                }
            }
        },

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
                const newEditingSubTasks = { ...this.editingSubTasks }
                delete newEditingSubTasks[subTaskId]
                this.editingSubTasks = newEditingSubTasks
                const newEditingSubTaskTitles = { ...this.editingSubTaskTitles }
                delete newEditingSubTaskTitles[subTaskId]
                this.editingSubTaskTitles = newEditingSubTaskTitles
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Подзадача обновлена')
                } else {
                    console.log('Подзадача обновлена')
                }
            } catch (error) {
                console.error('Ошибка обновления подзадачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить подзадачу')
                } else {
                    alert('Не удалось обновить подзадачу')
                }
            }
        },

        cancelSubTaskEdit(subTaskId) {
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
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Комментарий добавлен')
                } else {
                    console.log('Комментарий добавлен')
                }
            } catch (error) {
                console.error('Ошибка создания комментария:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось добавить комментарий')
                } else {
                    alert('Не удалось добавить комментарий')
                }
            }
        },

        async deleteComment(taskId, commentId) {
            if (confirm('Удалить комментарий?')) {
                try {
                    await this.deleteTaskComment({ taskId, commentId })
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Комментарий удален')
                    } else {
                        console.log('Комментарий удален')
                    }
                } catch (error) {
                    console.error('Ошибка удаления комментария:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить комментарий')
                    } else {
                        alert('Не удалось удалить комментарий')
                    }
                }
            }
        },

        async addSubTaskComment(subTaskId) {
            const content = this.newSubTaskCommentContents[subTaskId]?.trim();
            if (!content) return;
            try {
                await this.createSubTaskComment({ subTaskId, content });
                this.newSubTaskCommentContents[subTaskId] = '';
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Комментарий к подзадаче добавлен');
                } else {
                    console.log('Комментарий к подзадаче добавлен');
                }
            } catch (error) {
                console.error('Ошибка создания комментария подзадачи:', error);
                if (this.$toast) {
                    this.$toast.error('Не удалось добавить комментарий к подзадаче');
                } else {
                    alert('Не удалось добавить комментарий к подзадаче');
                }
            }
        },

        async deleteSubTaskComment(subTaskId, commentId) {
            if (confirm('Удалить комментарий к подзадаче?')) {
                try {
                    await this.deleteSubTaskComment({ subTaskId, commentId });
                    // FIXED: проверка this.$toast
                    if (this.$toast) {
                        this.$toast.success('Комментарий к подзадаче удален');
                    } else {
                        console.log('Комментарий к подзадаче удален');
                    }
                } catch (error) {
                    console.error('Ошибка удаления комментария подзадачи:', error);
                    if (this.$toast) {
                        this.$toast.error('Не удалось удалить комментарий к подзадаче');
                    } else {
                        alert('Не удалось удалить комментарий к подзадаче');
                    }
                }
            }
        },

        getSubTasksProgress(taskId) {
            const total = this.getTotalSubTasksCount(taskId)
            const completed = this.getCompletedSubTasksCount(taskId)
            return total > 0 ? Math.round((completed / total) * 100) : 0
        },

        openEditTaskModal(task) {
            this.editingTaskData = {
                ...task,
                priority: task.priority || 2,
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
                    taskData.due_date = null
                }
                await this.updateTask({
                    taskId: this.editingTaskData.id,
                    taskData
                })
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Задача успешно обновлена!')
                } else {
                    console.log('Задача успешно обновлена!')
                }
                this.closeEditTaskModal()
                await this.fetchTasks()
            } catch (error) {
                console.error('Ошибка обновления задачи:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось обновить задачу')
                } else {
                    alert('Не удалось обновить задачу')
                }
            }
        },

        formatDateForInput(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            const localDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
            return localDate.toISOString().split('T')[0]
        },

        formatDateForBackend(dateString) {
            if (!dateString) return null
            const date = new Date(dateString)
            return date.toISOString()
        },

        formatDate(dateString) {
            if (!dateString) return ''
            return new Date(dateString).toLocaleDateString('ru-RU')
        },

        async generateDailyReport() {
            try {
                const today = new Date();
                const yesterday = new Date(today);
                yesterday.setDate(today.getDate() - 1);

                let report = `📅 Дейлик ${this.formatDateForReport(today)}\n`;
                report += `📋 Проект: ${this.project.name}\n\n`;

                // СДЕЛАЛ ВЧЕРА
                report += `✅ СДЕЛАЛ ВЧЕРА (${this.formatDateForReport(yesterday)}):\n`;

                let hasYesterdayProgress = false;

                for (const task of this.projectTasks) {
                    const subTasks = this.getSubTasks(task.id);
                    let hasTaskProgress = false;
                    let taskReport = '';

                    const completedSubTasksYesterday = subTasks.filter(subTask =>
                        subTask.completed_at &&
                        new Date(subTask.completed_at).toDateString() === yesterday.toDateString()
                    );

                    if (completedSubTasksYesterday.length > 0) {
                        hasYesterdayProgress = true;
                        hasTaskProgress = true;
                        taskReport += `- ${task.title}\n`;

                        completedSubTasksYesterday.forEach(subTask => {
                            taskReport += `  └─ ✅ ${subTask.title}\n`;

                            const subTaskComments = this.getSubTaskComments(subTask.id);
                            if (subTaskComments.length > 0) {
                                taskReport += `    💬 Комментарии к подзадаче:\n`;
                                subTaskComments.forEach(comment => {
                                    taskReport += `      └─ ${comment.content}\n`;
                                });
                            }
                        });

                        const taskComments = this.getTaskComments(task.id);
                        if (taskComments.length > 0) {
                            taskReport += `  💬 Комментарии к задаче:\n`;
                            taskComments.forEach(comment => {
                                taskReport += `    └─ ${comment.content}\n`;
                            });
                        }

                        taskReport += '\n';
                    }

                    if (task.completed_at && new Date(task.completed_at).toDateString() === yesterday.toDateString()) {
                        hasYesterdayProgress = true;
                        if (!hasTaskProgress) {
                            taskReport += `- ${task.title}\n`;

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

                // ДЕЛАЮ СЕГОДНЯ
                report += `\n🎯 ДЕЛАЮ СЕГОДНЯ (${this.formatDateForReport(today)}):\n`;

                const todayTasks = this.sortedTasks.filter(task =>
                    !task.is_completed &&
                    (task.priority === 1 || (task.due_date && this.isDueToday(task.due_date)))
                ).slice(0, 5);

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

                        const taskComments = this.getTaskComments(task.id);
                        if (taskComments.length > 0) {
                            report += `  💬 Комментарии к задаче:\n`;
                            taskComments.forEach(comment => {
                                report += `    └─ ${comment.content}\n`;
                            });
                        }

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
                } else {
                    alert('Не удалось сформировать дейлик');
                }
            }
        },

        formatDateForReport(date) {
            return date.toLocaleDateString('ru-RU', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        isDueToday(dueDate) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const due = new Date(dueDate);
            due.setHours(0, 0, 0, 0);
            return due.getTime() === today.getTime();
        },

        async copyToClipboardCustom(text, successMessage) {
            try {
                await navigator.clipboard.writeText(text);
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success(successMessage);
                } else {
                    console.log(successMessage);
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error);
                this.showCopyFallbackWithMessage(text, successMessage);
            }
        },

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
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success(successMessage);
                } else {
                    console.log(successMessage);
                }
            } catch (e) {
                this.showManualCopyPrompt(text);
            } finally {
                document.body.removeChild(textArea);
            }
        },

        showManualCopyPrompt(text) {
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

        async copySingleTaskToClipboard(task) {
            try {
                const reportText = this.generateSingleTaskReport(task)
                await navigator.clipboard.writeText(reportText)
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Отчет по задаче скопирован в буфер обмена!')
                } else {
                    console.log('Отчет по задаче скопирован в буфер обмена!')
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error)
                this.showCopyFallback(this.generateSingleTaskReport(task))
            }
        },

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

            const subTasks = this.getSubTasks(task.id)
            if (subTasks.length > 0) {
                const completedCount = this.getCompletedSubTasksCount(task.id)
                report += `📌 ПОДЗАДАЧИ (${completedCount}/${subTasks.length}):\n`
                subTasks.forEach((subTask, index) => {
                    const subStatus = subTask.is_completed ? '✅' : '⭕'
                    report += `  ${index + 1}. ${subStatus} ${subTask.title}\n`

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

            const comments = this.getTaskComments(task.id)
            if (comments.length > 0) {
                report += `💬 КОММЕНТАРИИ (${comments.length}):\n`
                comments.forEach(comment => {
                    report += `  └─ ${this.formatDate(comment.created_at)}: ${comment.content}\n`
                })
            }

            return report
        },

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

                const subTasks = this.getSubTasks(task.id)
                if (subTasks.length > 0) {
                    const completedCount = this.getCompletedSubTasksCount(task.id)
                    report += `      📌 Подзадачи (${completedCount}/${subTasks.length}):\n`
                    subTasks.forEach(subTask => {
                        const subStatus = subTask.is_completed ? '✅' : '⭕'
                        report += `      ${subStatus} ${subTask.title}\n`

                        const subTaskComments = this.getSubTaskComments(subTask.id)
                        if (subTaskComments.length > 0) {
                            report += `      💬 Комментарии к подзадаче:\n`
                            subTaskComments.forEach(comment => {
                                report += `        └─ ${this.formatDate(comment.created_at)}: ${comment.content}\n`
                            })
                        }
                    })
                }

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

            // FIXED: проверка this.$toast
            if (this.$toast) {
                this.$toast.success('Отчет по задачам успешно экспортирован!')
            } else {
                console.log('Отчет по задачам успешно экспортирован!')
            }
        },

        async copyTaskReport() {
            try {
                const reportText = this.generateTaskReport()
                await navigator.clipboard.writeText(reportText)
                // FIXED: проверка this.$toast
                if (this.$toast) {
                    this.$toast.success('Отчет по задачам скопирован в буфер обмена!')
                } else {
                    console.log('Отчет по задачам скопирован в буфер обмена!')
                }
            } catch (error) {
                console.error('Ошибка копирования в буфер:', error)
                if (this.$toast) {
                    this.$toast.error('Не удалось скопировать отчет')
                } else {
                    alert('Не удалось скопировать отчет')
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

            for (const task of this.projectTasks) {
                await this.fetchTaskComments(task.id)
                await this.fetchSubTasks(task.id)
                const subTasks = this.getSubTasks(task.id)
                for (const subTask of subTasks) {
                    await this.fetchSubTaskComments(subTask.id)
                }
            }

            // Запускаем интервал для живого времени
            this.timerInterval = setInterval(() => {
                this.now = Date.now();
            }, 1000);

        } catch (error) {
            console.error('Ошибка загрузки деталей проекта:', error)
            if (this.$toast) {
                this.$toast.error('Не удалось загрузить детали проекта')
            } else {
                alert('Не удалось загрузить детали проекта')
            }
        } finally {
            this.loading = false
        }
    },
    beforeUnmount() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
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

/* Блок заработка проекта */
.project-earnings {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 1rem 0;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}

.earnings-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.earnings-item .label {
    font-size: 1rem;
    opacity: 0.9;
    margin-bottom: 0.3rem;
}

.earnings-item .value {
    font-size: 1.6rem;
    font-weight: bold;
    color: #ffd700;
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

.task-header-actions {
    display: flex;
    gap: 8px;
}

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

.subtask-actions {
    display: flex;
    gap: 4px;
    margin-left: auto;
}

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

.task-actions {
    display: flex;
    justify-content: flex-end;
    padding-top: 1rem;
    border-top: 1px solid #e9ecef;
}

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

    .project-earnings {
        flex-direction: column;
        gap: 1rem;
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