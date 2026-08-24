<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const router = useRouter()
const code = route.params.code

const info = ref(null)
const questions = ref([])
const answers = ref({})
const startTime = ref(0)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

onMounted(async () => {
  startTime.value = Date.now()
  try {
    const [inf, qs] = await Promise.all([
      client.get(`/modules/${code}/exam`),
      client.get(`/modules/${code}/exam/questions`),
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
    if (!window.confirm(`还有 ${unanswered} 题未作答，未作答的题按答错处理，确定交卷吗？`)) {
      return
    }
  }
  submitting.value = true
  try {
    const res = await client.post('/exam/submit', {
      module_code: code,
      question_ids: questions.value.map((q) => q.id),
      answers: answers.value,
      duration_seconds: Math.round((Date.now() - startTime.value) / 1000),
    })
    router.push(`/modules/${code}/exam/result/${res.exam_record_id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || '交卷失败'
    submitting.value = false
  }
}
</script>

<template>
  <div class="exam">
    <div class="head">
      <div>
        <RouterLink :to="`/modules/${code}`" class="back">← 返回模块</RouterLink>
        <h1>模块考核</h1>
      </div>
      <div class="head-meta">
        <span class="badge black">{{ questions.length }} 题</span>
        <span class="badge gold">已答 {{ answeredCount }}</span>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <template v-if="info">
      <div class="card rules">
        <p>📄 {{ info.title }}：随机抽题 <b>{{ questions.length }}</b> 题（知识 {{ info.knowledge_count >= 7 ? 7 : info.knowledge_count }} + 案例 3），通过线 <b>{{ info.pass_score }}</b> 分，不强制限时，交卷后显示成绩与解析。</p>
      </div>

      <div class="card qcard">
        <template v-if="knowledgeQs.length">
          <h2 class="sec-title"><span class="sec-badge kb">知识考核</span></h2>
          <div
            v-for="(q, qi) in knowledgeQs"
            :key="q.id"
            class="question"
            :class="{ answered: (answers[q.id] || []).length > 0 }"
          >
            <p class="stem">
              <span class="qno">{{ qi + 1 }}</span>
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

        <template v-if="caseQs.length">
          <h2 class="sec-title"><span class="sec-badge case">案例考核</span>莱茵科技 × 林晓</h2>
          <div
            v-for="(q, qi) in caseQs"
            :key="q.id"
            class="question case-q"
            :class="{ answered: (answers[q.id] || []).length > 0 }"
          >
            <p class="stem">
              <span class="qno case-no">{{ qi + 1 }}</span>
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
          <span>{{ submitting ? '交卷中...' : '交卷' }}</span>
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.head h1 { margin: 6px 0 0; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.head-meta { display: flex; gap: 10px; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.rules { padding: 14px 18px; margin-bottom: 18px; background: var(--sov-paper); }
.rules p { margin: 0; font-weight: 700; font-size: 13.5px; }

.qcard { padding: 26px; }
.sec-title {
  margin: 0 0 14px; font-size: 16px;
  border-bottom: 4px solid var(--sov-black); padding-bottom: 10px;
  display: flex; align-items: center; gap: 10px;
}
.sec-title:not(:first-child) { margin-top: 26px; }
.sec-badge { padding: 3px 12px; border: 3px solid var(--sov-black); font-size: 12px; font-weight: 900; }
.sec-badge.kb { background: var(--sov-gold); color: var(--sov-black); }
.sec-badge.case { background: var(--sov-red); color: var(--sov-paper); }

.question { padding: 16px 0; border-bottom: 2px solid var(--sov-paper); }
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
  padding: 9px 12px; border: 2px solid var(--sov-black);
  background: var(--sov-white); cursor: pointer;
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
</style>
