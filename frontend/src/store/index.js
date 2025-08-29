import { createStore } from 'vuex'
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'

export default createStore({
    state: {
        projects: [],
        tasks: [],
        timeEntries: []
    },
    mutations: {
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
        }
    },
    actions: {
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
                console.log('Загрузка задач из:', `${API_BASE_URL}/tasks/`)
                const response = await axios.get(`${API_BASE_URL}/tasks/`)
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

        async startTimer({ dispatch }, taskId) {
            try {
                await axios.post(`${API_BASE_URL}/timer/start/${taskId}`)
                await dispatch('fetchTasks') // Refresh tasks to get updated timer status
            } catch (error) {
                console.error('Error starting timer:', error)
                throw error
            }
        },
        async pauseTimer({ dispatch }, taskId) {
            try {
                await axios.post(`${API_BASE_URL}/timer/pause/${taskId}`)
                await dispatch('fetchTasks')
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
        }
    },
    getters: {
        getTasksByProjectId: (state) => (projectId) => {
            return state.tasks.filter(task => task.project_id === projectId)
        },
        getActiveTimer: (state) => (taskId) => {
            const task = state.tasks.find(t => t.id === taskId)
            return task ? task.is_timer_running : false
        }
    }
})