<script setup>
import { useUserStore } from '../stores/user'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'
import { iconOf } from '../utils/icons'

const userStore = useUserStore()
const router = useRouter()
const error = ref('')

// 入营测试引导横幅
const showBanner = ref(false)
const dismissed = sessionStorage.getItem('placement_banner_dismissed') === '1'

// 遗忘曲线复习提醒
const reviews = ref([])

// 学习统计仪表盘
const stats = ref(null)

// 个性化学习路径（默认收起；首次使用前显示 NEW）
const pathCodes = ref([])
const pathExpanded = ref(false)
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
    // 网络异常时静默跳过
  }
})

// 考核通过模块徽章
const passedModules = computed(() => {
  if (!stats.value) return []
  return stats.value.exams.module_status.filter((m) => m.exam_passed)
})

// 时间问候
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

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
  } catch { /* 忽略 */ }
}

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
</script>

<template>
  <div class="home">
    <!-- 黑底方格 Hero（恢复原样式） -->
    <section class="hero">
      <div class="hero-grid grid-pattern on-dark"></div>
      <div class="hero-content">
        <h1>欢迎回来，<br />{{ userStore.user?.nickname || userStore.user?.username }}</h1>
        <p class="hero-sub">系统学习六大 HR 核心技能 · 章节训练巩固 · 模块考核认证</p>
        <div class="actions">
          <RouterLink class="btn primary" to="/modules"><span>开始学习</span></RouterLink>
          <RouterLink class="btn primary" to="/tasks"><span>教学任务</span></RouterLink>
        </div>
        <p v-if="passedModules.length" class="hero-cheer">🎉 已获 <b>{{ passedModules.length }}/6</b> 技能徽章，继续加油！</p>
      </div>
      <!-- 考核通过徽章（右上角） -->
      <div class="hero-badges">
        <div v-for="m in passedModules" :key="m.module_id" class="achievement" :title="m.name">
          <div class="ach-badge" v-html="iconOf(m.code, 22)"></div>
          <span class="ach-check">✓</span>
          <span class="ach-name">{{ m.name }}</span>
        </div>
      </div>
      <!-- 几何块面（右下角） -->
      <div class="hero-blocks">
        <span class="blk red"></span>
        <span class="blk gold"></span>
        <span class="blk paper"></span>
      </div>
    </section>

    <!-- 入营测试引导（紧凑横幅） -->
    <div v-if="showBanner" class="banner card">
      <div class="banner-body">
        <span class="badge red">NEW</span>
        <p>参加入营摸底测试，生成个性化教学任务</p>
      </div>
      <div class="banner-actions">
        <button class="btn primary small" @click="goPlacement"><span>去测试</span></button>
        <button class="btn small" @click="dismissBanner"><span>稍后</span></button>
      </div>
    </div>

    <!-- 2×2 统计 -->
    <div v-if="stats" class="stat-grid">
      <div class="card stat">
        <span class="stat-label">学习进度</span>
        <span class="stat-val">{{ stats.chapters.percent }}%</span>
        <span class="stat-sub">{{ stats.chapters.completed }}/{{ stats.chapters.total }} 章</span>
      </div>
      <div class="card stat">
        <span class="stat-label">考核认证</span>
        <span class="stat-val">{{ stats.exams.passed_count }}/6</span>
        <span class="stat-sub">{{ stats.exams.passed_count === 6 ? '全部通过 🎉' : '模块认证' }}</span>
      </div>
      <div class="card stat">
        <span class="stat-label">练习正确率</span>
        <span class="stat-val">{{ stats.practice.accuracy ?? '—' }}{{ stats.practice.accuracy !== null ? '%' : '' }}</span>
        <span class="stat-sub">{{ stats.practice.records ? `已练 ${stats.practice.records} 次` : '尚未开始' }}</span>
      </div>
      <div class="card stat">
        <span class="stat-label">今日目标</span>
        <span class="stat-val">{{ Math.min(100, Math.round(((stats.study_today.minutes ?? 0) / 30) * 100)) }}%</span>
        <span class="stat-sub">30 分钟/天</span>
      </div>
    </div>

    <!-- 复习提醒（紧凑） -->
    <div v-if="reviews.length" class="section">
      <h2 class="sec-title">复习提醒</h2>
      <div class="review-list">
        <div v-for="r in reviews" :key="r.module_id" class="card review" :class="{ due: r.due }">
          <div class="rv-info">
            <b>{{ r.name }}</b>
            <span>{{ r.due ? `待复习 ×${r.pending_reviews}，建议巩固` : `下次 ${r.next_interval_days} 天后复习` }}</span>
          </div>
          <div class="rv-actions">
            <RouterLink :to="`/modules/${r.code}`" class="btn small"><span>复习</span></RouterLink>
            <button class="btn small" @click="markReviewed(r.code)"><span>✓打卡</span></button>
          </div>
        </div>
      </div>
    </div>

    <!-- 学习路径（折叠） -->
    <div class="section">
      <div class="card path-card" :class="{ 'first-open': pathExpanded }">
        <div class="path-head" @click="pathExpanded = !pathExpanded">
          <div class="path-title">
            <h2>个性化学习路径</h2>
            <span v-if="pathFirstTime && pathExpanded" class="badge red">NEW</span>
          </div>
          <span class="path-toggle">{{ pathExpanded ? '收起 ▾' : '展开 ▸' }}</span>
        </div>
        <div v-show="pathExpanded" class="path-body">
          <p v-if="pathFirstTime" class="path-tip">首次使用：选择你的模块学习顺序（默认：招聘→绩效→薪酬→员工关系→培训→劳动法）。</p>
          <p v-else class="path-tip">调整学习顺序，保存后技能模块页按此展示。</p>
          <p v-if="error" class="modal-error">{{ error }}</p>
          <p v-if="pathSaved" class="path-saved">✓ 已保存</p>
          <div class="path-list">
            <div v-for="(code, i) in pathCodes" :key="code" class="path-row">
              <span class="path-no">{{ i + 1 }}</span>
              <span class="path-name">{{ moduleNames[code] || code }}</span>
              <div class="path-btns">
                <button class="arrow" :disabled="i === 0" @click="pathMove(i, -1)">↑</button>
                <button class="arrow" :disabled="i === pathCodes.length - 1" @click="pathMove(i, 1)">↓</button>
              </div>
            </div>
          </div>
          <div class="path-actions">
            <button class="btn primary small" :disabled="pathSaving" @click="savePath"><span>{{ pathSaving ? '保存中...' : '保存路径' }}</span></button>
            <button v-if="pathFirstTime" class="btn small" @click="skipPath"><span>跳过，用默认</span></button>
            <button class="btn small" :disabled="pathSaving" @click="resetPath"><span>恢复默认</span></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 12px; padding-bottom: 70px; }

