<template>
    <div class="project-list">
        <!-- Обернули заголовок в карточку с градиентным фоном как в ProjectDetail -->
        <div class="header-card">
            <div class="header-content">
                <h2>Мои проекты</h2>
                <p>Создавайте и управляйте своими проектами</p>
            </div>
        </div>

        <div class="card">
            <h3>Создать новый проект</h3>
            <div class="project-form">
                <div class="input-wrapper">
                    <input v-model="newProjectName" placeholder="Введите название проекта"
                        class="form-control project-input" @keyup.enter="createProject">
                </div>
                <button @click="createProject" class="btn btn-primary add-project-btn"
                    :disabled="!newProjectName.trim()">
                    <span class="btn-icon">+</span> Добавить проект
                </button>
            </div>
        </div>


        <div v-if="projects.length === 0" class="card empty-state">
            <div class="empty-icon">📁</div>
            <h3>Пока нет проектов</h3>
            <p>Создайте первый проект чтобы начать</p>
        </div>

        <div v-else>
            <div class="projects-grid">
                <div v-for="project in projects" :key="project.id" class="project-card card"
                    @click="$router.push(`/project/${project.id}`)">
                    <div class="project-header">
                        <h3>{{ project.name }}</h3>
                        <span class="project-time">{{ formatTime(project.total_time) }}</span>
                    </div>
                    <p class="project-created">Создан: {{ formatDate(project.created_at) }}</p>
                </div>
            </div>
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
                try {
                    await this.$store.dispatch('createProject', { name: this.newProjectName })
                    this.newProjectName = ''

                    if (this.$toast) {
                        this.$toast.success('Проект успешно создан!')
                    } else {
                        console.log('Проект успешно создан!')
                    }
                } catch (error) {
                    console.error('Ошибка при создании проекта:', error)
                    if (this.$toast) {
                        this.$toast.error('Не удалось создать проект')
                    } else {
                        console.error('Не удалось создать проект')
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
        formatDate(dateString) {
            if (!dateString) return 'Неизвестная дата'
            const date = new Date(dateString)
            return date.toLocaleDateString('ru-RU')
        }
    },
    async mounted() {
        try {
            await this.fetchProjects()
        } catch (error) {
            console.error('Ошибка загрузки проектов:', error)
            if (this.$toast) {
                this.$toast.error('Не удалось загрузить проекты')
            } else {
                console.error('Не удалось загрузить проекты')
            }
        }
    }
}
</script>

<style scoped>
.project-list {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 15px;
}

/* Новые стили для заголовка с градиентным фоном */
.header-card {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
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

/* Выравнивание формы */
.project-form {
    display: flex;
    gap: 1rem;
    align-items: center;
    /* Изменили на center для вертикального выравнивания */
}

.input-wrapper {
    flex: 1;
}

.project-input {
    padding: 15px;
    font-size: 20px;
    border-radius: 8px;
    border: 2px solid #e9ecef;
    transition: border-color 0.2s;
    height: 60px;
    width: 100%;
    box-sizing: border-box;
}

/* Сделали кнопку темнее и выровняли */
.add-project-btn {
    background-color: #0056b3;
    /* Более темный синий */
    border-color: #004999;
    padding: 15px 25px;
    font-size: 20px;
    border-radius: 8px;
    white-space: nowrap;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    color: white;
    font-weight: 600;
}

.add-project-btn:hover:not(:disabled) {
    background-color: #004999;
    border-color: #003d82;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.add-project-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.btn-icon {
    margin-right: 8px;
    font-weight: bold;
    font-size: 20px;
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
    .project-form {
        flex-direction: column;
        align-items: stretch;
        gap: 1.2rem;
    }

    .add-project-btn {
        width: 100%;
    }
}

/* Остальные стили без изменений */
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
    font-size: 1.3rem;
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.8rem;
}

.project-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
    padding: 1.8rem;
    border-radius: 12px;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    background-color: #f8f9fa;
}

.project-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.2rem;
}

.project-header h3 {
    margin: 0;
    color: #343a40;
    font-size: 1.6rem;
    font-weight: 500;
    flex: 1;
    margin-right: 1rem;
}

.project-time {
    background-color: #e9ecef;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    color: #495057;
    font-size: 1.2rem;
    white-space: nowrap;
}

.project-created {
    color: #6c757d;
    margin-bottom: 0;
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .projects-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .project-header {
        flex-direction: column;
        gap: 0.8rem;
    }

    .project-header h3 {
        margin-right: 0;
    }

    .header-content h2 {
        font-size: 2rem;
    }
}
</style>