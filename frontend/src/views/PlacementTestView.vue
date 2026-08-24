<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()
const questions = ref([])
const modules = ref([])
const answers = ref({})          // {questionId: [key,...]}
const currentIdx = ref(0)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const [qs, mods] = await Promise.all([
      client.get('/placement/questions'),
      client.get('/modules'),
    ])
    questions.value = qs
    const moduleIds = new Set(qs.map((q) => q.module_id))
    modules.value = mods.filter((m) => moduleIds.has(m.id))
  } catch (e) {
    error.value = e.response?.data?.detail || '测试题加载失败'
  } finally {
    loading.value = false
  }
})

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
}
function moduleAnswered(m) {
  return m.questions.filter((q) => (answers.value[q.id] || []).length > 0).length
}

async function submit() {
  const unanswered = totalCount.value - answeredCount.value
  if (unanswered > 0) {
    if (!window.confirm(`还有 ${unanswered} 题未作答，未作答的题按答错处理，确定提交吗？`)) {
      return
    }
  }
  submitting.value = true
  try {
    await client.post('/placement/submit', {
      question_ids: questions.value.map((q) => q.id),
      answers: answers.value,
    })
    router.push('/placement/result')
  } catch (e) {
    error.value = e.response?.data?.detail || '提交失败，请重试'
    submitting.value = false
  }
}
</script>

<template>
  <div class="test">
    <div class="head">
      <h1>入营摸底测试</h1>
      <div class="progress">
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="progress-text">{{ answeredCount }} / {{ totalCount }} 题</span>
      </div>
    </div>

    <!-- 模块切换 -->
    <div class="mods">
      <button
        v-for="(m, i) in moduleGroups"
        :key="m.id"
        class="mod-tab"
        :class="{ active: i === currentIdx }"
        @click="currentIdx = i"
      >
        {{ m.name }}
        <span class="done" :class="{ ok: moduleAnswered(m) === m.questions.length }">
          {{ moduleAnswered(m) }}/{{ m.questions.length }}
        </span>
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <template v-if="current">
      <div class="card qcard">
        <h2 class="mod-name">{{ current.name }}</h2>
        <div
          v-for="(q, qi) in current.questions"
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
      </div>

      <div class="nav-btns">
        <button class="btn" :disabled="currentIdx === 0" @click="currentIdx--">
          <span>上一模块</span>
        </button>
        <button
          v-if="currentIdx < moduleGroups.length - 1"
          class="btn primary"
          @click="currentIdx++"
        >
          <span>下一模块</span>
        </button>
        <button v-else class="btn primary" :disabled="submitting" @click="submit">
          <span>{{ submitting ? '提交中...' : '提交测试' }}</span>
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 18px; flex-wrap: wrap; }
.test h1 { margin: 0; }
.progress { display: flex; align-items: center; gap: 10px; min-width: 260px; }
.progress-track {
  flex: 1; height: 16px;
  border: 3px solid var(--sov-black);
  background: var(--sov-white);
}
.progress-fill { height: 100%; background: var(--sov-red); transition: width 150ms linear; }
.progress-text { font-size: 13px; font-weight: 900; white-space: nowrap; }

.mods { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.mod-tab {
  padding: 8px 14px;
  border: 3px solid var(--sov-black);
  border-radius: 0;
  background: var(--sov-paper);
  color: var(--sov-black);
  font-family: var(--font-sans);
  font-size: 13px; font-weight: 900;
  cursor: pointer;
  display: inline-flex; align-items: center; gap: 8px;
  box-shadow: var(--shadow-sm);
  transition: transform 100ms linear, box-shadow 100ms linear;
}
.mod-tab:hover { transform: translate(2px, 2px); box-shadow: none; }
.mod-tab.active { background: var(--sov-red); color: var(--sov-paper); }
.mod-tab .done { font-size: 11px; opacity: .8; }
.mod-tab .done.ok { color: var(--sov-green-dark, #00a074); }
.mod-tab.active .done.ok { color: #d8ffe9; }

.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.qcard { padding: 26px; margin-bottom: 20px; }
.mod-name {
  margin: 0 0 20px; padding-bottom: 12px;
  border-bottom: 4px solid var(--sov-black);
  font-size: 18px;
}
.question { padding: 16px 0; border-bottom: 2px solid var(--sov-paper); }
.question:last-child { border-bottom: none; }
.stem { margin: 0 0 12px; font-weight: 900; font-size: 15px; display: flex; align-items: flex-start; gap: 8px; }
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
  border: 2px solid var(--sov-border, #d9e1e8);
  border-color: var(--sov-black);
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
  border: 2px solid var(--sov-black);
  font-size: 12px; font-weight: 900;
}

.nav-btns { display: flex; gap: 14px; justify-content: space-between; }
.nav-btns .btn { min-width: 150px; }
</style>