/* 黑底方格 Hero */
.hero {
  position: relative; overflow: hidden;
  background: var(--sov-black);
  color: var(--sov-paper);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-lg);
  padding: 26px 22px;
}
.hero-grid { position: absolute; inset: 0; pointer-events: none; }
.hero-content { position: relative; z-index: 1; max-width: 620px; }
.hero h1 {
  margin: 0 0 8px;
  color: var(--sov-paper);
  font-size: 26px;
  text-transform: uppercase;
  letter-spacing: .01em;
  line-height: 1.15;
}
.hero-sub {
  margin: 0 0 16px;
  color: var(--sov-paper);
  font-weight: 700;
  font-size: 13.5px;
  letter-spacing: .03em;
  opacity: .85;
}
.hero-cheer {
  margin: 12px 0 0;
  color: var(--sov-gold);
  font-weight: 900;
  font-size: 13px;
}
.hero-cheer b { color: var(--sov-paper); }
.actions { display: flex; gap: 12px; flex-wrap: wrap; }
.actions .btn { padding: 10px 24px; font-size: 14px; }

.hero-badges {
  position: absolute; top: 14px; right: 16px;
  display: flex; align-items: flex-start; gap: 8px;
  flex-wrap: wrap; justify-content: flex-end;
  max-width: 200px;
}
.achievement { display: flex; flex-direction: column; align-items: center; gap: 3px; position: relative; }
.ach-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 42px; height: 42px;
  background: var(--sov-gold);
  border: 3px solid var(--sov-paper);
  color: var(--sov-black);
  box-shadow: var(--shadow-sm);
  animation: ach-pop .5s ease-out;
}
@keyframes ach-pop {
  0% { transform: scale(0); }
  60% { transform: scale(1.25); }
  100% { transform: scale(1); }
}
.ach-check {
  position: absolute; top: -7px; right: -7px;
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 2px solid var(--sov-paper);
  font-size: 11px; font-weight: 900;
}
.ach-name {
  font-size: 9.5px; font-weight: 900;
  color: var(--sov-paper);
  background: rgba(26, 26, 26, .7);
  border: 2px solid var(--sov-paper);
  padding: 1px 5px;
  white-space: nowrap;
}
.hero-blocks { position: absolute; right: 20px; bottom: 16px; display: flex; gap: 6px; }
.hero-blocks .blk {
  width: 26px; height: 26px;
  transform: rotate(45deg);
  border: 3px solid var(--sov-black);
  box-shadow: var(--shadow-sm);
}
.hero-blocks .blk.red { background: var(--sov-red); }
.hero-blocks .blk.gold { background: var(--sov-gold); }
.hero-blocks .blk.paper { background: var(--sov-paper); }

@media (max-width: 720px) {
  .hero-badges { position: static; max-width: none; justify-content: flex-start; margin-top: 12px; }
  .hero-blocks { display: none; }
}

