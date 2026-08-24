<script setup>
import { useUserStore } from '../stores/user'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const userStore = useUserStore()
const router = useRouter()
const error = ref('')

// 入营测试引导横幅：未参加测试时显示，可关闭（本次会话内不再提示）
const showBanner = ref(false)
const dismissed = sessionStorage.getItem('placement_banner_dismissed') === '1'

// 遗忘曲线复习提醒
const reviews = ref([])

// 学习统计仪表盘
const stats = ref(null)

// 个性化学习路径（首页，常态收起；首次登录展开引导）
const pathCodes = ref([])
const pathExpanded = ref(!localStorage.getItem('path_prompt_done'))
const pathFirstTime = ref(!localStorage.getItem('path_prompt_done'))
const pathSaving = ref(false)
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

onMounted(async () => {
  try {
    const [latest, rev, st, path] = await Promise.all([
      client.get('/placement/latest'),
      client.get('/dashboard/review').catch(() => ({ reviews: [] })),
      client.get('/stats').catch(() => null),
      client.get('/learning-path').catch(() => ({ module_codes: DEFAULT_PATH })),
    ])
    showBanner.value = !latest && !dismissed
    reviews.value = rev.reviews || []
    stats.value = st
    pathCodes.value = (path.module_codes && path.module_codes.length)
      ? path.module_codes
      : [...DEFAULT_PATH]
  } catch {
    // 网络异常时静默跳过引导
  }
})

function pathMove(idx, dir) {
  const target = idx + dir
  if (target < 0 || target >= pathCodes.value.length) return
  const arr = [...pathCodes.value]
  ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
  pathCodes.value = arr
  pathSaved.value = false
}

async function savePath() {
  pathSaving.value = true
  try {
    await client.put('/learning-path', { module_codes: pathCodes.value })
    pathSaved.value = true
    pathFirstTime.value = false
    localStorage.setItem('path_prompt_done', '1')
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    pathSaving.value = false
  }
}

function skipPath() {
  localStorage.setItem('path_prompt_done', '1')
  pathFirstTime.value = false
  pathExpanded.value = false
}

async function resetPath() {
  pathCodes.value = [...DEFAULT_PATH]
  pathSaved.value = false
  await savePath()
}

function goPlacement() {
  sessionStorage.setItem('placement_banner_dismissed', '1')
  router.push('/placement')
}
function dismissBanner() {
  sessionStorage.setItem('placement_banner_dismissed', '1')
  showBanner.value = false
}

async function markReviewed(code) {
  try {
    await client.post(`/dashboard/review/${code}/done`)
    const rev = await client.get('/dashboard/review')
    reviews.value = rev.reviews || []
  } catch {
    // 忽略
  }
}
</script>

