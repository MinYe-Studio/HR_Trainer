<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()
const data = ref(null)
const examStatus = ref({})
const loading = ref(true)
const error = ref('')

const levelBadge = { focus: 'red', consolidate: 'gold', express: 'black' }
const levelText = { focus: '重点学习', consolidate: '巩固提升', express: '快速通道' }

onMounted(async () => {
  try {
    const [tasks, st] = await Promise.all([
      client.get('/placement/tasks'),
      client.get('/stats').catch(() => null),
    ])
    data.value = tasks
    const map = {}
    ;(st?.exams?.module_status || []).forEach((m) => {
      map[m.code] = m
    })
    examStatus.value = map
  } catch (e) {
    error.value = e.response?.data?.detail || '任务加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="tasks">
    <div class="head">
      <h1>教学任务</h1>
      <span class="head-bar red"></span>
    </div>
    <p class="tip">根据你的摸底测试成绩生成的个性化学习任务，按优先级排序。</p>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <!-- 未参加测试 -->
    <template v-if="data && !data.has_placement">
      <div class="card cta-card">
        <h2>你还没有参加入营能力摸底测试</h2>
        <p>完成摸底测试后，系统将根据你的成绩生成个性化教学任务。</p>
        <button class="btn primary" @click="router.push('/placement')">
          <span>去参加摸底测试</span>
        </button>
      </div>
    </template>

    <!-- 任务清单 -->
    <template v-if="data && data.has_placement">
      <div class="list">
        <div v-for="t in data.tasks" :key="t.module_id" class="card task">
          <div class="order" :class="levelBadge[t.level]">{{ t.order }}</div>
          <div class="task-body">
            <div class="task-head">
              <h3>{{ t.name }}</h3>
              <span class="badge" :class="levelBadge[t.level]">{{ t.level_label }}</span>
            </div>
            <p class="action">{{ t.recommended_action }}</p>
            <div class="task-foot">
              <span class="score">摸底 {{ t.score }} 分</span>
              <span v-if="examStatus[t.code]" class="badge" :class="examStatus[t.code].exam_passed ? 'black' : examStatus[t.code].exam_taken ? 'red' : 'gold'">
                {{ examStatus[t.code].exam_passed ? '考核已通过 ✓' : examStatus[t.code].exam_taken ? `考核未通过 ${examStatus[t.code].exam_score}分` : '未考核' }}
              </span>
              <button class="btn mini" @click="router.push(`/modules/${t.code}`)">
                <span>进入模块</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.head { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.tasks h1 { margin: 0; }
.head-bar { display: inline-block; width: 46px; height: 8px; border: 4px solid var(--sov-black); }
.head-bar.red { background: var(--sov-red); }
.tip { margin: 0 0 24px; color: var(--sov-brown); font-weight: 700; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.cta-card { padding: 30px; text-align: center; }
.cta-card h2 { margin: 0 0 10px; }
.cta-card p { margin: 0 0 22px; color: var(--sov-brown); font-weight: 700; }

.list { display: flex; flex-direction: column; gap: 16px; }
.task { display: flex; gap: 18px; padding: 18px; align-items: stretch; }
.order {
  display: flex; align-items: center; justify-content: center;
  width: 44px; flex-shrink: 0;
  font-size: 22px; font-weight: 900;
  color: var(--sov-paper);
  border: 4px solid var(--sov-black);
}
.order.red { background: var(--sov-red); }
.order.gold { background: var(--sov-gold); color: var(--sov-black); }
.order.black { background: var(--sov-black); }
.task-body { flex: 1; display: flex; flex-direction: column; }
.task-head { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.task-head h3 { margin: 0; font-size: 17px; }
.action { margin: 0 0 12px; color: var(--sov-brown); font-size: 13.5px; font-weight: 700; }
.task-foot { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: auto; }
.score { font-size: 12px; font-weight: 900; color: var(--sov-black); background: var(--sov-paper); border: 2px solid var(--sov-black); padding: 4px 10px; }
.btn.mini { padding: 6px 16px; font-size: 12.5px; box-shadow: var(--shadow-sm); }
</style>