/* 引导横幅 */
.banner {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 12px 14px; flex-wrap: wrap;
}
.banner-body { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 200px; }
.banner-body p { margin: 0; font-weight: 700; font-size: 13px; }
.banner-actions { display: flex; gap: 8px; }
.btn.small { padding: 6px 14px; font-size: 12.5px; box-shadow: var(--shadow-sm); }

/* 问候主卡 */
.greet-card { padding: 18px 16px; }
.greet-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.greet-time { margin: 0; font-size: 17px; font-weight: 900; }
.greet-sub { margin: 2px 0 0; color: var(--sov-brown); font-size: 12px; font-weight: 700; }
.today-study { display: flex; align-items: baseline; gap: 4px; text-align: right; }
.today-min { font-size: 30px; font-weight: 900; color: var(--sov-red); line-height: 1; }
.today-unit { font-size: 11px; font-weight: 900; color: var(--sov-brown); line-height: 1.2; }
.greet-btn { width: 100%; padding: 12px 0; font-size: 15px; }
.cheer { margin: 10px 0 0; font-size: 12.5px; font-weight: 900; color: var(--sov-gold); }
.cheer b { color: var(--sov-black); }

/* 徽章横滑 */
.badge-row {
  display: flex; gap: 10px; overflow-x: auto;
  padding: 4px 2px;
  -webkit-overflow-scrolling: touch;
}
.ach { display: flex; flex-direction: column; align-items: center; gap: 3px; flex-shrink: 0; }
.ach-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 46px; height: 46px;
  background: var(--sov-gold);
  border: 3px solid var(--sov-paper);
  color: var(--sov-black);
  box-shadow: var(--shadow-sm);
}
.ach-name { font-size: 10px; font-weight: 900; color: var(--sov-ink-2, #55677a); white-space: nowrap; }
.ach-more { display: flex; align-items: center; flex-shrink: 0; font-size: 12px; font-weight: 900; color: var(--sov-red-dark); }

/* 2×2 统计 */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat { padding: 12px 14px; display: flex; flex-direction: column; gap: 2px; }
.stat-label { font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: .06em; color: var(--sov-brown); }
.stat-val { font-size: 24px; font-weight: 900; line-height: 1.1; }
.stat-sub { font-size: 11px; font-weight: 700; color: var(--sov-brown); }

@media (min-width: 768px) {
  .stat-grid { grid-template-columns: repeat(4, 1fr); }
  .home { padding-bottom: 0; }
}

/* 板块标题 */
.section { display: flex; flex-direction: column; gap: 8px; }
.sec-title { margin: 4px 0 0; font-size: 15px; border-bottom: 3px solid var(--sov-black); padding-bottom: 6px; }

/* 复习提醒 */
.review-list { display: flex; flex-direction: column; gap: 8px; }
.review { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 14px; }
.review.due { border-left: 8px solid var(--sov-red); }
.rv-info { display: flex; flex-direction: column; gap: 1px; }
.rv-info b { font-size: 14px; }
.rv-info span { font-size: 11.5px; color: var(--sov-brown); font-weight: 700; }
.rv-actions { display: flex; gap: 6px; }

/* 学习路径 */
.path-card { padding: 0; }
.path-card.first-open { border-top: 6px solid var(--sov-red); }
.path-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 13px 16px; cursor: pointer; user-select: none;
}
.path-title { display: flex; align-items: center; gap: 8px; }
.path-title h2 { margin: 0; font-size: 15px; }
.path-toggle { font-size: 12px; font-weight: 900; color: var(--sov-brown); }
.path-body { padding: 0 16px 14px; border-top: 2px solid var(--sov-paper); padding-top: 10px; }
.path-tip { margin: 0 0 8px; color: var(--sov-brown); font-size: 12px; font-weight: 700; }
.modal-error { margin: 0 0 8px; color: var(--sov-red); font-size: 12px; font-weight: 900; }
.path-saved {
  display: inline-block; margin: 0 0 8px;
  background: var(--sov-green-dark, #00a074); color: var(--sov-paper);
  font-size: 12px; font-weight: 900; border: 2px solid var(--sov-black);
  padding: 2px 8px;
}
.path-list { display: flex; flex-direction: column; gap: 5px; margin-bottom: 10px; }
.path-row { display: flex; align-items: center; gap: 10px; padding: 7px 10px; background: var(--sov-paper); border: 2px solid var(--sov-black); }
.path-no {
  display: inline-flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; flex-shrink: 0;
  background: var(--sov-black); color: var(--sov-paper);
  font-size: 12px; font-weight: 900;
}
.path-name { flex: 1; font-weight: 900; font-size: 13.5px; }
.path-btns { display: flex; gap: 5px; }
.arrow { width: 26px; height: 26px; border: 2px solid var(--sov-black); background: var(--sov-white); font-weight: 900; cursor: pointer; }
.arrow:hover { background: var(--sov-gold); }
.arrow:disabled { opacity: .35; cursor: not-allowed; }
.path-actions { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
