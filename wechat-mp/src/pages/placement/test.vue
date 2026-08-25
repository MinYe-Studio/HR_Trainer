<script setup>
import { computed, ref } from 'vue'
import { onHide, onLoad, onUnload } from '@dcloudio/uni-app'
import client from '../../api/client'

const DRAFT_KEY = 'hrt_placement_draft_v1'

const questions = ref([])
const modules = ref([])
const answers = ref({})          // {questionId: [key,...]}
const currentIdx = ref(0)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const restored = ref(false)

// ---------- 答案暂存：中途退出自动保存，重新进入可继续 ----------
function saveDraft() {
  if (!questions.value.length) return
  try {
    uni.setStorageSync(DRAFT_KEY, JSON.stringify({
      answers: answers.value,
      currentIdx: currentIdx.value,
      qids: questions.value.map((q) => q.id),
      at: Date.now(),
    }))
  } catch { /* 存储失败忽略 */ }
}

function clearDraft() {
  try { uni.removeStorageSync(DRAFT_KEY) } catch { /* 忽略 */ }
}

function restoreDraft(qs) {
  try {
    const raw = uni.getStorageSync(DRAFT_KEY)
    if (!raw) return
    const draft = JSON.parse(raw)
    const qidSet = new Set(qs.map((q) => q.id))
    // 仅恢复与当前试卷一致的答案（题目集变化则丢弃）
    const validAnswers = {}
    for (const [qid, keys] of Object.entries(draft.answers || {})) {
      if (qidSet.has(Number(qid)) && Array.isArray(keys)) validAnswers[qid] = keys
    }
    answers.value = validAnswers
    const maxIdx = Math.max(0, modules.value.length - 1)
    currentIdx.value = Math.min(Number(draft.currentIdx) || 0, maxIdx)
    restored.value = Object.keys(validAnswers).length > 0
  } catch { /* 草稿损坏忽略 */ }
}

onLoad(async () => {
  try {
    const [qs, mods] = await Promise.all([
      client.get('/placement/questions'),
      client.get('/modules'),
    ])
    questions.value = qs
    const moduleIds = new Set(qs.map((q) => q.module_id))
    modules.value = mods.filter((m) => moduleIds.has(m.id))
    restoreDraft(qs)
  } catch (e) {
    error.value = e.response?.data?.detail || '测试题加载失败'
  } finally {
    loading.value = false
  }
})

// 退出页面（返回/跳转）时保存草稿
onHide(saveDraft)
onUnload(saveDraft)

const moduleGroups = computed(() =>
  modules.value.map((m) => ({
    ...m,
    questions: questions.value.filter((q) => q.module_id === m.id),
  }))
)
const current = computed(() => moduleGroups.value[currentIdx.value] || null)
const totalCount = computed(() => questions.value.length)
const answeredCount = computed(() => Object.keys(answers.value).length)
const progress = computed(() =>
  totalCount.value ? Math.round((answeredCount.value / totalCount.value) * 100) : 0
)

function isChecked(q, key) {
  return (answers.value[q.id] || []).includes(key)
}
function toggle(q, key) {
  const cur = answers.value[q.id] || []
  if (q.qtype === 'multiple') {
    answers.value[q.id] = cur.includes(key)
      ? cur.filter((k) => k !== key)
      : [...cur, key]
  } else {
    answers.value[q.id] = [key]
  }
  saveDraft()
}
function moduleAnswered(m) {
  return m.questions.filter((q) => (answers.value[q.id] || []).length > 0).length
}

function clearAndRestart() {
  answers.value = {}
  currentIdx.value = 0
  restored.value = false
  clearDraft()
  saveDraft()
}

async function submit() {
  const unanswered = totalCount.value - answeredCount.value
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
    await client.post('/placement/submit', {
      question_ids: questions.value.map((q) => q.id),
      answers: answers.value,
    })
    clearDraft()
    uni.redirectTo({ url: '/pages/placement/result' })
  } catch (e) {
    error.value = e.response?.data?.detail || '提交失败，请重试'
    submitting.value = false
  }
}
</script>

