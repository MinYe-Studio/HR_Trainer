<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()
const result = ref(null)
const loading = ref(true)
const error = ref('')

const levelBadge = { focus: 'red', consolidate: 'gold', express: 'black' }
const levelText = { focus: '重点学习', consolidate: '巩固提升', express: '快速通道' }

onMounted(async () => {
  try {
    result.value = await client.get('/placement/latest')
  } catch (e) {
    error.value = e.response?.data?.detail || '结果加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="result">
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <template v-if="result">
      <div class="card total-card">
        <div class="total">
          <span class="total-label">摸底总分</span>
          <span class="total-score">{{ result.total_score }}</span>
          <span class="total-unit">分</span>
        </div>
        <div class="total-actions">
          <button class="btn primary" @click="router.push('/tasks')">
            <span>查看教学任务</span>
          </button>
          <button class="btn" @click="router.push('/placement/test')">
            <span>重新测试</span>
          </button>
        </div>
      </div>

      <h2 class="sec-title">各模块得分</h2>
      <div class="grid">
        <div v-for="m in result.module_scores" :key="m.module_id" class="card mcard">
          <div class="mhead">
            <h3>{{ m.name }}</h3>
            <span class="badge" :class="levelBadge[m.level]">{{ levelText[m.level] }}</span>
          </div>
          <div class="score-row">
            <span class="score">{{ m.score }}</span>
            <span class="score-detail">正确 {{ m.correct }}/{{ m.total }}</span>
          </div>
          <div class="bar">
            <div class="bar-fill" :class="levelBadge[m.level]" :style="{ width: m.score + '%' }"></div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.total-card {
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
  padding: 30px; margin-bottom: 26px; flex-wrap: wrap;
}
.total { display: flex; align-items: baseline; gap: 8px; }
.total-label {
  font-size: 14px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .1em;
  color: var(--sov-brown);
  margin-right: 8px;
}
.total-score { font-size: 64px; font-weight: 900; line-height: 1; color: var(--sov-red); }
.total-unit { font-size: 18px; font-weight: 900; }
.total-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.sec-title { margin: 0 0 16px; font-size: 18px; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; }
.mcard { padding: 20px; }
.mhead { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 14px; }
.mhead h3 { margin: 0; font-size: 16px; }
.score-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.score { font-size: 34px; font-weight: 900; }
.score-detail { font-size: 12px; font-weight: 700; color: var(--sov-brown); }
.bar { height: 14px; border: 3px solid var(--sov-black); background: var(--sov-white); }
.bar-fill { height: 100%; transition: width 300ms linear; }
.bar-fill.red { background: var(--sov-red); }
.bar-fill.gold { background: var(--sov-gold); }
.bar-fill.black { background: var(--sov-black); }
</style>
