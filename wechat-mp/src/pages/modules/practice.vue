<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import client from '../../api/client'
import { useStudyTimer } from '../../composables/useStudyTimer'

useStudyTimer()

const code = ref('')
const chapterId = ref(0)
const questions = ref([])
const answers = ref({})
const result = ref(null)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    questions.value = await client.get(`/modules/${code.value}/chapters/${chapterId.value}/practice`)
  } catch (e) {
    error.value = e.response?.data?.detail || '训练题加载失败'
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  code.value = options.code || ''
  chapterId.value = Number(options.id) || 0
  load()
})

const answeredCount = computed(() => Object.keys(answers.value).length)
const knowledgeQs = computed(() => questions.value.filter((q) => q.category === 'practice'))
const caseQs = computed(() => questions.value.filter((q) => q.category === 'practice_case'))
const totalCount = computed(() => questions.value.length)

function qIndexIn(q, list) {
  return list.findIndex((x) => x.id === q.id) + 1
}

function isChecked(q, key) {
  return (answers.value[q.id] || []).includes(key)
}
function toggle(q, key) {
  if (result.value) return // 已提交，锁定答案
  const cur = answers.value[q.id] || []
  if (q.qtype === 'multiple') {
    answers.value[q.id] = cur.includes(key) ? cur.filter((k) => k !== key) : [...cur, key]
  } else {
    answers.value[q.id] = [key]
  }
}

async function submit() {
  const unanswered = questions.value.length - answeredCount.value
  if (unanswered > 0) {
    const ok = await new Promise((resolve) => {
      uni.showModal({
        title: '确认提交',
        content: `还有 ${unanswered} 题未作答，未作答的题按答错处理，确定提交吗？`,
        success: (r) => resolve(r.confirm),
        fail: () => resolve(false),
      })
    })
    if (!ok) return
  }
  submitting.value = true
  try {
    result.value = await client.post('/practice/submit', {
      chapter_id: Number(chapterId.value),
      answers: answers.value,
    })
    uni.pageScrollTo({ scrollTop: 0, duration: 200 })
  } catch (e) {
    error.value = e.response?.data?.detail || '提交失败'
  } finally {
    submitting.value = false
  }
}

function reset() {
  answers.value = {}
  result.value = null
}

function goBack() { uni.navigateBack() }
function goModule() {
  // 训练页由章节页 navigateTo 进入：返回章节(1层) → 返回模块(2层)
  uni.navigateBack({ delta: 2 })
}
function goChapterView() {
  // 查看讲解：返回章节页（第 1 层）
  uni.navigateBack({ delta: 1 })
}
</script>