<template>
  <div class="home">
    <!-- Hero：纯黑底 + 莱茵生命网格构图（置顶） -->
    <section class="hero">
      <div class="hero-grid grid-pattern on-dark"></div>
      <div class="hero-content">
        <h1>欢迎回来，<br />{{ userStore.user?.nickname || userStore.user?.username }}</h1>
        <p class="hero-sub">系统学习六大 HR 核心技能 · 章节训练巩固 · 模块考核认证</p>
        <div class="actions">
          <RouterLink class="btn primary" to="/modules"><span>开始学习</span></RouterLink>
          <RouterLink class="btn primary" to="/tasks"><span>教学任务</span></RouterLink>
        </div>
      </div>
      <!-- 几何块面（右下角） -->
      <div class="hero-blocks">
        <span class="blk red"></span>
        <span class="blk gold"></span>
        <span class="blk paper"></span>
      </div>
    </section>

    <!-- 个性化学习路径（常态收起，可展开；首次登录展开引导） -->
    <div class="card path-card" :class="{ 'first-open': pathExpanded }">
      <div class="path-head" @click="pathExpanded = !pathExpanded">
        <div class="path-title">
          <h2>个性化学习路径</h2>
          <span v-if="pathFirstTime && pathExpanded" class="badge red">NEW</span>
        </div>
        <span class="path-toggle">{{ pathExpanded ? '收起 ▾' : '展开 ▸' }}</span>
      </div>

      <div v-show="pathExpanded" class="path-body">
        <p v-if="pathFirstTime" class="path-tip">首次使用：请选择你的模块学习顺序（默认：招聘→绩效→薪酬→员工关系→培训→劳动法），可随时修改。</p>
        <p v-else class="path-tip">调整模块学习顺序，保存后技能模块页将按此顺序展示。</p>
        <p v-if="error" class="modal-error">{{ error }}</p>
        <p v-if="pathSaved" class="path-saved">✓ 学习路径已保存</p>

        <div class="path-list">
          <div v-for="(code, i) in pathCodes" :key="code" class="path-row">
            <span class="path-no">{{ i + 1 }}</span>
            <span class="path-name">{{ moduleNames[code] || code }}</span>
            <div class="path-btns">
              <button class="arrow" :disabled="i === 0" @click="pathMove(i, -1)" title="上移">↑</button>
              <button class="arrow" :disabled="i === pathCodes.length - 1" @click="pathMove(i, 1)" title="下移">↓</button>
            </div>
          </div>
        </div>

        <div class="path-actions">
          <button class="btn primary small" :disabled="pathSaving" @click="savePath">
            <span>{{ pathSaving ? '保存中...' : '保存路径' }}</span>
          </button>
          <button v-if="pathFirstTime" class="btn small" @click="skipPath">
            <span>跳过，使用默认</span>
          </button>
          <button class="btn small" :disabled="pathSaving" @click="resetPath">
            <span>恢复默认</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 入营测试引导横幅（可关闭） -->
    <div v-if="showBanner" class="card banner">
      <div class="banner-body">
        <span class="badge red">NEW</span>
        <p>你还没有参加入营能力摸底测试，完成测试将生成你的个性化教学任务。</p>
      </div>
      <div class="banner-actions">
        <button class="btn primary small" @click="goPlacement"><span>去测试</span></button>
        <button class="btn small" @click="dismissBanner"><span>稍后再说</span></button>
      </div>
    </div>

    <!-- 遗忘曲线复习提醒 -->
    <div v-if="reviews.length" class="review-section">
      <h2 class="review-title">遗忘曲线 · 复习提醒</h2>
      <p class="review-tip">根据艾宾浩斯遗忘曲线（1/2/4/7/15/30 天间隔），以下模块需要巩固复习。</p>
      <div class="review-grid">
        <div
          v-for="r in reviews"
          :key="r.module_id"
          class="card review-card"
          :class="{ due: r.due }"
        >
          <div class="rv-head">
            <h3>{{ r.name }}</h3>
            <span class="badge" :class="r.due ? 'red' : 'gold'">
              {{ r.due ? `待复习 ×${r.pending_reviews}` : `下次 ${r.next_interval_days} 天后` }}
            </span>
          </div>
          <p class="rv-info">
            {{ r.due ? `距上次考核通过 ${r.elapsed_days} 天，建议按遗忘曲线复习巩固` : `上次通过 ${r.elapsed_days} 天前，第 ${r.next_interval_days} 天复习` }}
          </p>
          <div class="rv-actions">
            <RouterLink :to="`/modules/${r.code}`" class="btn small">
              <span>去复习</span>
            </RouterLink>
            <button class="btn small" @click="markReviewed(r.code)">
              <span>✓ 已复习打卡</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 学习统计仪表盘 -->
    <template v-if="stats">
      <div class="dash-grid">
        <div class="card dash-card">
          <div class="dash-head">
            <span class="dash-label">学习进度</span>
            <span class="dash-value">{{ stats.chapters.percent }}%</span>
          </div>
          <div class="dash-bar">
            <div class="dash-bar-fill" :style="{ width: stats.chapters.percent + '%' }"></div>
          </div>
          <p class="dash-sub">已完成 {{ stats.chapters.completed }} / {{ stats.chapters.total }} 章</p>
        </div>

        <div class="card dash-card">
          <div class="dash-head">
            <span class="dash-label">摸底测试</span>
            <span class="dash-value">{{ stats.placement.taken ? stats.placement.total_score : '—' }}</span>
          </div>
          <div class="dash-bar full">
            <div class="dash-bar-fill" :style="{ width: (stats.placement.taken ? stats.placement.total_score : 0) + '%' }"></div>
          </div>
          <p class="dash-sub">{{ stats.placement.taken ? '已参加入营摸底' : '尚未参加摸底测试' }}</p>
        </div>

        <div class="card dash-card">
          <div class="dash-head">
            <span class="dash-label">考核认证</span>
            <span class="dash-value">{{ stats.exams.passed_count }}/6</span>
          </div>
          <div class="dash-bar full">
            <div class="dash-bar-fill" :style="{ width: (stats.exams.passed_count / 6 * 100) + '%' }"></div>
          </div>
          <p class="dash-sub">{{ stats.exams.passed_count === 6 ? '全部模块已通过考核 🎉' : '通过考核的模块数' }}</p>
        </div>

        <div class="card dash-card">
          <div class="dash-head">
            <span class="dash-label">练习正确率</span>
            <span class="dash-value">{{ stats.practice.accuracy ?? '—' }}{{ stats.practice.accuracy !== null ? '%' : '' }}</span>
          </div>
          <div class="dash-bar full">
            <div class="dash-bar-fill" :style="{ width: (stats.practice.accuracy ?? 0) + '%' }"></div>
          </div>
          <p class="dash-sub">{{ stats.practice.records ? `已练 ${stats.practice.records} 次 / ${stats.practice.total_questions} 题` : '尚未开始训练' }}</p>
        </div>
      </div>

      <!-- 模块考核状态总览 -->
      <div class="card status-card">
        <h2 class="status-title">模块考核状态</h2>
        <div class="status-grid">
          <div v-for="m in stats.exams.module_status" :key="m.module_id" class="status-row">
            <span class="status-name">{{ m.name }}</span>
            <span v-if="m.exam_taken" class="badge" :class="m.exam_passed ? 'black' : 'red'">
              {{ m.exam_passed ? `已通过 ${m.exam_score} 分` : `未通过 ${m.exam_score} 分` }}
            </span>
            <span v-else class="badge gold">未考核</span>
            <RouterLink :to="`/modules/${m.code}`" class="status-link">进入 →</RouterLink>
          </div>
        </div>
      </div>
    </template>

    <div class="notice">
      <p>🎉 欢迎使用 HR 技能训练营！完成各模块「讲解 → 训练 → 考核」闭环，通过全部 6 个模块考核即可完成全部课程。</p>
    </div>
  </div>
