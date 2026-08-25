<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import client from '../../api/client'

const code = ref('')
const recordId = ref(0)
const result = ref(null)
const records = ref([])
const loading = ref(true)
const error = ref('')

onLoad(async (options) => {
  code.value = options.code || ''
  recordId.value = Number(options.id) || 0
  try {
    const [res, recs] = await Promise.all([
      client.get(`/exam/result/${recordId.value}`),
      client.get(`/exam/records?module_code=${code.value}`),
    ])
    result.value = res
    records.value = recs
  } catch (e) {
    error.value = e.response?.data?.detail || '成绩加载失败'
  } finally {
    loading.value = false
  }
})

// 分数-时间曲线：用 CSS 柱状图呈现（小程序不支持内联 SVG）
const bars = computed(() => {
  const recs = records.value
  if (recs.length < 1) return []
  const max = Math.max(100, ...recs.map((r) => r.score))
  return recs.map((r) => ({
    score: r.score,
    passed: r.passed,
    time: String(r.submitted_at).slice(5, 16).replace('T', ' '),
    height: Math.max(8, Math.round((r.score / max) * 100)),
  }))
})

const fmtDuration = (s) => {
  if (!s) return '--'
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}分${sec}秒`
}

function goRetest() {
  uni.redirectTo({ url: `/pages/modules/exam?code=${code.value}` })
}
function goModule() {
  // 考核页由模块详情 navigateTo 进入，交卷后 redirectTo 结果页：
  // 返回一层即回到模块详情
  uni.navigateBack({ delta: 1 })
}
function goChapter(chId) {
  uni.navigateTo({ url: `/pages/modules/chapter?code=${code.value}&id=${chId}` })
}
</script>

<template>
  <view class="result">
    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <template v-if="result">
      <!-- 成绩横幅 -->
      <view class="card result-bar" :class="result.passed ? 'pass' : 'fail'">
        <view class="result-score">
          <text class="big">{{ result.score }}</text>
          <text class="unit">分</text>
        </view>
        <view class="result-info">
          <text class="badge" :class="result.passed ? 'black' : 'red'">
            {{ result.passed ? '考核通过' : '未通过' }}
          </text>
          <text class="stat">通过线 {{ result.pass_score }} 分 | 本次耗时 {{ fmtDuration(result.duration_seconds) }}</text>
          <text v-if="result.chapter_auto_completed" class="auto-note">✓ 考核通过，本章节已自动标记完成</text>
        </view>
        <view class="result-actions">
          <view class="btn primary" @click="goRetest"><text>重新考核</text></view>
          <view class="btn" @click="goModule"><text>返回模块</text></view>
        </view>
      </view>

      <!-- 分数-时间曲线（柱状图） -->
      <view v-if="bars.length >= 2" class="card curve-card">
        <text class="sec-title">分数-时间曲线</text>
        <view class="chart">
          <view v-for="(b, i) in bars" :key="i" class="col">
            <text class="col-score">{{ b.score }}</text>
            <view class="col-track">
              <view class="col-fill" :class="b.passed ? 'pass' : 'fail'" :style="{ height: b.height + '%' }"></view>
            </view>
            <text class="col-time">{{ b.time }}</text>
          </view>
        </view>
      </view>

      <!-- 逐题反馈 -->
      <text class="sec-title">答题反馈</text>
      <view class="feedback">
        <view
          v-for="(d, i) in result.details"
          :key="d.question_id"
          class="card fb-item"
          :class="d.correct ? 'right' : 'wrong'"
        >
          <view class="fb-head">
            <view class="fb-mark"><text>{{ d.correct ? '✓' : '✗' }}</text></view>
            <text class="fb-stem">{{ i + 1 }}. {{ d.stem }}</text>
          </view>
          <view class="fb-answers">
            <text v-if="d.correct" class="fb-line good">回答正确</text>
            <text v-else class="fb-line bad">
              你的答案：{{ d.user_answer.length ? d.user_answer.join('、') : '（未作答）' }}
            </text>
            <text v-if="!d.correct" class="fb-line">正确答案：{{ d.correct_answer.join('、') }}</text>
          </view>
          <text class="fb-exp">💡 {{ d.explanation }}</text>
          <view class="fb-kp">
            <text class="fb-kp-text">📚 涉及章节：《{{ d.chapter_title || '模块综合' }}》 · 知识点：{{ d.knowledge_point || '模块综合' }}</text>
            <view v-if="d.chapter_id" class="btn mini" @click="goChapter(d.chapter_id)"><text>查看讲解</text></view>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<style scoped>
.result { padding: 14px 14px 40px; display: flex; flex-direction: column; gap: 14px; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.result-bar { display: flex; align-items: center; gap: 20px; padding: 18px 16px; flex-wrap: wrap; }
.result-bar.pass { border-top: 8px solid #00a074; }
.result-bar.fail { border-top: 8px solid var(--sov-red); }
.result-score { display: flex; align-items: baseline; gap: 4px; }
.result-score .big { font-size: 48px; font-weight: 900; line-height: 1; }
.result-info { flex: 1; min-width: 150px; display: flex; flex-direction: column; gap: 4px; }
.result-info .stat { color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.auto-note {
  display: inline-block;
  background: #00a074; color: var(--sov-paper);
  font-size: 12.5px; font-weight: 900; border: 3px solid var(--sov-black);
  padding: 4px 12px;
}
.result-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.curve-card { padding: 18px 14px; }
.sec-title {
  font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em;
  border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; display: block; }
.chart {
  display: flex; align-items: flex-end; justify-content: space-between; gap: 8px;
  height: 180px; padding: 12px 4px 0;
  border-bottom: 3px solid var(--sov-black);
}
.col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; height: 100%; }
.col-score { font-size: 13px; font-weight: 900; }
.col-track {
  flex: 1; width: 60%;
  display: flex; align-items: flex-end;
  border: 2px solid var(--sov-black);
  background: var(--sov-white);
}
.col-fill { width: 100%; }
.col-fill.pass { background: #00a074; }
.col-fill.fail { background: var(--sov-red); }
.col-time { font-size: 10px; font-weight: 700; color: var(--sov-brown); }

.feedback { display: flex; flex-direction: column; gap: 14px; }
.fb-item { padding: 16px 14px; }
.fb-item.right { border-left: 10px solid #00a074; }
.fb-item.wrong { border-left: 10px solid var(--sov-red); }
.fb-head { display: flex; gap: 10px; align-items: flex-start; }
.fb-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; flex-shrink: 0;
  background: var(--sov-black); color: var(--sov-paper); font-weight: 900;
}
.fb-item.right .fb-mark { background: #00a074; }
.fb-item.wrong .fb-mark { background: var(--sov-red); }
.fb-stem { flex: 1; font-weight: 900; font-size: 14.5px; display: block; }
.fb-answers { margin: 10px 0 0; display: flex; flex-direction: column; gap: 4px; }
.fb-line { font-size: 13.5px; font-weight: 700; display: block; }
.fb-line.good { color: #00a074; }
.fb-line.bad { color: var(--sov-red); }
.fb-exp {
  margin: 10px 0 0; padding: 10px 12px;
  background: var(--sov-paper); border: 2px solid var(--sov-black);
  font-size: 13px; font-weight: 700;
  display: block;
}
.fb-kp {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  margin: 10px 0 0;
  font-size: 12.5px; font-weight: 900;
  color: #55677a;
  background: #fafbfc;
  border: 2px solid #d9e1e8;
  padding: 8px 12px;
  flex-wrap: wrap;
}
.fb-kp-text { flex: 1; display: block; }
</style>
