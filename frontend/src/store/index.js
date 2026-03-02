import { createStore } from 'vuex'
import axios from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'

export default createStore({
    state: {
        token: localStorage.getItem('token') || Cookies.get('token') || '',
        user: null,
        projects: [],
        tasks: [],
        timeEntries: [],
        taskComments: {},
        subTasks: {},
        subTaskComments: {},
        // Новые состояния для daily сессии и статистики
        dailySession: null,
        dailyStats: null
    },
    mutations: {
        SET_TOKEN(state, token) {
            state.token = token
            localStorage.setItem('token', token)
            Cookies.set('token', token, { expires: 30, path: '/' })
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        },
        CLEAR_TOKEN(state) {
            state.token = ''
            localStorage.removeItem('token')
            Cookies.remove('token', { path: '/' })
            delete axios.defaults.headers.common['Authorization']
        },
        SET_USER(state, user) {
            state.user = user
        },
        SET_PROJECTS(state, projects) {
            state.projects = projects
        },
        SET_TASKS(state, tasks) {
            state.tasks = tasks
        },
        SET_TIME_ENTRIES(state, timeEntries) {
            state.timeEntries = timeEntries
        },
        ADD_PROJECT(state, project) {
            state.projects.push(project)
        },
        ADD_TASK(state, task) {
            state.tasks.push(task)
        },
        UPDATE_TASK(state, updatedTask) {
            const index = state.tasks.findIndex(t => t.id === updatedTask.id)
            if (index !== -1) {
                state.tasks.splice(index, 1, updatedTask)
            }
        },
        UPDATE_PROJECT(state, updatedProject) {
            const index = state.projects.findIndex(p => p.id === updatedProject.id)
            if (index !== -1) {
                state.projects.splice(index, 1, updatedProject)
            }
        },
        SET_TASK_COMMENTS(state, { taskId, comments }) {
            state.taskComments[taskId] = comments
        },
        ADD_TASK_COMMENT(state, { taskId, comment }) {
            if (!state.taskComments[taskId]) {
                state.taskComments[taskId] = []
            }
            state.taskComments[taskId].push(comment)
        },
        REMOVE_TASK_COMMENT(state, { taskId, commentId }) {
            if (state.taskComments[taskId]) {
                state.taskComments[taskId] = state.taskComments[taskId].filter(
                    comment => comment.id !== commentId
                )
            }
        },
        SET_SUB_TASKS(state, { taskId, subTasks }) {
            state.subTasks[taskId] = subTasks
        },
        ADD_SUB_TASK(state, { taskId, subTask }) {
            if (!state.subTasks[taskId]) {
                state.subTasks[taskId] = []
            }
            state.subTasks[taskId].push(subTask)
        },
        UPDATE_SUB_TASK(state, { taskId, subTask }) {
            if (state.subTasks[taskId]) {
                const index = state.subTasks[taskId].findIndex(st => st.id === subTask.id)
                if (index !== -1) {
                    state.subTasks[taskId].splice(index, 1, subTask)
                }
            }
        },
        REMOVE_SUB_TASK(state, { taskId, subTaskId }) {
            if (state.subTasks[taskId]) {
                state.subTasks[taskId] = state.subTasks[taskId].filter(
                    subTask => subTask.id !== subTaskId
                )
            }
        },
        UPDATE_TASK_STATUS(state, { taskId, isCompleted }) {
            const task = state.tasks.find(t => t.id === taskId)
            if (task) {
                task.is_completed = isCompleted
                task.completed_at = isCompleted ? new Date().toISOString() : null
            }
        },
        SET_SUB_TASK_COMMENTS(state, { subTaskId, comments }) {
            state.subTaskComments[subTaskId] = comments;
        },
        ADD_SUB_TASK_COMMENT(state, { subTaskId, comment }) {
            if (!state.subTaskComments[subTaskId]) {
                state.subTaskComments[subTaskId] = [];
            }
            state.subTaskComments[subTaskId].push(comment);
        },
        REMOVE_SUB_TASK_COMMENT(state, { subTaskId, commentId }) {
            if (state.subTaskComments[subTaskId]) {
                state.subTaskComments[subTaskId] = state.subTaskComments[subTaskId].filter(
                    comment => comment.id !== commentId
                );
            }
        },
        // Мутации для daily сессии
        SET_DAILY_SESSION(state, session) {
            state.dailySession = session
        },
        SET_DAILY_STATS(state, stats) {
            state.dailyStats = stats
        }
    },
    actions: {
        async login({ commit }, credentials) {
            try {
                const response = await axios.post(`${API_BASE_URL}/login`, credentials)
                commit('SET_TOKEN', response.data.access_token)
                return response.data
            } catch (error) {
                console.error('Ошибка входа:', error)
                throw error
            }
        },
        async register(_, userData) {
            try {
                const response = await axios.post(`${API_BASE_URL}/register`, userData)
                return response.data
            } catch (error) {
                console.error('Ошибка регистрации:', error)
                throw error
            }
        },
        async logout({ commit }) {
            commit('CLEAR_TOKEN')
            commit('SET_USER', null)
            commit('SET_DAILY_SESSION', null)
            commit('SET_DAILY_STATS', null)
        },
        async fetchProjects({ commit }) {
            try {
                const response = await axios.get(`${API_BASE_URL}/projects/`)
                commit('SET_PROJECTS', response.data)
            } catch (error) {
                console.error('Ошибка загрузки проектов:', error)
                throw error
            }
        },
        async createProject({ commit }, projectData) {
            try {
                const response = await axios.post(`${API_BASE_URL}/projects/`, projectData)
                commit('ADD_PROJECT', response.data)
                return response.data
            } catch (error) {
                console.error('Ошибка создания проекта:', error)
                throw error
            }
        },
        async fetchTasks({ commit }) {
            try {
                console.log('Загрузка задач из:', `${API_BASE_URL}/tasks-with-details/`)
                const response = await axios.get(`${API_BASE_URL}/tasks-with-details/`)
                console.log('Ответ задач:', response.data)
                commit('SET_TASKS', response.data)
            } catch (error) {
                console.error('Ошибка загрузки задач:', error)
                throw error
            }
        },
        async createTask({ commit }, taskData) {
            try {
                const response = await axios.post(`${API_BASE_URL}/tasks/`, taskData)
                commit('ADD_TASK', response.data)
                return response.data
            } catch (error) {
                console.error('Ошибка создания задачи:', error)
                throw error
            }
        },
        async startTimer({ commit, dispatch }, taskId) {
            try {
                const response = await axios.post(`${API_BASE_URL}/timer/start/${taskId}`)
                await dispatch('fetchTasks')
                if (response.data.daily_session) {
                    commit('SET_DAILY_SESSION', response.data.daily_session)
                }
                await dispatch('fetchDailyStats', 30)
            } catch (error) {
                console.error('Error starting timer:', error)
                throw error
            }
        },
        async pauseTimer({ commit, dispatch }, taskId) {
            try {
                const response = await axios.post(`${API_BASE_URL}/timer/pause/${taskId}`)
                await dispatch('fetchTasks')
                if (response.data.daily_session) {
                    commit('SET_DAILY_SESSION', response.data.daily_session)
                }
                await dispatch('fetchDailyStats', 30)
            } catch (error) {
                console.error('Error pausing timer:', error)
                throw error
            }
        },
        async deleteProject({ commit }, projectId) {
            try {
                await axios.delete(`${API_BASE_URL}/projects/${projectId}`)
                commit('SET_PROJECTS', this.state.projects.filter(p => p.id !== projectId))
            } catch (error) {
                console.error('Ошибка удаления проекта:', error)
                throw error
            }
        },
        async deleteTask({ commit }, taskId) {
            try {
                await axios.delete(`${API_BASE_URL}/tasks/${taskId}`)
                commit('SET_TASKS', this.state.tasks.filter(t => t.id !== taskId))
            } catch (error) {
                console.error('Ошибка удаления задачи:', error)
                throw error
            }
        },
        async updateTask({ commit }, { taskId, taskData }) {
            try {
                const response = await axios.put(`${API_BASE_URL}/tasks/${taskId}`, taskData)
                commit('UPDATE_TASK', response.data)
                return response.data
            } catch (error) {
                console.error('Ошибка обновления задачи:', error)
                throw error
            }
        },
        async updateProject({ commit }, { projectId, projectData }) {
            try {
                const response = await axios.put(`${API_BASE_URL}/projects/${projectId}`, projectData)
                commit('UPDATE_PROJECT', response.data)
                return response.data
            } catch (error) {
                console.error('Ошибка обновления проекта:', error)
                throw error
            }
        },
        async fetchTaskComments({ commit }, taskId) {
            try {
                const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}/comments`)
                commit('SET_TASK_COMMENTS', { taskId, comments: response.data })
            } catch (error) {
                console.error('Ошибка загрузки комментариев:', error)
                throw error
            }
        },
        async createTaskComment({ commit }, { taskId, content }) {
            try {
                const response = await axios.post(`${API_BASE_URL}/tasks/${taskId}/comments`, { content })
                commit('ADD_TASK_COMMENT', { taskId, comment: response.data })
                return response.data
            } catch (error) {
                console.error('Ошибка создания комментария:', error)
                throw error
            }
        },
        async deleteTaskComment({ commit }, { taskId, commentId }) {
            try {
                await axios.delete(`${API_BASE_URL}/comments/${commentId}`)
                commit('REMOVE_TASK_COMMENT', { taskId, commentId })
            } catch (error) {
                console.error('Ошибка удаления комментария:', error)
                throw error
            }
        },
        async fetchSubTasks({ commit }, taskId) {
            try {
                const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}/subtasks`)
                commit('SET_SUB_TASKS', { taskId, subTasks: response.data })
            } catch (error) {
                console.error('Ошибка загрузки подзадач:', error)
                throw error
            }
        },
        async createSubTask({ commit }, { taskId, title }) {
            try {
                const response = await axios.post(`${API_BASE_URL}/tasks/${taskId}/subtasks`, { title })
                commit('ADD_SUB_TASK', { taskId, subTask: response.data })
                return response.data
            } catch (error) {
                console.error('Ошибка создания подзадачи:', error)
                throw error
            }
        },
        async updateSubTask({ commit }, { taskId, subTaskId, subTaskData }) {
            try {
                const response = await axios.put(`${API_BASE_URL}/subtasks/${subTaskId}`, subTaskData)
                commit('UPDATE_SUB_TASK', { taskId, subTask: response.data })
                return response.data
            } catch (error) {
                console.error('Ошибка обновления подзадачи:', error)
                throw error
            }
        },
        async deleteSubTask({ commit }, { taskId, subTaskId }) {
            try {
                await axios.delete(`${API_BASE_URL}/subtasks/${subTaskId}`)
                commit('REMOVE_SUB_TASK', { taskId, subTaskId })
            } catch (error) {
                console.error('Ошибка удаления подзадачи:', error)
                throw error
            }
        },
        async updateTaskStatus({ commit }, { taskId, isCompleted }) {
            try {
                const response = await axios.put(`${API_BASE_URL}/tasks/${taskId}`, {
                    is_completed: isCompleted
                })
                commit('UPDATE_TASK_STATUS', { taskId, isCompleted })
                return response.data
            } catch (error) {
                console.error('Ошибка обновления статуса задачи:', error)
                throw error
            }
        },
        async fetchSubTaskComments({ commit }, subTaskId) {
            try {
                const response = await axios.get(`${API_BASE_URL}/subtasks/${subTaskId}/comments`)
                commit('SET_SUB_TASK_COMMENTS', { subTaskId, comments: response.data })
            } catch (error) {
                console.error('Ошибка загрузки комментариев подзадачи:', error)
                throw error
            }
        },
        async createSubTaskComment({ commit }, { subTaskId, content }) {
            try {
                const response = await axios.post(`${API_BASE_URL}/subtasks/${subTaskId}/comments`, { content })
                commit('ADD_SUB_TASK_COMMENT', { subTaskId, comment: response.data })
                return response.data
            } catch (error) {
                console.error('Ошибка создания комментария подзадачи:', error)
                throw error
            }
        },
        async deleteSubTaskComment({ commit }, { subTaskId, commentId }) {
            try {
                await axios.delete(`${API_BASE_URL}/subtask-comments/${commentId}`)
                commit('REMOVE_SUB_TASK_COMMENT', { subTaskId, commentId })
            } catch (error) {
                console.error('Ошибка удаления комментария подзадачи:', error)
                throw error
            }
        },
        // Daily session actions
        async fetchCurrentDailySession({ commit }) {
            try {
                const response = await axios.get(`${API_BASE_URL}/daily/current`)
                commit('SET_DAILY_SESSION', response.data)
            } catch (error) {
                console.error('Ошибка загрузки daily сессии:', error)
            }
        },
        async fetchDailyStats({ commit }, days = 30) {
            try {
                const response = await axios.get(`${API_BASE_URL}/daily/stats?days=${days}`)
                commit('SET_DAILY_STATS', response.data)
            } catch (error) {
                console.error('Ошибка загрузки статистики:', error)
            }
        }
    },
    getters: {
        isAuthenticated: state => !!state.token,
        getTasksByProjectId: (state) => (projectId) => {
            return state.tasks.filter(task => task.project_id === projectId)
        },
        getActiveTimer: (state) => (taskId) => {
            const task = state.tasks.find(t => t.id === taskId)
            return task ? task.is_timer_running : false
        },
        getTaskComments: (state) => (taskId) => {
            return state.taskComments[taskId] || []
        },
        getSubTasks: (state) => (taskId) => {
            return state.subTasks[taskId] || []
        },
        getCompletedSubTasksCount: (state) => (taskId) => {
            const subTasks = state.subTasks[taskId] || []
            return subTasks.filter(st => st.is_completed).length
        },
        getTotalSubTasksCount: (state) => (taskId) => {
            return (state.subTasks[taskId] || []).length
        },
        getSubTaskComments: (state) => (subTaskId) => {
            return state.subTaskComments[subTaskId] || []
        },
        // Daily getters
        currentDailySeconds: (state) => {
            return state.dailySession?.total_time || 0
        },
        isDailyTimerRunning: (state) => {
            return state.dailySession?.is_timer_running || false
        }
    }
})