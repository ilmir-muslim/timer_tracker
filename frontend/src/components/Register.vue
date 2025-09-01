<template>
    <div class="register-container">
        <div class="register-card">
            <h2>Регистрация</h2>
            <form @submit.prevent="handleRegister">
                <div class="form-group">
                    <input v-model="username" type="text" placeholder="Имя пользователя" required>
                </div>
                <div class="form-group">
                    <input v-model="password" type="password" placeholder="Пароль" required>
                </div>
                <div class="form-group">
                    <input v-model="confirmPassword" type="password" placeholder="Подтвердите пароль" required>
                </div>
                <button type="submit" :disabled="loading">Зарегистрироваться</button>
                <p class="login-link">
                    Уже есть аккаунт? <a href="#" @click.prevent="$router.push('/login')">Войти</a>
                </p>
            </form>
            <p v-if="error" class="error">{{ error }}</p>
        </div>
    </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
    name: 'UserRegister',
    data() {
        return {
            username: '',
            password: '',
            confirmPassword: '',
            loading: false,
            error: ''
        }
    },
    methods: {
        ...mapActions(['register', 'login']), // Добавляем действие login
        async handleRegister() {
            if (this.password !== this.confirmPassword) {
                this.error = 'Пароли не совпадают'
                return
            }

            this.loading = true
            this.error = ''

            try {
                // Сначала регистрируем пользователя
                await this.register({
                    username: this.username,
                    password: this.password
                })

                // Затем автоматически выполняем вход
                await this.login({
                    username: this.username,
                    password: this.password
                })

                // Перенаправляем на главную страницу
                this.$router.push('/')
            } catch (error) {
                this.error = 'Не удалось создать аккаунт. Возможно, имя пользователя уже занято.'
            } finally {
                this.loading = false
            }
        }
    }
}
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    padding: 20px;
}

.register-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

.register-card h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #343a40;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
}

button {
    width: 100%;
    padding: 0.75rem;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
}

button:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
}

.login-link {
    text-align: center;
    margin-top: 1rem;
}

.error {
    color: #dc3545;
    text-align: center;
    margin-top: 1rem;
}
</style>