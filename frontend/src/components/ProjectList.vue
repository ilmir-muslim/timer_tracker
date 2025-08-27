<template>
    <div class="project-list">
        <h2>Projects</h2>
        <div class="project-form">
            <input v-model="newProjectName" placeholder="New project name" />
            <button @click="createProject">Add Project</button>
        </div>
        <div v-for="project in projects" :key="project.id" class="project-item">
            <h3>{{ project.name }}</h3>
            <p>Total time: {{ formatTime(project.total_time) }}</p>
            <button @click="$router.push(`/project/${project.id}`)">View Details</button>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
    name: 'ProjectList',
    data() {
        return {
            newProjectName: ''
        }
    },
    computed: {
        ...mapState(['projects'])
    },
    methods: {
        ...mapActions(['createProject', 'fetchProjects']),
        async createProject() {
            if (this.newProjectName.trim()) {
                await this.$store.dispatch('createProject', { name: this.newProjectName })
                this.newProjectName = ''
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
    mounted() {
        this.fetchProjects()
    }
}
</script>

<style scoped>
.project-list {
    padding: 20px;
}

.project-form {
    margin-bottom: 20px;
}

.project-item {
    border: 1px solid #ddd;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 5px;
}
</style>