<template>
  <view class="practice">
    <text class="back" @click="goBack">← 返回章节</text>

    <view class="head">
      <text class="head-title">章节训练</text>
      <view class="head-meta">
        <text class="badge black">{{ totalCount }} 题</text>
        <text class="badge gold">已答 {{ answeredCount }}</text>
      </view>
    </view>

    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <!-- 判分结果横幅 -->
    <view v-if="result" class="card result-bar" :class="result.score >= 60 ? 'pass' : 'fail'">
      <view class="result-score">
        <text class="big">{{ result.score }}</text>
        <text class="unit">分</text>
      </view>
      <view class="result-info">
        <text class="stat">答对 {{ result.correct_count }} / {{ result.total_count }} 题</text>
        <text class="tip">{{ result.score >= 60 ? '本章训练通过，可以进入模块考核！' : '未达到 60 分，建议重读讲解后重新练习。' }}</text>
        <text v-if="result.chapter_completed" class="auto-done">✓ 满分通过，本章已自动标记为已完成</text>
      </view>
      <view class="result-actions">
        <view class="btn primary" @click="reset"><text>重新练习</text></view>
        <view class="btn" @click="goModule"><text>返回模块</text></view>
      </view>
    </view>

    <view v-else-if="questions.length" class="qcard card">
      <!-- 知识巩固 -->
      <template v-if="knowledgeQs.length">
        <view class="sec-title">
          <text class="sec-badge kb">知识巩固</text>
          <text>本章知识点训练</text>
        </view>
        <view
          v-for="q in knowledgeQs"
          :key="q.id"
          class="question"
          :class="{ answered: (answers[q.id] || []).length > 0 }"
        >
          <view class="stem">
            <view class="qno"><text>{{ qIndexIn(q, knowledgeQs) }}</text></view>
            <text class="stem-text">{{ q.stem }}</text>
            <view class="qtype" :class="q.qtype">
              <text>{{ q.qtype === 'single' ? '单选' : q.qtype === 'multiple' ? '多选' : '判断' }}</text>
            </view>
          </view>
          <view class="options">
            <view
              v-for="opt in q.options"
              :key="opt.key"
              class="option"
              :class="{ checked: isChecked(q, opt.key) }"
              @click="toggle(q, opt.key)"
            >
              <view class="opt-key"><text>{{ opt.key }}</text></view>
              <text class="opt-text">{{ opt.text }}</text>
            </view>
          </view>
        </view>
      </template>

      <!-- 案例应用 -->
      <template v-if="caseQs.length">
        <view class="sec-title">
          <text class="sec-badge case">案例应用</text>
          <text>莱茵科技 × 林晓</text>
        </view>
        <view
          v-for="q in caseQs"
          :key="q.id"
          class="question case-q"
          :class="{ answered: (answers[q.id] || []).length > 0 }"
        >
          <view class="stem">
            <view class="qno case-no"><text>{{ qIndexIn(q, caseQs) }}</text></view>
            <text class="stem-text">{{ q.stem }}</text>
            <view class="qtype" :class="q.qtype">
              <text>{{ q.qtype === 'single' ? '单选' : q.qtype === 'multiple' ? '多选' : '判断' }}</text>
            </view>
          </view>
          <view class="options">
            <view
              v-for="opt in q.options"
              :key="opt.key"
              class="option"
              :class="{ checked: isChecked(q, opt.key) }"
              @click="toggle(q, opt.key)"
            >
              <view class="opt-key"><text>{{ opt.key }}</text></view>
              <text class="opt-text">{{ opt.text }}</text>
            </view>
          </view>
        </view>
      </template>

      <view class="btn primary submit-btn" :class="{ disabled: submitting }" @click="submit">
        <text>{{ submitting ? '提交中...' : '提交答案' }}</text>
      </view>
    </view>

    <!-- 判分后的逐题反馈 -->
    <view v-if="result" class="feedback">
      <text class="sec-title">答题反馈</text>
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
          <text v-if="!d.correct" class="fb-line">
            正确答案：{{ d.correct_answer.join('、') }}
          </text>
        </view>
        <text class="fb-exp">💡 {{ d.explanation }}</text>
        <view class="fb-kp">
          <text class="fb-kp-text">📚 本章《{{ d.chapter_title }}》 · 知识点：{{ d.knowledge_point || '本章综合' }}</text>
          <view class="btn mini" @click="goChapterView"><text>查看讲解</text></view>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.practice { padding: 14px 14px 40px; display: flex; flex-direction: column; gap: 12px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.head-title { font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.head-meta { display: flex; gap: 10px; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

/* 结果横幅 */
.result-bar { display: flex; align-items: center; gap: 20px; padding: 18px 16px; flex-wrap: wrap; }
.result-bar.pass { border-top: 8px solid #00a074; }
.result-bar.fail { border-top: 8px solid var(--sov-red); }
.result-score { display: flex; align-items: baseline; gap: 4px; }
.result-score .big { font-size: 48px; font-weight: 900; line-height: 1; }
.result-info { flex: 1; min-width: 150px; display: flex; flex-direction: column; gap: 2px; }
.result-info .stat { font-weight: 900; font-size: 15px; }
.result-info .tip { color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.auto-done {
  display: inline-block;
  background: #00a074;
  color: var(--sov-paper);
  font-size: 12.5px; font-weight: 900;
  border: 3px solid var(--sov-black);
  padding: 4px 12px;
}
.result-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.qcard { padding: 16px 12px; }
.sec-title {
  display: flex; align-items: center; gap: 10px;
  font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em;
  border-bottom: 4px solid var(--sov-black);
  padding-bottom: 10px;
  margin: 0 0 12px;
}
.sec-title:not(:first-child) { margin-top: 24px; }
.sec-badge {
  display: inline-block; padding: 3px 12px;
  border: 3px solid var(--sov-black);
  font-size: 12px; font-weight: 900; letter-spacing: .06em;
}
.sec-badge.kb { background: var(--sov-gold); color: var(--sov-black); }
.sec-badge.case { background: var(--sov-red); color: var(--sov-paper); }
.question { padding: 14px 0; border-bottom: 2px solid var(--sov-paper); }
.question:last-child { border-bottom: none; }
.case-q { background: var(--sov-paper); padding: 14px 12px; margin-bottom: 10px; border: 2px solid var(--sov-black); }
.qno.case-no { background: var(--sov-red); }
.stem { display: flex; align-items: flex-start; gap: 8px; margin: 0 0 12px; }
.stem-text { font-weight: 900; font-size: 15px; flex: 1; }
.qno {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 26px; height: 26px;
  background: var(--sov-black); color: var(--sov-paper);
  font-size: 13px; flex-shrink: 0; margin-top: 2px;
}
.qtype { margin-left: auto; flex-shrink: 0; font-size: 11px; padding: 2px 8px; border: 2px solid var(--sov-black); }
.qtype.single { background: var(--sov-gold); color: var(--sov-black); }
.qtype.multiple { background: var(--sov-red); color: var(--sov-paper); }
.qtype.judge { background: var(--sov-black); color: var(--sov-paper); }
.options { display: flex; flex-direction: column; gap: 8px; }
.option {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px;
  border: 2px solid var(--sov-black);
  background: var(--sov-white);
  font-size: 14px; font-weight: 700;
}
.option.checked { background: var(--sov-paper); box-shadow: inset 4px 0 0 var(--sov-red); }
.opt-key {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; flex-shrink: 0;
  border: 2px solid var(--sov-black); font-size: 12px; font-weight: 900;
}
.submit-btn { width: 100%; margin-top: 18px; padding: 12px 0; font-size: 15px; }
.disabled { opacity: .5; }

/* 反馈 */
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
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
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
