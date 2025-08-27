import { createStore } from 'vuex'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export default createStore({
    state: {
        project: [],
        tasks: [],
        timeEntries: []
    },
    mutations: {
        SET_PROJECTS(state, projects) {
            state.project = projects
        },
        SET_TASKS(state, tasks) {
            state.tasks = tasks
        },
        SET_TIME_ENTRIES(state, timeEntries) {
            state.timeEntries = timeEntries
        },
        ADD_PROJECT(state, project) {
            state.project.push(project)
        },
        ADD_TASK(state, tasks) {
            state.tasks.push(tasks)
        }
    },
    actions: {
        async fetchProjects({ commit }) {
            try {
                const response = await axios.get(`${API_BASE_URL}/projects/`)
                commit('SET_PROJECTS', response.data)
            } catch (error) {
                console.error('Error fetching projects:', error)
            }
        },
        async createProject({ commit }, projectData) {
            try {
                const response = await axios.post(`${API_BASE_URL}/projects/`, projectData)
                commit('ADD_PROJECT', response.data)
                return response.data
            } catch (error) {
                console.error('Error creating project:', error)
                throw error
            }
        },
        async fetchTasks({ commit }) {
            try {
                const response = await axios.get(`${API_BASE_URL}/tasks/`)
                commit('SET_TASKS', response.data)
            } catch (error) {
                console.error('Error fetching tasks:', error)
            }
        },
        async createTask({ commit }, taskData) {
            try {
                const response = await axios.post(`${API_BASE_URL}/tasks/`, taskData)
                commit('ADD_TASK', response.data)
                return response.data
            } catch (error) {
                console.error('Error creating task:', error)
                throw error
            }
        },
        async startTimer({ dispatch }, taskId) {
            try {
                await axios.post(`${API_BASE_URL}/timer/start/${taskId}`)
                dispatch('fetchTasks') // Refresh tasks to get updated timer status
            } catch (error) {
                console.error('Error starting timer:', error)
                throw error
            }
        },
        async pauseTimer({ dispatch }, timeEntryId) {
            try {
                await axios.post(`${API_BASE_URL}/timer/pause/${timeEntryId}`)
                dispatch('fetchTasks') // Refresh tasks to get updated timer status
            } catch (error) {
                console.error('Error pausing timer:', error)
                throw error
            }
        },
        async stopTimer({ dispatch }, timeEntryId) {
            try {
                await axios.post(`${API_BASE_URL}/timer/stop/${timeEntryId}`)
                dispatch('fetchTasks') // Refresh tasks to get updated timer status
            } catch (error) {
                console.error('Error stopping timer:', error)
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