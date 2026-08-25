<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import client from '../../api/client'
import { useStudyTimer } from '../../composables/useStudyTimer'

useStudyTimer()

const code = ref('')
const info = ref(null)
const questions = ref([])
const answers = ref({})
const startTime = ref(0)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

onLoad(async (options) => {
  code.value = options.code || ''
  startTime.value = Date.now()
  try {
    const [inf, qs] = await Promise.all([
      client.get(`/modules/${code.value}/exam`),
      client.get(`/modules/${code.value}/exam/questions`),
    ])
    info.value = inf
    questions.value = qs
  } catch (e) {
    error.value = e.response?.data?.detail || '考核题目加载失败'
  } finally {
    loading.value = false
  }
})

const answeredCount = computed(() => Object.keys(answers.value).length)
const knowledgeQs = computed(() => questions.value.filter((q) => q.category === 'exam'))
const caseQs = computed(() => questions.value.filter((q) => q.category === 'exam_case'))

function isChecked(q, key) {
  return (answers.value[q.id] || []).includes(key)
}
function toggle(q, key) {
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
        title: '确认交卷',
        content: `还有 ${unanswered} 题未作答，未作答的题按答错处理，确定交卷吗？`,
        success: (r) => resolve(r.confirm),
        fail: () => resolve(false),
      })
    })
    if (!ok) return
  }
  submitting.value = true
  try {
    const res = await client.post('/exam/submit', {
      module_code: code.value,
      question_ids: questions.value.map((q) => q.id),
      answers: answers.value,
      duration_seconds: Math.round((Date.now() - startTime.value) / 1000),
    })
    uni.redirectTo({ url: `/pages/modules/examResult?id=${res.exam_record_id}&code=${code.value}` })
  } catch (e) {
    error.value = e.response?.data?.detail || '交卷失败'
    submitting.value = false
  }
}

function goBack() { uni.navigateBack() }
</script>

<template>
  <view class="exam">
    <view class="head">
      <view class="head-left">
        <text class="back" @click="goBack">← 返回模块</text>
        <text class="head-title">模块考核</text>
      </view>
      <view class="head-meta">
        <text class="badge black">{{ questions.length }} 题</text>
        <text class="badge gold">已答 {{ answeredCount }}</text>
      </view>
    </view>

    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <template v-if="info">
      <view class="card rules">
        <text class="rules-text">📄 {{ info.title }}：随机抽题 {{ questions.length }} 题（知识 {{ info.knowledge_count >= 7 ? 7 : info.knowledge_count }} + 案例 3），通过线 {{ info.pass_score }} 分，不强制限时，交卷后显示成绩与解析。</text>
      </view>

      <view class="card qcard">
        <template v-if="knowledgeQs.length">
          <view class="sec-title">
            <text class="sec-badge kb">知识考核</text>
          </view>
          <view
            v-for="(q, qi) in knowledgeQs"
            :key="q.id"
            class="question"
            :class="{ answered: (answers[q.id] || []).length > 0 }"
          >
            <view class="stem">
              <view class="qno"><text>{{ qi + 1 }}</text></view>
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

        <template v-if="caseQs.length">
          <view class="sec-title">
            <text class="sec-badge case">案例考核</text>
            <text>莱茵科技 × 林晓</text>
          </view>
          <view
            v-for="(q, qi) in caseQs"
            :key="q.id"
            class="question case-q"
            :class="{ answered: (answers[q.id] || []).length > 0 }"
          >
            <view class="stem">
              <view class="qno case-no"><text>{{ qi + 1 }}</text></view>
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
          <text>{{ submitting ? '交卷中...' : '交卷' }}</text>
        </view>
      </view>
    </template>
  </view>
</template>

<style scoped>
.exam { padding: 14px 14px 40px; display: flex; flex-direction: column; gap: 12px; }
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.head-left { display: flex; flex-direction: column; gap: 6px; }
.head-title { font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.head-meta { display: flex; gap: 10px; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.rules { padding: 14px 18px; background: var(--sov-paper); }
.rules-text { font-weight: 700; font-size: 13.5px; }

.qcard { padding: 16px 12px; }
.sec-title {
  display: flex; align-items: center; gap: 10px;
  font-size: 16px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em;
  border-bottom: 4px solid var(--sov-black);
  padding-bottom: 10px;
  margin: 0 0 12px;
}
.sec-title:not(:first-child) { margin-top: 24px; }
.sec-badge { padding: 3px 12px; border: 3px solid var(--sov-black); font-size: 12px; font-weight: 900; }
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
  padding: 9px 12px; border: 2px solid var(--sov-black);
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
</style>
