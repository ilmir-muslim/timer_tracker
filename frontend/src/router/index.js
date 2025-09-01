import { createRouter, createWebHistory } from 'vue-router'
import ProjectList from '../components/ProjectList.vue'
import ProjectDetail from '../components/ProjectDetail.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import store from '../store'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: ProjectList,
        meta: { requiresAuth: true }
    },
    {
        path: '/project/:id',
        name: 'ProjectDetail',
        component: ProjectDetail,
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// Навигационный guard для проверки аутентификации
router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!store.getters.isAuthenticated) {
            next('/login')
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router