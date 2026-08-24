<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const router = useRouter()
const code = route.params.code
const recordId = route.params.id

const result = ref(null)
const records = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [res, recs] = await Promise.all([
      client.get(`/exam/result/${recordId}`),
      client.get(`/exam/records?module_code=${code}`),
    ])
    result.value = res
    records.value = recs
  } catch (e) {
    error.value = e.response?.data?.detail || '成绩加载失败'
  } finally {
    loading.value = false
  }
})

// 分数-时间曲线（手写 SVG 折线图）
const W = 560
const H = 200
const PAD = 30

const curvePoints = computed(() => {
  const recs = records.value
  if (recs.length < 2) return null
  const scores = recs.map((r) => r.score)
  const max = Math.max(100, ...scores)
  const min = Math.min(0, ...scores)
  const n = recs.length
  return {
    points: recs.map((r, i) => {
      const x = PAD + (i * (W - PAD * 2)) / Math.max(1, n - 1)
      const y = H - PAD - ((r.score - min) / Math.max(1, max - min)) * (H - PAD * 2)
      return { x, y, score: r.score, time: String(r.submitted_at).slice(5, 16).replace('T', ' ') }
    }),
    max,
    min,
  }
})

const fmtDuration = (s) => {
  if (!s) return '--'
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}分${sec}秒`
}
</script>

<template>
  <div class="result">
    <div class="crumbs">
      <RouterLink :to="`/modules/${code}`" class="back">← 返回模块</RouterLink>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <template v-if="result">
      <!-- 成绩横幅 -->
      <div class="card result-bar" :class="result.passed ? 'pass' : 'fail'">
        <div class="result-score">
          <span class="big">{{ result.score }}</span>
          <span class="unit">分</span>
        </div>
        <div class="result-info">
          <span class="badge" :class="result.passed ? 'black' : 'red'">
            {{ result.passed ? '考核通过' : '未通过' }}
          </span>
          <p class="stat">通过线 {{ result.pass_score }} 分 | 本次耗时 {{ fmtDuration(result.duration_seconds) }}</p>
          <p v-if="result.chapter_auto_completed" class="auto-note">✓ 考核通过，本章节已自动标记完成</p>
        </div>
        <div class="result-actions">
          <button class="btn primary" @click="router.push(`/modules/${code}/exam`)">
            <span>重新考核</span>
          </button>
          <RouterLink :to="`/modules/${code}`" class="btn"><span>返回模块</span></RouterLink>
        </div>
      </div>

      <!-- 分数-时间曲线 -->
      <div v-if="curvePoints" class="card curve-card">
        <h2 class="sec-title">分数-时间曲线</h2>
        <div class="curve-wrap">
          <svg :viewBox="`0 0 ${W} ${H}`" class="curve-svg">
            <line v-for="i in 5" :key="i" :x1="PAD" :x2="W - PAD" :y1="PAD + (i - 1) * ((H - PAD * 2) / 4)" :y2="PAD + (i - 1) * ((H - PAD * 2) / 4)" class="grid-line" />
            <polyline
              :points="curvePoints.points.map((p) => `${p.x},${p.y}`).join(' ')"
              class="curve-line"
            />
            <circle
              v-for="(p, i) in curvePoints.points"
              :key="i"
              :cx="p.x" :cy="p.y" r="4"
              :class="p.score >= 60 ? 'dot-pass' : 'dot-fail'"
            />
            <text
              v-for="(p, i) in curvePoints.points"
              :key="'t' + i"
              :x="p.x" :y="p.y - 10"
              class="curve-label"
              text-anchor="middle"
            >{{ p.score }}</text>
          </svg>
          <div class="curve-axis">
            <span v-for="(p, i) in curvePoints.points" :key="'a' + i" class="axis-label">{{ p.time }}</span>
          </div>
        </div>
      </div>

      <!-- 逐题反馈 -->
      <h2 class="sec-title">答题反馈</h2>
      <div class="feedback">
        <div
          v-for="(d, i) in result.details"
          :key="d.question_id"
          class="card fb-item"
          :class="d.correct ? 'right' : 'wrong'"
        >
          <div class="fb-head">
            <span class="fb-mark">{{ d.correct ? '✓' : '✗' }}</span>
            <p class="fb-stem">
              <span v-if="d.category === 'exam_case'" class="fb-case-tag">案例</span>
              {{ i + 1 }}. {{ d.stem }}
            </p>
          </div>
          <div class="fb-answers">
            <p v-if="d.correct" class="fb-line good">回答正确</p>
            <p v-else class="fb-line bad">
              你的答案：{{ d.user_answer.length ? d.user_answer.join('、') : '（未作答）' }}
            </p>
            <p v-if="!d.correct" class="fb-line">正确答案：<b>{{ d.correct_answer.join('、') }}</b></p>
          </div>
          <p class="fb-exp">💡 {{ d.explanation }}</p>
          <div class="fb-kp">
            <span>📚 涉及章节：《{{ d.chapter_title || '模块综合' }}》 · 知识点：{{ d.knowledge_point || '模块综合' }}</span>
            <RouterLink v-if="d.chapter_id" :to="`/modules/${code}/chapters/${d.chapter_id}`" class="btn mini">
              <span>查看讲解</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.crumbs { margin-bottom: 14px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.result-bar { display: flex; align-items: center; gap: 20px; padding: 22px 24px; margin-bottom: 20px; flex-wrap: wrap; }
.result-bar.pass { border-top: 8px solid var(--sov-green-dark, #00a074); }
.result-bar.fail { border-top: 8px solid var(--sov-red); }
.result-score { display: flex; align-items: baseline; gap: 4px; }
.result-score .big { font-size: 56px; font-weight: 900; line-height: 1; }
.result-info { flex: 1; min-width: 200px; }
.result-info .stat { margin: 6px 0 0; color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.auto-note {
  display: inline-block; margin: 8px 0 0;
  background: var(--sov-green-dark, #00a074); color: var(--sov-paper);
  font-size: 12.5px; font-weight: 900; border: 3px solid var(--sov-black);
  padding: 4px 12px;
}
.result-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.curve-card { padding: 22px; margin-bottom: 20px; }
.sec-title { margin: 0 0 14px; font-size: 17px; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; }
.curve-wrap { overflow-x: auto; }
.curve-svg { width: 100%; min-width: 400px; max-width: 640px; display: block; margin: 0 auto; }
.grid-line { stroke: var(--sov-border, #d9e1e8); stroke-width: 1.5; stroke-dasharray: 4 4; }
.curve-line { fill: none; stroke: var(--sov-red); stroke-width: 3.5; }
.dot-pass { fill: var(--sov-green-dark, #00a074); stroke: var(--sov-black); stroke-width: 1.5; }
.dot-fail { fill: var(--sov-red); stroke: var(--sov-black); stroke-width: 1.5; }
.curve-label { font-size: 11px; font-weight: 900; fill: var(--sov-black); }
.curve-axis { display: flex; justify-content: space-between; max-width: 640px; margin: 0 auto; padding: 0 24px; }
.axis-label { font-size: 10px; font-weight: 700; color: var(--sov-brown); }

.feedback { display: flex; flex-direction: column; gap: 14px; }
.fb-item { padding: 18px 20px; }
.fb-item.right { border-left: 10px solid var(--sov-green-dark, #00a074); }
.fb-item.wrong { border-left: 10px solid var(--sov-red); }
.fb-head { display: flex; gap: 10px; align-items: flex-start; }
.fb-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; flex-shrink: 0;
  background: var(--sov-black); color: var(--sov-paper); font-weight: 900;
}
.fb-item.right .fb-mark { background: var(--sov-green-dark, #00a074); }
.fb-item.wrong .fb-mark { background: var(--sov-red); }
.fb-stem { margin: 0; font-weight: 900; font-size: 14.5px; }
.fb-case-tag {
  display: inline-block; margin-right: 6px;
  background: var(--sov-red); color: var(--sov-paper);
  font-size: 11px; font-weight: 900; padding: 1px 8px;
  border: 2px solid var(--sov-black); vertical-align: 1px;
}
.fb-answers { margin: 10px 0 0; padding-left: 36px; }
.fb-line { margin: 2px 0; font-size: 13.5px; font-weight: 700; }
.fb-line.good { color: var(--sov-green-dark, #00a074); }
.fb-line.bad { color: var(--sov-red); }
.fb-exp {
  margin: 10px 0 0; padding: 10px 12px;
  background: var(--sov-paper); border: 2px solid var(--sov-black);
  font-size: 13px; font-weight: 700;
}
.fb-kp {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  margin: 10px 0 0;
  font-size: 12.5px; font-weight: 900;
  color: var(--sov-ink-2, #55677a);
  background: var(--sov-surface-2, #fafbfc);
  border: 2px solid var(--sov-border, #d9e1e8);
  padding: 8px 12px;
  flex-wrap: wrap;
}
.fb-kp .btn.mini { padding: 4px 12px; font-size: 12px; box-shadow: var(--shadow-sm); }
</style>