</template>

<style scoped>
.hero {
  position: relative; overflow: hidden;
  background: var(--sov-black);
  color: var(--sov-paper);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-lg);
  padding: 52px 40px;
}
.hero-grid { position: absolute; inset: 0; pointer-events: none; }
.hero-content { position: relative; z-index: 1; max-width: 640px; }
.hero h1 {
  margin: 0 0 14px;
  color: var(--sov-paper);
  font-size: 40px;
  text-transform: uppercase;
  letter-spacing: .01em;
  line-height: 1.15;
}
.hero-sub {
  margin: 0 0 30px;
  color: var(--sov-paper);
  font-weight: 700;
  font-size: 15px;
  letter-spacing: .03em;
  opacity: .85;
  max-width: 52ch;
}
.actions { display: flex; gap: 16px; flex-wrap: wrap; }
.actions .btn { padding: 12px 34px; font-size: 15px; }

/* 几何块面（构成主义，右下角） */
.hero-blocks { position: absolute; right: 30px; bottom: 26px; display: flex; gap: 10px; }
.hero-blocks .blk {
  width: 40px; height: 40px;
  transform: rotate(45deg);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-sm);
}
.hero-blocks .blk.red { background: var(--sov-red); }
.hero-blocks .blk.gold { background: var(--sov-gold); }
.hero-blocks .blk.paper { background: var(--sov-paper); }

