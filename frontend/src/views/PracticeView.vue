<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'
import { useStudyTimer } from '../composables/useStudyTimer'

useStudyTimer()

const route = useRoute()
const router = useRouter()
const code = route.params.code
const chapterId = route.params.id

const questions = ref([])
const answers = ref({})
const result = ref(null)          // 提交后的判分结果
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    questions.value = await client.get(`/modules/${code}/chapters/${chapterId}/practice`)
  } catch (e) {
    error.value = e.response?.data?.detail || '训练题加载失败'
  } finally {
    loading.value = false
  }
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
    if (!window.confirm(`还有 ${unanswered} 题未作答，未作答的题按答错处理，确定提交吗？`)) {
      return
    }
  }
  submitting.value = true
  try {
    result.value = await client.post('/practice/submit', {
      chapter_id: Number(chapterId),
      answers: answers.value,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
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
</script>

<template>
  <div class="practice">
    <div class="crumbs">
      <RouterLink :to="`/modules/${code}/chapters/${chapterId}`" class="back">← 返回章节</RouterLink>
    </div>

    <div class="head">
      <h1>章节训练</h1>
      <div class="head-meta">
        <span class="badge black">{{ totalCount }} 题</span>
        <span class="badge gold">已答 {{ answeredCount }}</span>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <!-- 判分结果横幅 -->
    <div v-if="result" class="card result-bar" :class="result.score >= 60 ? 'pass' : 'fail'">
      <div class="result-score">
        <span class="big">{{ result.score }}</span>
        <span class="unit">分</span>
      </div>
      <div class="result-info">
        <p class="stat">答对 <b>{{ result.correct_count }}</b> / {{ result.total_count }} 题</p>
        <p class="tip">{{ result.score >= 60 ? '本章训练通过，可以进入模块考核！' : '未达到 60 分，建议重读讲解后重新练习。' }}</p>
        <p v-if="result.chapter_completed" class="auto-done">✓ 满分通过，本章已自动标记为已完成</p>
      </div>
      <div class="result-actions">
        <button class="btn primary" @click="reset"><span>重新练习</span></button>
        <RouterLink :to="`/modules/${code}`" class="btn"><span>返回模块</span></RouterLink>
      </div>
    </div>

    <div v-else-if="questions.length" class="qcard card">
      <!-- 知识巩固 -->
      <template v-if="knowledgeQs.length">
        <h2 class="sec-title"><span class="sec-badge kb">知识巩固</span>本章知识点训练</h2>
        <div
          v-for="q in knowledgeQs"
          :key="q.id"
          class="question"
          :class="{ answered: (answers[q.id] || []).length > 0 }"
        >
          <p class="stem">
            <span class="qno">{{ qIndexIn(q, knowledgeQs) }}</span>
            {{ q.stem }}
            <span class="qtype" :class="q.qtype">
              {{ q.qtype === 'single' ? '单选' : q.qtype === 'multiple' ? '多选' : '判断' }}
            </span>
          </p>
          <div class="options">
            <label
              v-for="opt in q.options"
              :key="opt.key"
              class="option"
              :class="{ checked: isChecked(q, opt.key) }"
            >
              <input
                :type="q.qtype === 'multiple' ? 'checkbox' : 'radio'"
                :name="'q' + q.id"
                :checked="isChecked(q, opt.key)"
                @change="toggle(q, opt.key)"
              />
              <span class="opt-key">{{ opt.key }}</span>
              <span class="opt-text">{{ opt.text }}</span>
            </label>
          </div>
        </div>
      </template>

      <!-- 案例应用 -->
      <template v-if="caseQs.length">
        <h2 class="sec-title"><span class="sec-badge case">案例应用</span>莱茵科技 × 林晓</h2>
        <div
          v-for="q in caseQs"
          :key="q.id"
          class="question case-q"
          :class="{ answered: (answers[q.id] || []).length > 0 }"
        >
          <p class="stem">
            <span class="qno case-no">{{ qIndexIn(q, caseQs) }}</span>
            {{ q.stem }}
            <span class="qtype" :class="q.qtype">
              {{ q.qtype === 'single' ? '单选' : q.qtype === 'multiple' ? '多选' : '判断' }}
            </span>
          </p>
          <div class="options">
            <label
              v-for="opt in q.options"
              :key="opt.key"
              class="option"
              :class="{ checked: isChecked(q, opt.key) }"
            >
              <input
                :type="q.qtype === 'multiple' ? 'checkbox' : 'radio'"
                :name="'q' + q.id"
                :checked="isChecked(q, opt.key)"
                @change="toggle(q, opt.key)"
              />
              <span class="opt-key">{{ opt.key }}</span>
              <span class="opt-text">{{ opt.text }}</span>
            </label>
          </div>
        </div>
      </template>

      <button class="btn primary submit-btn" :disabled="submitting" @click="submit">
        <span>{{ submitting ? '提交中...' : '提交答案' }}</span>
      </button>
    </div>

    <!-- 判分后的逐题反馈 -->
    <div v-if="result" class="feedback">
      <h2 class="sec-title">答题反馈</h2>
      <div
        v-for="(d, i) in result.details"
        :key="d.question_id"
        class="card fb-item"
        :class="d.correct ? 'right' : 'wrong'"
      >
        <div class="fb-head">
          <span class="fb-mark">{{ d.correct ? '✓' : '✗' }}</span>
          <p class="fb-stem">
            <span v-if="d.category === 'practice_case'" class="fb-case-tag">案例</span>
            {{ i + 1 }}. {{ d.stem }}
          </p>
        </div>
        <div class="fb-answers">
          <p v-if="d.correct" class="fb-line good">回答正确</p>
          <p v-else class="fb-line bad">
            你的答案：{{ d.user_answer.length ? d.user_answer.join('、') : '（未作答）' }}
          </p>
          <p v-if="!d.correct" class="fb-line">
            正确答案：<b>{{ d.correct_answer.join('、') }}</b>
          </p>
        </div>
        <p class="fb-exp">💡 {{ d.explanation }}</p>
        <div class="fb-kp">
          <span>📚 本章《{{ d.chapter_title }}》 · 知识点：{{ d.knowledge_point || '本章综合' }}</span>
          <RouterLink :to="`/modules/${code}/chapters/${d.chapter_id}`" class="btn mini">
            <span>查看讲解</span>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.crumbs { margin-bottom: 14px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; flex-wrap: wrap; }
.head h1 { margin: 0; }
.head-meta { display: flex; gap: 10px; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

/* 结果横幅 */
.result-bar { display: flex; align-items: center; gap: 20px; padding: 20px 24px; margin-bottom: 20px; flex-wrap: wrap; }
.result-bar.pass { border-top: 8px solid var(--sov-green-dark, #00a074); }
.result-bar.fail { border-top: 8px solid var(--sov-red); }
.result-score { display: flex; align-items: baseline; gap: 4px; }
.result-score .big { font-size: 52px; font-weight: 900; line-height: 1; }
.result-info { flex: 1; min-width: 180px; }
.result-info .stat { margin: 0; font-weight: 900; font-size: 15px; }
.result-info .tip { margin: 4px 0 0; color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.auto-done {
  margin: 6px 0 0;
  display: inline-block;
  background: var(--sov-green-dark, #00a074);
  color: var(--sov-paper);
  font-size: 12.5px; font-weight: 900;
  border: 3px solid var(--sov-black);
  padding: 4px 12px;
}
.result-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.qcard { padding: 26px; margin-bottom: 20px; }
@media (max-width: 720px) {
  .qcard { padding: 14px 12px; }
  .head h1 { font-size: 19px; }
  .result-bar { padding: 16px 14px; }
  .result-score .big { font-size: 44px; }
  .question { padding: 12px 0; }
  .fb-item { padding: 14px 12px; }
  .fb-kp { flex-direction: column; align-items: flex-start; }
}
.sec-title {
  margin: 0 0 14px; font-size: 17px;
  border-bottom: 4px solid var(--sov-black);
  padding-bottom: 10px;
  display: flex; align-items: center; gap: 10px;
}
.sec-title:not(:first-child) { margin-top: 26px; }
.sec-badge {
  display: inline-block; padding: 3px 12px;
  border: 3px solid var(--sov-black);
  font-size: 12px; font-weight: 900; letter-spacing: .06em;
}
.sec-badge.kb { background: var(--sov-gold); color: var(--sov-black); }
.sec-badge.case { background: var(--sov-red); color: var(--sov-paper); }
.question { padding: 16px 0; border-bottom: 2px solid var(--sov-paper); }
.question:last-child { border-bottom: none; }
.case-q { background: var(--sov-paper); padding: 16px 14px; margin-bottom: 10px; border: 2px solid var(--sov-black); }
.case-q .option { background: var(--sov-white); }
.qno.case-no { background: var(--sov-red); }
.stem { margin: 0 0 12px; font-weight: 900; font-size: 15px; display: flex; align-items: flex-start; gap: 8px; }
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
  cursor: pointer;
  font-size: 14px; font-weight: 700;
  transition: background-color 100ms linear;
}
.option:hover { background: var(--sov-paper); }
.option.checked { background: var(--sov-paper); box-shadow: inset 4px 0 0 var(--sov-red); }
.option input { accent-color: var(--sov-red); width: 16px; height: 16px; }
.opt-key {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; flex-shrink: 0;
  border: 2px solid var(--sov-black); font-size: 12px; font-weight: 900;
}
.submit-btn { width: 100%; margin-top: 18px; padding: 12px 0; font-size: 15px; }

/* 反馈 */
.sec-title { margin: 0 0 16px; font-size: 18px; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; }
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
  border: 2px solid var(--sov-black);
  vertical-align: 1px;
}
.fb-answers { margin: 10px 0 0; padding-left: 36px; }
.fb-line { margin: 2px 0; font-size: 13.5px; font-weight: 700; }
.fb-line.good { color: var(--sov-green-dark, #00a074); }
.fb-line.bad { color: var(--sov-red); }
.fb-exp {
  margin: 10px 0 0; padding: 10px 12px;
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
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
