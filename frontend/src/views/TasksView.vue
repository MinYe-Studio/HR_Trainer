<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()
const data = ref(null)
const examStatus = ref({})
const loading = ref(true)
const error = ref('')

// 学习路径
const pathCodes = ref([])
const savingPath = ref(false)
const pathSaved = ref(false)
const DEFAULT_PATH = ['recruitment', 'performance', 'compensation', 'employee-relations', 'training', 'labor-law']
const moduleNames = {
  recruitment: '招聘与面试',
  performance: '绩效管理',
  compensation: '薪酬福利',
  'employee-relations': '员工关系',
  training: '培训与人才发展',
  'labor-law': '劳动法与合规',
}

const levelBadge = { focus: 'red', consolidate: 'gold', express: 'black' }
const levelText = { focus: '重点学习', consolidate: '巩固提升', express: '快速通道' }

onMounted(async () => {
  try {
    const [tasks, st, path] = await Promise.all([
      client.get('/placement/tasks'),
      client.get('/stats').catch(() => null),
      client.get('/learning-path').catch(() => ({ module_codes: DEFAULT_PATH })),
    ])
    data.value = tasks
    pathCodes.value = (path.module_codes && path.module_codes.length) ? path.module_codes : [...DEFAULT_PATH]
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

function move(idx, dir) {
  const target = idx + dir
  if (target < 0 || target >= pathCodes.value.length) return
  const arr = [...pathCodes.value]
  ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
  pathCodes.value = arr
  pathSaved.value = false
}

async function savePath() {
  savingPath.value = true
  try {
    await client.put('/learning-path', { module_codes: pathCodes.value })
    pathSaved.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    savingPath.value = false
  }
}

async function resetPath() {
  pathCodes.value = [...DEFAULT_PATH]
  pathSaved.value = false
  savingPath.value = true
  try {
    await client.put('/learning-path', { module_codes: pathCodes.value })
    pathSaved.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    savingPath.value = false
  }
}
</script>

<template>
  <div class="tasks">
    <div class="head">
      <h1>教学任务</h1>
      <span class="head-bar red"></span>
    </div>
    <p class="tip">根据你的摸底测试成绩生成的个性化学习任务，按优先级排序。</p>

    <!-- 个性化学习路径编辑器 -->
    <div class="card path-card">
      <div class="path-head">
        <h2>个性化学习路径</h2>
        <div class="path-head-actions">
          <button class="btn small" :disabled="savingPath" @click="savePath">
            <span>{{ savingPath ? '保存中...' : '保存路径' }}</span>
          </button>
          <button class="btn small" :disabled="savingPath" @click="resetPath">
            <span>恢复默认</span>
          </button>
        </div>
      </div>
      <p class="path-tip">调整模块学习顺序（默认：招聘→绩效→薪酬→员工关系→培训→劳动法），保存后技能模块页将按此顺序展示。</p>
      <p v-if="pathSaved" class="path-saved">✓ 学习路径已保存</p>
      <div class="path-list">
        <div v-for="(code, i) in pathCodes" :key="code" class="path-row">
          <span class="path-no">{{ i + 1 }}</span>
          <span class="path-name">{{ moduleNames[code] || code }}</span>
          <div class="path-btns">
            <button class="arrow" :disabled="i === 0" @click="move(i, -1)" title="上移">↑</button>
            <button class="arrow" :disabled="i === pathCodes.length - 1" @click="move(i, 1)" title="下移">↓</button>
          </div>
        </div>
      </div>
    </div>

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
.tip { margin: 0 0 20px; color: var(--sov-brown); font-weight: 700; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

/* 学习路径编辑器 */
.path-card { padding: 20px 24px; margin-bottom: 20px; }
.path-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px; flex-wrap: wrap; }
.path-head h2 { margin: 0; font-size: 17px; }
.path-head-actions { display: flex; gap: 10px; }
.btn.small { padding: 6px 16px; font-size: 13px; box-shadow: var(--shadow-sm); }
.path-tip { margin: 0 0 8px; color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.path-saved {
  display: inline-block; margin: 0 0 10px;
  background: var(--sov-green-dark, #00a074); color: var(--sov-paper);
  font-size: 12.5px; font-weight: 900; border: 3px solid var(--sov-black);
  padding: 3px 10px;
}
.path-list { display: flex; flex-direction: column; gap: 6px; }
.path-row {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 12px;
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
}
.path-no {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; flex-shrink: 0;
  background: var(--sov-black); color: var(--sov-paper);
  font-size: 13px; font-weight: 900;
}
.path-name { flex: 1; font-weight: 900; font-size: 14px; }
.path-btns { display: flex; gap: 6px; }
.arrow {
  width: 28px; height: 28px;
  border: 2px solid var(--sov-black);
  background: var(--sov-white);
  color: var(--sov-black);
  font-weight: 900; cursor: pointer;
}
.arrow:hover { background: var(--sov-gold); }
.arrow:disabled { opacity: .35; cursor: not-allowed; background: var(--sov-white); }

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
