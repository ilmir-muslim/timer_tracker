<template>
    <div class="daily-tasks">
        <!-- Заголовок с градиентом как в проектах -->
        <div class="header-card">
            <div class="header-content">
                <h2>📅 Ежедневные задачи</h2>
                <p>Задачи вне проектов - рутина, привычки, ежедневные дела</p>
            </div>
        </div>

        <div class="task-management-tabs">
            <button @click="activeTab = 'tasks'" :class="['tab-btn', { active: activeTab === 'tasks' }]">
                ✅ Трекер задач
            </button>
        </div>

        <!-- Единый блок всех кнопок отчетов -->
        <div class="all-report-actions card">
            <h3>📊 Все отчеты и действия</h3>

            <div class="report-sections">
                <!-- Недельные отчеты -->
                <div class="report-section">
                    <h4>Недельные отчеты</h4>
                    <div class="report-buttons">
                        <button @click="generateCurrentWeekReport" class="btn btn-weekly">
                            📅 Отчет за текущую неделю
                        </button>
                        <button @click="generatePreviousWeekReport" class="btn btn-weekly">
                            📅 Отчет за прошлую неделю
                        </button>
                        <button @click="transferUncompletedTasksFromPreviousWeek" class="btn btn-transfer">
                            🔄 Перенести не завершенные задачи прошлой недели
                        </button>
                    </div>
                </div>

                <!-- Дейлики -->
                <div class="report-section">
                    <h4>Ежедневные отчеты</h4>
                    <div class="report-buttons">
                        <button @click="generateDailyReport" class="btn btn-daily">
                            📅 Сформировать дейлик
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Остальная часть компонента без изменений -->
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

        <!-- Статистика -->
        <div class="tasks-stats card">
            <div class="stat-item">
                <span class="stat-number">{{ totalTasks }}</span>
                <span class="stat-label">Всего задач</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ completedTasks }}</span>
                <span class="stat-label">Выполнено</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ completionRate }}%</span>
                <span class="stat-label">Прогресс</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ totalSubTasks }}</span>
                <span class="stat-label">Всего подзадач</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ completedSubTasks }}</span>
                <span class="stat-label">Выполнено подзадач</span>
            </div>
        </div>

        <!-- Список задач -->
        <div v-if="sortedTasks.length === 0" class="card empty-state">
            <div class="empty-icon">📝</div>
            <h3>Пока нет ежедневных задач</h3>
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
                            <button @click="deleteSubTaskHandler(task.id, subTask.id)" class="btn btn-sm btn-danger">
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

        <!-- Модальное окно редактирования задачи -->
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
    name: 'DailyTasks',
    data() {
        return {
            activeTab: 'tasks',
            newTaskTitle: '',
            newTaskPriority: 2,
            newTaskDueDate: '',
            newSubTaskTitles: {},
            newCommentContents: {},
            newSubTaskCommentContents: {},
            taskView: 'all',
            editingSubTasks: {},
            editingSubTaskTitles: {},
            editingTaskModal: false,
            editingTaskData: null
        }
    },
    computed: {
        ...mapState(['tasks']),
        ...mapGetters([
            'getTaskComments',
            'getSubTasks',
            'getCompletedSubTasksCount',
            'getTotalSubTasksCount',
            'getSubTaskComments'
        ]),

        // Фильтруем задачи без проекта (project_id = null)
        dailyTasks() {
            return this.tasks.filter(task => task.project_id === null)
        },

        taskTrackerTasks() {
            return this.dailyTasks.filter(task => {
                if (this.taskView === 'active') return !task.is_completed
                if (this.taskView === 'completed') return task.is_completed
                return true
            })
        },

        sortedTasks() {
            return [...this.taskTrackerTasks].sort((a, b) => {
                if (a.is_completed !== b.is_completed) {
                    return a.is_completed ? 1 : -1;
                }
                return new Date(b.created_at) - new Date(a.created_at);
            });
        },

        totalTasks() {
            return this.dailyTasks.length
        },
        completedTasks() {
            return this.dailyTasks.filter(task => task.is_completed).length
        },
        pendingTasks() {
            return this.totalTasks - this.completedTasks
        },
        completionRate() {
            return this.totalTasks > 0 ? Math.round((this.completedTasks / this.totalTasks) * 100) : 0
        },
        totalSubTasks() {
            let total = 0
            this.dailyTasks.forEach(task => {
                total += this.getTotalSubTasksCount(task.id)
            })
            return total
        },
        completedSubTasks() {
            let completed = 0
            this.dailyTasks.forEach(task => {
                completed += this.getCompletedSubTasksCount(task.id)
            })
            return completed
        }
    },
    methods: {
        ...mapActions([
            'fetchTasks',
            'createTask',
            'deleteTask',
            'updateTask',
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

        // Вспомогательные функции для работы с неделями
        getWeekRange(date = new Date()) {
            const start = new Date(date);
            const day = start.getDay();
            const diff = start.getDate() - day + (day === 0 ? -6 : 1); // adjust when day is sunday
            start.setDate(diff);
            start.setHours(0, 0, 0, 0);

            const end = new Date(start);
            end.setDate(start.getDate() + 6);
            end.setHours(23, 59, 59, 999);

            return { start, end };
        },

        getCurrentWeekRange() {
            return this.getWeekRange();
        },

        getPreviousWeekRange() {
            const date = new Date();
            date.setDate(date.getDate() - 7);
            return this.getWeekRange(date);
        },

        // Методы для недельных отчетов
        generateCurrentWeekReport() {
            const weekRange = this.getCurrentWeekRange();
            const report = this.generateWeeklyReport(weekRange, 'ТЕКУЩАЯ НЕДЕЛЯ');
            this.copyToClipboardCustom(report, 'Отчет за текущую неделю скопирован в буфер обмена!');
        },

        generatePreviousWeekReport() {
            const weekRange = this.getPreviousWeekRange();
            const report = this.generateWeeklyReport(weekRange, 'ПРОШЛАЯ НЕДЕЛЯ');
            this.copyToClipboardCustom(report, 'Отчет за прошлую неделю скопирован в буфер обмена!');
        },

        generateWeeklyReport(weekRange, weekType) {
            const tasksInWeek = this.dailyTasks.filter(task => {
                const taskDate = new Date(task.created_at);
                return taskDate >= weekRange.start && taskDate <= weekRange.end;
            });

            const completedTasks = tasksInWeek.filter(task => task.is_completed);
            const pendingTasks = tasksInWeek.filter(task => !task.is_completed);

            let report = `📅 ОТЧЕТ ЗА ${weekType}\n`;
            report += `Период: ${weekRange.start.toLocaleDateString('ru-RU')} - ${weekRange.end.toLocaleDateString('ru-RU')}\n`;
            report += `Сформировано: ${new Date().toLocaleString('ru-RU')}\n\n`;

            report += `📊 СТАТИСТИКА:\n`;
            report += `├─ Всего задач: ${tasksInWeek.length}\n`;
            report += `├─ Выполнено: ${completedTasks.length}\n`;
            report += `├─ В работе: ${pendingTasks.length}\n`;
            report += `└─ Прогресс: ${tasksInWeek.length > 0 ? Math.round((completedTasks.length / tasksInWeek.length) * 100) : 0}%\n\n`;

            // Выполненные задачи
            if (completedTasks.length > 0) {
                report += `✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ:\n`;
                completedTasks.forEach((task, index) => {
                    report += `${index + 1}. ${task.title}\n`;

                    // Подзадачи
                    const subTasks = this.getSubTasks(task.id);
                    if (subTasks.length > 0) {
                        const completedSubTasks = subTasks.filter(st => st.is_completed);
                        report += `   📌 Подзадачи (${completedSubTasks.length}/${subTasks.length}):\n`;
                        subTasks.forEach(subTask => {
                            const status = subTask.is_completed ? '✅' : '⭕';
                            report += `   ${status} ${subTask.title}\n`;
                        });
                    }

                    // Комментарии
                    const comments = this.getTaskComments(task.id);
                    if (comments.length > 0) {
                        report += `   💬 Комментарии:\n`;
                        comments.forEach(comment => {
                            report += `   └─ ${comment.content}\n`;
                        });
                    }
                    report += '\n';
                });
            }

            // Невыполненные задачи
            if (pendingTasks.length > 0) {
                report += `🟡 НЕВЫПОЛНЕННЫЕ ЗАДАЧИ:\n`;
                pendingTasks.forEach((task, index) => {
                    report += `${index + 1}. ${task.title} (${this.getPriorityLabel(task.priority)})\n`;

                    // Подзадачи
                    const subTasks = this.getSubTasks(task.id);
                    if (subTasks.length > 0) {
                        const completedSubTasks = subTasks.filter(st => st.is_completed);
                        report += `   📌 Подзадачи (${completedSubTasks.length}/${subTasks.length}):\n`;
                        subTasks.forEach(subTask => {
                            const status = subTask.is_completed ? '✅' : '⭕';
                            report += `   ${status} ${subTask.title}\n`;
                        });
                    }

                    // Комментарии
                    const comments = this.getTaskComments(task.id);
                    if (comments.length > 0) {
                        report += `   💬 Комментарии:\n`;
                        comments.forEach(comment => {
                            report += `   └─ ${comment.content}\n`;
                        });
                    }
                    report += '\n';
                });
            }

            return report;
        },

        async transferUncompletedTasksFromPreviousWeek() {
            const weekRange = this.getPreviousWeekRange();
            const uncompletedTasks = this.dailyTasks.filter(task => {
                const taskDate = new Date(task.created_at);
                return taskDate >= weekRange.start && taskDate <= weekRange.end && !task.is_completed;
            });

            if (uncompletedTasks.length === 0) {
                if (this.$toast) {
                    this.$toast.info('Нет не завершенных задач за прошлую неделю для переноса.');
                }
                return;
            }

            if (!confirm(`Перенести ${uncompletedTasks.length} не завершенных задач из прошлой недели в текущую с повышением приоритета?`)) {
                return;
            }

            try {
                for (const task of uncompletedTasks) {
                    // Повышаем приоритет (1 -> остается 1, 2 -> 1, 3 -> 2)
                    const newPriority = task.priority === 1 ? 1 : task.priority - 1;

                    await this.updateTask({
                        taskId: task.id,
                        taskData: {
                            priority: newPriority,
                            created_at: new Date().toISOString()
                        }
                    });
                }

                await this.fetchTasks();

                if (this.$toast) {
                    this.$toast.success(`Перенесено ${uncompletedTasks.length} задач с повышением приоритета.`);
                }
            } catch (error) {
                console.error('Ошибка при переносе задач:', error);
                if (this.$toast) {
                    this.$toast.error('Не удалось перенести задачи.');
                }
            }
        },

        async addTask() {
            if (this.newTaskTitle.trim()) {
                try {
                    const taskData = {
                        title: this.newTaskTitle,
                        project_id: null,
                        priority: parseInt(this.newTaskPriority)
                    }

                    if (this.newTaskDueDate) {
                        taskData.due_date = this.formatDateForBackend(this.newTaskDueDate)
                    }

                    await this.createTask(taskData)
                    this.newTaskTitle = ''
                    this.newTaskDueDate = ''
                    this.newTaskPriority = 2

                    if (this.$toast) {
                        this.$toast.success('Ежедневная задача успешно добавлена!')
                    }
                } catch (error) {
                    console.error('Ошибка создания задачи:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось создать задачу')
                    }
                }
            }
        },

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

        // Дейлик для ежедневных задач
        async generateDailyReport() {
            try {
                const today = new Date();
                const yesterday = new Date(today);
                yesterday.setDate(today.getDate() - 1);

                let report = `📅 Дейлик ${this.formatDateForReport(today)}\n`;
                report += `📋 Раздел: Ежедневные задачи\n\n`;

                // СДЕЛАЛ ВЧЕРА
                report += `✅ СДЕЛАЛ ВЧЕРА (${this.formatDateForReport(yesterday)}):\n`;

                let hasYesterdayProgress = false;

                for (const task of this.dailyTasks) {
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
                report += `└─ Общий прогресс: ${this.completionRate}%\n`;

                await this.copyToClipboardCustom(report, 'Дейлик по ежедневным задачам успешно скопирован в буфер обмена!');

            } catch (error) {
                console.error('Ошибка генерации дейлика:', error);
                if (this.$toast) {
                    this.$toast.error('Не удалось сформировать дейлик');
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
                if (this.$toast) {
                    this.$toast.success(successMessage);
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
                if (this.$toast) {
                    this.$toast.success(successMessage);
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

                if (this.$toast) {
                    this.$toast.success('Отчет по задаче скопирован в буфер обмена!')
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

            let report = `📋 ОТЧЕТ ПО ЕЖЕДНЕВНОЙ ЗАДАЧЕ\n`
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
        }
    },
    async mounted() {
        try {
            await this.fetchTasks()

            // Загружаем комментарии и подзадачи для всех ежедневных задач
            for (const task of this.dailyTasks) {
                await this.fetchTaskComments(task.id)
                await this.fetchSubTasks(task.id)

                const subTasks = this.getSubTasks(task.id)
                for (const subTask of subTasks) {
                    await this.fetchSubTaskComments(subTask.id)
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки ежедневных задач:', error)
            if (this.$toast) {
                this.$toast.error('Не удалось загрузить ежедневные задачи')
            }
        }
    }
}
</script>

<style scoped>
.daily-tasks {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 20px;
}

.header-card {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    border-radius: 16px;
    color: white;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    margin-bottom: 2.5rem;
    padding: 2.5rem;
    text-align: center;
}

.header-content h2 {
    font-size: 2.4rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: white;
}

.header-content p {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.3rem;
    margin: 0;
}

/* Новый стиль для единого блока всех отчетов */
.all-report-actions {
    margin-bottom: 2rem;
}

.all-report-actions h3 {
    margin-bottom: 1.5rem;
    color: #343a40;
    text-align: center;
    font-size: 1.5rem;
}

.report-sections {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.report-section {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1.5rem;
    background: #f8f9fa;
}

.report-section h4 {
    margin-bottom: 1rem;
    color: #495057;
    font-size: 1.2rem;
    text-align: center;
}

.report-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

/* Стили кнопок */
.btn-weekly {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    font-weight: 600;
}

.btn-transfer {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    font-weight: 600;
}

.btn-daily {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    color: white;
    font-weight: 600;
}

.btn-weekly:hover,
.btn-transfer:hover,
.btn-daily:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.btn-weekly:hover {
    background: linear-gradient(135deg, #3a9dfc 0%, #00d9e0 100%);
}

.btn-transfer:hover {
    background: linear-gradient(135deg, #ff5252 0%, #e74c3c 100%);
}

.btn-daily:hover {
    background: linear-gradient(135deg, #ff5252, #e74c3c);
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

/* Остальные стили остаются без изменений */
.task-form {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

.full-width-input {
    width: 100%;
}

.task-input {
    min-height: 120px;
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

.task-options {
    display: flex;
    gap: 1rem;
}

.priority-select,
.date-input {
    flex: 1;
}

.add-task-btn {
    padding: 15px 25px;
    font-size: 18px;
    border-radius: 8px;
    align-self: flex-end;
    min-width: 150px;
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

.tasks-list {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}

.task-item {
    transition: all 0.3s ease;
    padding: 1.8rem;
    border-radius: 12px;
    border-left: 4px solid #6c757d;
}

.task-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
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

.subtask-edit-input {
    flex: 1;
    padding: 4px 8px;
    border: 1px solid #007bff;
    border-radius: 4px;
    font-size: 14px;
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

.add-subtask {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.subtask-input {
    flex: 1;
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

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-danger:hover {
    background-color: #c82333;
}

.btn-edit {
    background-color: #ffc107;
    color: #212529;
}

.btn-edit:hover {
    background-color: #e0a800;
}

.btn-sm {
    padding: 8px 12px;
    font-size: 14px;
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

/* Адаптивность */
@media (max-width: 768px) {
    .daily-tasks {
        padding: 0 15px;
    }

    .header-card {
        padding: 1.5rem;
    }

    .header-content h2 {
        font-size: 2rem;
    }

    .report-sections {
        gap: 1rem;
    }

    .report-section {
        padding: 1rem;
    }

    .report-buttons {
        flex-direction: column;
        align-items: center;
    }

    .task-options {
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

    .task-header-actions {
        flex-direction: column;
        gap: 4px;
    }

    .subtask-actions {
        flex-direction: column;
    }

    .subtask-comments {
        padding-left: 0.5rem;
    }
}

@media (max-width: 480px) {
    .header-content h2 {
        font-size: 1.8rem;
    }

    .task-item {
        padding: 1.2rem;
    }

    .task-header h4 {
        font-size: 1.2rem;
    }

    .tasks-stats {
        grid-template-columns: 1fr;
    }

    .task-filters {
        flex-direction: column;
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