.diag-line { margin: 22px 0; width: 100%; }

/* 引导横幅 */
.banner {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 16px 20px; margin-bottom: 20px;
  flex-wrap: wrap;
}
.banner-body { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 240px; }
.banner-body p { margin: 0; font-weight: 700; font-size: 13.5px; }
.banner-actions { display: flex; gap: 10px; }
.btn.small { padding: 7px 16px; font-size: 13px; box-shadow: var(--shadow-sm); }

/* 个性化学习路径（首页） */
.path-card { margin-bottom: 20px; padding: 0; }
.path-card.first-open { border-top: 8px solid var(--sov-red); }
.path-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 22px; cursor: pointer;
  user-select: none;
}
.path-title { display: flex; align-items: center; gap: 10px; }
.path-title h2 { margin: 0; font-size: 17px; }
.path-toggle { font-size: 13px; font-weight: 900; color: var(--sov-brown); }
.path-body { padding: 0 22px 22px; border-top: 2px solid var(--sov-paper); padding-top: 14px; }
.path-tip { margin: 0 0 10px; color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.modal-error { margin: 0 0 10px; color: var(--sov-red); font-size: 13px; font-weight: 900; }
.path-saved {
  display: inline-block; margin: 0 0 10px;
  background: var(--sov-green-dark, #00a074); color: var(--sov-paper);
  font-size: 12.5px; font-weight: 900; border: 3px solid var(--sov-black);
  padding: 3px 10px;
}
.path-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
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
.path-actions { display: flex; gap: 10px; flex-wrap: wrap; }

/* 遗忘曲线复习提醒 */
.review-section { margin-bottom: 20px; }
.review-title { margin: 0 0 4px; font-size: 18px; }
.review-tip { margin: 0 0 14px; color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.review-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }
.review-card { padding: 18px 20px; }
.review-card.due { border-left: 10px solid var(--sov-red); }
.rv-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
.rv-head h3 { margin: 0; font-size: 15.5px; }
.rv-info { margin: 0 0 14px; color: var(--sov-brown); font-size: 13px; font-weight: 700; }
.rv-actions { display: flex; gap: 10px; }

/* 学习统计仪表盘 */
.dash-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px; }
.dash-card { padding: 18px 20px; }
.dash-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 10px; }
.dash-label { font-size: 12.5px; font-weight: 900; text-transform: uppercase; letter-spacing: .08em; color: var(--sov-brown); }
.dash-value { font-size: 26px; font-weight: 900; }
.dash-bar { height: 14px; border: 3px solid var(--sov-black); background: var(--sov-white); }
.dash-bar-fill { height: 100%; background: var(--sov-red); transition: width 300ms linear; }
.dash-sub { margin: 8px 0 0; color: var(--sov-brown); font-size: 12.5px; font-weight: 700; }

.status-card { padding: 22px 24px; margin-bottom: 20px; }
.status-title { margin: 0 0 14px; font-size: 17px; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; }
.status-grid { display: flex; flex-direction: column; gap: 8px; }
.status-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px;
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
}
.status-name { flex: 1; font-weight: 900; font-size: 14px; }
.status-link { font-size: 13px; font-weight: 900; text-transform: uppercase; letter-spacing: .04em; }

.notice {
  padding: 16px 20px;
  background: var(--sov-white);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-md);
}
.notice p { margin: 0; font-weight: 700; color: var(--sov-brown); font-size: 13.5px; }

@media (max-width: 720px) {
  .hero { padding: 34px 22px; }
  .hero h1 { font-size: 28px; }
  .hero-blocks { display: none; }
}
</style>
