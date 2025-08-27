<template>
    <div class="project-detail">
        <h2>{{ project.name }}</h2>
        <p>Total time: {{ formatTime(project.total_time) }}</p>

        <div class="task-form">
            <input v-model="newTaskTitle" placeholder="New task title" />
            <button @click="createTask">Add Task</button>
        </div>

        <div v-for="task in tasks" :key="task.id" class="task-item">
            <h3>{{ task.title }}</h3>
            <p>Time spent: {{ formatTime(task.total_time) }}</p>
            <div class="timer-controls">
                <button v-if="!task.is_timer_running" @click="startTimer(task.id)" class="start-btn">
                    Start
                </button>
                <button v-else @click="pauseTimer(task.id)" class="pause-btn">
                    Pause
                </button>
                <button @click="stopTimer(task.id)" class="stop-btn">
                    Stop
                </button>
            </div>
        </div>

        <button @click="$router.push('/')">Back to Projects</button>
    </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'

export default {
    name: 'ProjectDetail',
    data() {
        return {
            newTaskTitle: '',
            project: {}
        }
    },
    computed: {
        ...mapState(['projects', 'tasks']),
        ...mapGetters(['getTasksByProjectId']),
        projectId() {
            return parseInt(this.$route.params.id)
        },
        tasks() {
            return this.getTasksByProjectId(this.projectId)
        }
    },
    methods: {
        ...mapActions(['createTask', 'fetchProjects', 'fetchTasks', 'startTimer', 'pauseTimer', 'stopTimer']),
        async createTask() {
            if (this.newTaskTitle.trim()) {
                await this.$store.dispatch('createTask', {
                    title: this.newTaskTitle,
                    project_id: this.projectId
                })
                this.newTaskTitle = ''
            }
        },
        formatTime(seconds) {
            if (!seconds) return '0:00:00'
            const hours = Math.floor(seconds / 3600)
            const minutes = Math.floor((seconds % 3600) / 60)
            const secs = Math.floor(seconds % 60)
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        }
    },
    async mounted() {
        await this.fetchProjects()
        await this.fetchTasks()

        // Find the current project
        this.project = this.projects.find(p => p.id === this.projectId) || {}
    }
}
</script>

<style scoped>
.project-detail {
    padding: 20px;
}

.task-form {
    margin: 20px 0;
}

.task-item {
    border: 1px solid #ddd;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 5px;
}

.timer-controls {
    margin-top: 10px;
}

.start-btn {
    background-color: #4CAF50;
    color: white;
}

.pause-btn {
    background-color: #FFC107;
    color: black;
}

.stop-btn {
    background-color: #F44336;
    color: white;
}

button {
    margin-right: 5px;
    padding: 5px 10px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}
</style>