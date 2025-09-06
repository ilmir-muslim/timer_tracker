<template>
    <div class="login-container">
        <div class="login-card">
            <h2>Вход в систему</h2>
            <form @submit.prevent="handleLogin">
                <div class="form-group">
                    <input v-model="username" type="text" placeholder="Имя пользователя" required>
                </div>
                <div class="form-group">
                    <input v-model="password" type="password" placeholder="Пароль" required>
                </div>
                <div class="remember-me">
                    <label>
                        <input type="checkbox" v-model="rememberMe">
                        Запомнить меня
                    </label>
                </div>
                <button type="submit" :disabled="loading">Войти</button>
                <p class="register-link">
                    Нет аккаунта? <a href="#" @click.prevent="$router.push('/register')">Зарегистрироваться</a>
                </p>
            </form>
            <p v-if="error" class="error">{{ error }}</p>
        </div>
    </div>
</template>

<script>
import { mapActions } from 'vuex'
import Cookies from 'js-cookie'

export default {
    name: 'UserLogin',
    data() {
        return {
            username: Cookies.get('rememberedUsername') || '',
            password: '',
            rememberMe: !!Cookies.get('rememberedUsername'),
            loading: false,
            error: ''
        }
    },
    methods: {
        ...mapActions(['login']),
        async handleLogin() {
            this.loading = true
            this.error = ''

            try {
                await this.login({
                    username: this.username,
                    password: this.password
                })

                // Сохраняем логин в куки если выбрано "Запомнить меня"
                if (this.rememberMe) {
                    Cookies.set('rememberedUsername', this.username, { expires: 30, path: '/' })
                } else {
                    Cookies.remove('rememberedUsername', { path: '/' })
                }

                this.$router.push('/')
            } catch (error) {
                this.error = 'Неверное имя пользователя или пароль'
            } finally {
                this.loading = false
            }
        }
    }
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    padding: 20px;
}

.login-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

.login-card h2 {
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

.remember-me {
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.remember-me label {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-size: 0.9rem;
    color: #6c757d;
}

.remember-me input {
    margin-right: 8px;
}

button {
    width: 100%;
    padding: 0.75rem;
    background-color: #007bff;
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

.register-link {
    text-align: center;
    margin-top: 1rem;
}

.error {
    color: #dc3545;
    text-align: center;
    margin-top: 1rem;
}
</style>