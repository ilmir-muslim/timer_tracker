<template>
    <div class="daily-stats card">
        <h3>📊 Статистика работы</h3>

        <!-- Сегодня (используем актуальное значение из dailySession) -->
        <div class="stat-section">
            <h4>Сегодня</h4>
            <div class="stat-big">
                <span class="stat-value">{{ formatTime(currentDailySeconds) }}</span>
            </div>
        </div>

        <!-- Неделя -->
        <div class="stat-section">
            <h4>Последние 7 дней</h4>
            <div class="week-summary">
                <span class="stat-value">{{ formatTime(weekTotal) }}</span>
                <span class="stat-label">всего</span>
            </div>
            <div class="mini-chart">
                <div v-for="(day, idx) in weekData" :key="idx" class="chart-bar"
                    :style="{ height: getBarHeight(day.total_seconds) + 'px' }"
                    :title="day.date + ': ' + formatTime(day.total_seconds)">
                </div>
            </div>
            <div class="week-days">
                <span v-for="(day, idx) in weekData" :key="idx" class="day-label">
                    {{ shortDay(day.date) }}
                </span>
            </div>
        </div>

        <!-- Месяц -->
        <div class="stat-section">
            <h4>Последние 30 дней</h4>
            <div class="month-summary">
                <span class="stat-value">{{ formatTime(monthTotal) }}</span>
                <span class="stat-label">всего</span>
            </div>
            <div class="mini-chart month-chart">
                <div v-for="(day, idx) in monthData" :key="idx" class="chart-bar"
                    :style="{ height: getBarHeight(day.total_seconds, 40) + 'px' }"
                    :title="day.date + ': ' + formatTime(day.total_seconds)">
                </div>
            </div>
        </div>

        <div v-if="loading" class="loading">Загрузка...</div>
    </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
    name: 'DailyStats',
    data() {
        return {
            loading: false
        }
    },
    computed: {
        ...mapState({
            stats: state => state.dailyStats
        }),
        ...mapGetters(['currentDailySeconds']), // добавляем геттер
        weekData() {
            return this.stats?.week || []
        },
        weekTotal() {
            return this.weekData.reduce((sum, d) => sum + d.total_seconds, 0)
        },
        monthData() {
            return this.stats?.month || []
        },
        monthTotal() {
            return this.monthData.reduce((sum, d) => sum + d.total_seconds, 0)
        },
        maxWeek() {
            const max = Math.max(...this.weekData.map(d => d.total_seconds), 1)
            return max
        }
    },
    methods: {
        ...mapActions(['fetchDailyStats']),
        formatTime(seconds) {
            if (!seconds) return '0ч 0м 0с'
            const hours = Math.floor(seconds / 3600)
            const minutes = Math.floor((seconds % 3600) / 60)
            const secs = Math.floor(seconds % 60)
            return hours > 0 ? `${hours}ч ${minutes}м ${secs}с` : `${minutes}м ${secs}с`
        },
        getBarHeight(seconds, maxHeight = 50) {
            const max = this.maxWeek
            return max > 0 ? (seconds / max) * maxHeight : 2
        },
        shortDay(dateStr) {
            const d = new Date(dateStr)
            return d.toLocaleDateString('ru-RU', { weekday: 'short' }).slice(0, 2)
        }
    },
    async mounted() {
        this.loading = true
        try {
            await this.fetchDailyStats(30)
        } catch (e) {
            console.error(e)
        } finally {
            this.loading = false
        }
    }
}
</script>

<style scoped>
.daily-stats {
    padding: 1.5rem;
}

.daily-stats h3 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #343a40;
    text-align: center;
}

.stat-section {
    margin-bottom: 2rem;
    border-bottom: 1px solid #e9ecef;
    padding-bottom: 1.5rem;
}

.stat-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.stat-section h4 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1.1rem;
}

.stat-big {
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #28a745;
    font-family: monospace;
}

.stat-label {
    color: #6c757d;
    margin-left: 0.5rem;
}

.week-summary,
.month-summary {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1rem;
}

.mini-chart {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 60px;
    gap: 2px;
    margin: 0.5rem 0;
}

.month-chart {
    height: 50px;
}

.chart-bar {
    flex: 1;
    background: linear-gradient(to top, #28a745, #20c997);
    border-radius: 3px 3px 0 0;
    min-height: 3px;
    transition: height 0.2s;
}

.week-days {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
    font-size: 0.7rem;
    color: #6c757d;
}

.day-label {
    flex: 1;
    text-align: center;
}

.loading {
    text-align: center;
    color: #6c757d;
    padding: 1rem;
}
</style>