<template>
  <view class="test">
    <view class="head">
      <text class="head-title">入营摸底测试</text>
      <view class="progress">
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progress + '%' }"></view>
        </view>
        <text class="progress-text">{{ answeredCount }} / {{ totalCount }} 题</text>
      </view>
    </view>

    <!-- 恢复上次进度的提示 -->
    <view v-if="restored" class="restore-tip">
      <text>↻ 已恢复上次答题进度（{{ answeredCount }} 题），可继续作答或重新开始</text>
      <text class="restore-clear" @click="clearAndRestart">重新开始</text>
    </view>

    <!-- 模块切换 -->
    <scroll-view scroll-x class="mods">
      <view class="mods-inner">
        <view
          v-for="(m, i) in moduleGroups"
          :key="m.id"
          class="mod-tab"
          :class="{ active: i === currentIdx }"
          @click="currentIdx = i"
        >
          <text>{{ m.name }}</text>
          <text class="done" :class="{ ok: moduleAnswered(m) === m.questions.length }">
            {{ moduleAnswered(m) }}/{{ m.questions.length }}
          </text>
        </view>
      </view>
    </scroll-view>

    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <template v-if="current">
      <view class="card qcard">
        <text class="mod-name">{{ current.name }}</text>
        <view
          v-for="(q, qi) in current.questions"
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
      </view>

      <view class="nav-btns">
        <view class="btn" :class="{ disabled: currentIdx === 0 }" @click="currentIdx--">
          <text>上一模块</text>
        </view>
        <view
          v-if="currentIdx < moduleGroups.length - 1"
          class="btn primary"
          @click="currentIdx++"
        >
          <text>下一模块</text>
        </view>
        <view v-else class="btn primary" :class="{ disabled: submitting }" @click="submit">
          <text>{{ submitting ? '提交中...' : '提交测试' }}</text>
        </view>
      </view>
    </template>
  </view>
</template>

<style scoped>
.test { padding: 14px 14px 40px; }

/* 恢复进度提示条 */
.restore-tip {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 8px 12px;
  background: var(--sov-gold);
  border: 3px solid var(--sov-black);
  font-size: 12px; font-weight: 900;
  margin-bottom: 12px;
}
.restore-clear {
  flex-shrink: 0;
  color: var(--sov-red-dark);
  text-decoration: underline;
}
.head { display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px; }
.head-title { font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.progress { display: flex; align-items: center; gap: 10px; }
.progress-track {
  flex: 1; height: 16px;
  border: 3px solid var(--sov-black);
  background: var(--sov-white);
}
.progress-fill { height: 100%; background: var(--sov-red); transition: width 150ms linear; }
.progress-text { font-size: 13px; font-weight: 900; white-space: nowrap; }

/* 模块切换（横向滚动） */
.mods { width: 100%; white-space: nowrap; margin-bottom: 16px; }
.mods-inner { display: inline-flex; gap: 8px; padding: 2px; }
.mod-tab {
  padding: 8px 14px;
  border: 3px solid var(--sov-black);
  background: var(--sov-paper);
  color: var(--sov-black);
  font-size: 13px; font-weight: 900;
  display: inline-flex; align-items: center; gap: 8px;
  box-shadow: var(--shadow-sm);
}
.mod-tab.active { background: var(--sov-red); color: var(--sov-paper); }
.mod-tab .done { font-size: 11px; opacity: .8; }
.mod-tab .done.ok { color: #00a074; }
.mod-tab.active .done.ok { color: #d8ffe9; }

.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.qcard { padding: 20px 14px; margin-bottom: 20px; }
.mod-name {
  display: block; margin: 0 0 16px; padding-bottom: 12px;
  border-bottom: 4px solid var(--sov-black);
  font-size: 18px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em;
}
.question { padding: 14px 0; border-bottom: 2px solid var(--sov-paper); }
.question:last-child { border-bottom: none; }
.stem { display: flex; align-items: flex-start; gap: 8px; margin: 0 0 12px; }
.stem-text { font-weight: 900; font-size: 15px; flex: 1; }
.qno {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 26px; height: 26px;
  background: var(--sov-black); color: var(--sov-paper);
  font-size: 13px; flex-shrink: 0; margin-top: 2px;
}
.qtype {
  margin-left: auto; flex-shrink: 0;
  font-size: 11px; padding: 2px 8px;
  border: 2px solid var(--sov-black);
}
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
  border: 2px solid var(--sov-black);
  font-size: 12px; font-weight: 900;
}

.nav-btns { display: flex; gap: 14px; justify-content: space-between; }
.nav-btns .btn { flex: 1; }
.disabled { opacity: .5; }
</style>
