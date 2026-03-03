<template>
    <div class="earnings-summary card">
        <h3>💰 Заработок</h3>
        <div class="stat-item">
            <span class="stat-label">Всего заработано:</span>
            <span class="stat-value">{{ formatMoney(totalEarned) }}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Средний в месяц:</span>
            <span class="stat-value">{{ formatMoney(averageMonthly) }}</span>
        </div>
        <div class="stat-item" v-if="months > 0">
            <span class="stat-label">Месяцев:</span>
            <span class="stat-value">{{ months }}</span>
        </div>
    </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
    name: 'EarningsSummary',
    computed: {
        ...mapState({
            summary: state => state.earningsSummary
        }),
        totalEarned() {
            return this.summary?.total_earned || 0;
        },
        averageMonthly() {
            return this.summary?.average_monthly || 0;
        },
        months() {
            return this.summary?.months_since_registration || 0;
        }
    },
    methods: {
        formatMoney(amount) {
            return amount.toFixed(2) + ' ₽';
        }
    }
}
</script>

<style scoped>
.earnings-summary {
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    margin: 0.75rem 0;
    font-size: 1.1rem;
}

.stat-label {
    color: #6c757d;
}

.stat-value {
    font-weight: bold;
    color: #28a745;
}
</style>