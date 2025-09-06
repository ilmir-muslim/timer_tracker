import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import axios from 'axios'

const app = createApp(App)

// Автоматическая установка токена при наличии
if (store.state.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${store.state.token}`
}

// Добавляем перехватчик для ошибок авторизации
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            store.commit('CLEAR_TOKEN')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

app.use(store)
app.use(router)
app.use(Toast, {
    transition: "Vue-Toastification__bounce",
    maxToasts: 20,
    newestOnTop: true
})

app.mount('#app')