<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import client from '../../api/client'
import ModuleBadge from '../../components/ModuleBadge.vue'
import TabBar from '../../components/TabBar.vue'

const error = ref('')
const showBanner = ref(false)
const dismissed = uni.getStorageSync('placement_banner_dismissed') === '1'
const reviews = ref([])
const stats = ref(null)
const pathCodes = ref([])
const pathExpanded = ref(false)
const pathFirstTime = ref(!uni.getStorageSync('path_prompt_done'))
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

async function load() {
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
    // 静默跳过
  }
}

onShow(load)

// 考核通过模块徽章
const passedModules = computed(() => {
  if (!stats.value) return []
  return stats.value.exams.module_status.filter((m) => m.exam_passed)
})

// 徽章区：只显示已开始学习的模块（≥1 章），未学习不展示
const moduleBadges = computed(() => {
  if (!stats.value) return []
  return stats.value.exams.module_status
    .filter((m) => (m.chapters_completed || 0) >= 1 || m.exam_passed)
    .map((m) => ({
      code: m.code,
      name: m.name,
      chaptersCompleted: m.chapters_completed || 0,
      chaptersTotal: m.chapters_total || 0,
      examPassed: m.exam_passed,
    }))
})

function goPlacement() {
  uni.setStorageSync('placement_banner_dismissed', '1')
  showBanner.value = false
  uni.navigateTo({ url: '/pages/placement/intro' })
}
function dismissBanner() {
  uni.setStorageSync('placement_banner_dismissed', '1')
  showBanner.value = false
}

async function markReviewed(code) {
  try {
    await client.post(`/dashboard/review/${code}/done`)
    const rev = await client.get('/dashboard/review')
    reviews.value = rev.reviews || []
  } catch { /* 忽略 */ }
}

function goModules() { uni.navigateTo({ url: '/pages/modules/list' }) }
function goTasks() { uni.navigateTo({ url: '/pages/tasks/index' }) }
function goModule(code) { uni.navigateTo({ url: `/pages/modules/detail?code=${code}` }) }

function pathMove(idx, dir) {
  const target = idx + dir
  if (target < 0 || target >= pathCodes.value.length) return
  const arr = [...pathCodes.value]
  const t = arr[idx]; arr[idx] = arr[target]; arr[target] = t
  pathCodes.value = arr
  pathSaved.value = false
}

async function savePath() {
  pathSaving.value = true
  try {
    await client.put('/learning-path', { module_codes: pathCodes.value })
    pathSaved.value = true
    pathFirstTime.value = false
    uni.setStorageSync('path_prompt_done', '1')
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    pathSaving.value = false
  }
}

function skipPath() {
  uni.setStorageSync('path_prompt_done', '1')
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
  <view class="home">
    <!-- 黑底方格 Hero -->
    <view class="hero">
      <view class="hero-grid grid-pattern on-dark"></view>
      <view class="hero-content">
        <text class="hero-title">欢迎回来，学员</text>
        <text class="hero-sub">系统学习六大 HR 核心技能 · 章节训练巩固 · 模块考核认证</text>
        <view class="actions">
          <view class="btn primary hero-btn" @click="goModules"><text>开始学习</text></view>
          <view class="btn primary hero-btn" @click="goTasks"><text>教学任务</text></view>
        </view>
        <text v-if="passedModules.length" class="hero-cheer">🎉 已获 {{ passedModules.length }}/6 技能徽章，继续加油！</text>
      </view>
      <!-- 徽章成长区（仅已学习模块） -->
      <view v-if="moduleBadges.length" class="hero-badges">
        <view
          v-for="b in moduleBadges"
          :key="b.code"
          class="achievement"
          @click="goModule(b.code)"
        >
          <ModuleBadge
            :code="b.code"
            :name="b.name"
            :chapters-completed="b.chaptersCompleted"
            :chapters-total="b.chaptersTotal"
            :exam-passed="b.examPassed"
            :size="32"
          />
        </view>
      </view>
      <!-- 几何块面（左下角，竖向排列） -->
      <view class="hero-blocks">
        <view class="blk red"></view>
        <view class="blk gold"></view>
        <view class="blk paper"></view>
      </view>
    </view>

    <!-- 入营测试引导 -->
    <view v-if="showBanner" class="banner card">
      <view class="banner-body">
        <text class="badge red">NEW</text>
        <text class="banner-text">参加入营摸底测试，生成个性化教学任务</text>
      </view>
      <view class="banner-actions">
        <view class="btn primary small" @click="goPlacement"><text>去测试</text></view>
        <view class="btn small" @click="dismissBanner"><text>稍后</text></view>
      </view>
    </view>

    <!-- 2×2 统计 -->
    <view v-if="stats" class="stat-grid">
      <view class="card stat">
        <text class="stat-label">学习进度</text>
        <text class="stat-val">{{ stats.chapters.percent }}%</text>
        <text class="stat-sub">{{ stats.chapters.completed }}/{{ stats.chapters.total }} 章</text>
      </view>
      <view class="card stat">
        <text class="stat-label">考核认证</text>
        <text class="stat-val">{{ stats.exams.passed_count }}/6</text>
        <text class="stat-sub">{{ stats.exams.passed_count === 6 ? '全部通过 🎉' : '模块认证' }}</text>
      </view>
      <view class="card stat">
        <text class="stat-label">练习正确率</text>
        <text class="stat-val">{{ stats.practice.accuracy ?? '—' }}{{ stats.practice.accuracy !== null ? '%' : '' }}</text>
        <text class="stat-sub">{{ stats.practice.records ? `已练 ${stats.practice.records} 次` : '尚未开始' }}</text>
      </view>
      <view class="card stat">
        <text class="stat-label">今日目标</text>
        <text class="stat-val">{{ Math.min(100, Math.round(((stats.study_today.minutes ?? 0) / 30) * 100)) }}%</text>
        <text class="stat-sub">30 分钟/天</text>
      </view>
    </view>

    <!-- 复习提醒 -->
    <view v-if="reviews.length" class="section">
      <text class="sec-title">复习提醒</text>
      <view class="review-list">
        <view v-for="r in reviews" :key="r.module_id" class="card review" :class="{ due: r.due }">
          <view class="rv-info">
            <text class="rv-name">{{ r.name }}</text>
            <text class="rv-desc">{{ r.due ? `待复习 ×${r.pending_reviews}，建议巩固` : `下次 ${r.next_interval_days} 天后复习` }}</text>
          </view>
          <view class="rv-actions">
            <view class="btn small" @click="goModule(r.code)"><text>复习</text></view>
            <view class="btn small" @click="markReviewed(r.code)"><text>✓打卡</text></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 学习路径 -->
    <view class="section">
      <view class="card path-card">
        <view class="path-head" @click="pathExpanded = !pathExpanded">
          <view class="path-title">
            <text class="path-h2">个性化学习路径</text>
            <text v-if="pathFirstTime && pathExpanded" class="badge red">NEW</text>
          </view>
          <text class="path-toggle">{{ pathExpanded ? '收起 ▾' : '展开 ▸' }}</text>
        </view>
        <view v-show="pathExpanded" class="path-body">
          <text v-if="pathFirstTime" class="path-tip">首次使用：选择你的模块学习顺序（默认：招聘→绩效→薪酬→员工关系→培训→劳动法）。</text>
          <text v-else class="path-tip">调整学习顺序，保存后技能模块页按此展示。</text>
          <text v-if="error" class="modal-error">{{ error }}</text>
          <text v-if="pathSaved" class="path-saved">✓ 已保存</text>
          <view class="path-list">
            <view v-for="(code, i) in pathCodes" :key="code" class="path-row">
              <text class="path-no">{{ i + 1 }}</text>
              <text class="path-name">{{ moduleNames[code] || code }}</text>
              <view class="path-btns">
                <view class="arrow" :class="{ disabled: i === 0 }" @click="pathMove(i, -1)"><text>↑</text></view>
                <view class="arrow" :class="{ disabled: i === pathCodes.length - 1 }" @click="pathMove(i, 1)"><text>↓</text></view>
              </view>
            </view>
          </view>
          <view class="path-actions">
            <view class="btn primary small" :class="{ disabled: pathSaving }" @click="savePath">
              <text>{{ pathSaving ? '保存中...' : '保存路径' }}</text>
            </view>
            <view v-if="pathFirstTime" class="btn small" @click="skipPath"><text>跳过，用默认</text></view>
            <view class="btn small" :class="{ disabled: pathSaving }" @click="resetPath"><text>恢复默认</text></view>
          </view>
        </view>
      </view>
    </view>

    <TabBar current="home" />
  </view>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 12px; padding: 14px 14px calc(80px + env(safe-area-inset-bottom)); }

/* 黑底方格 Hero */
.hero {
  position: relative; overflow: hidden;
  background: var(--sov-black);
  color: var(--sov-paper);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-lg);
  padding: 26px 22px;
}
.hero-grid { position: absolute; left: 0; top: 0; right: 0; bottom: 0; }
.hero-content { position: relative; z-index: 1; }
.hero-title {
  display: block;
  margin: 0 0 8px;
  color: var(--sov-paper);
  font-size: 26px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .01em;
  line-height: 1.15;
}
.hero-sub {
  display: block;
  margin: 0 0 16px;
  color: var(--sov-paper);
  font-weight: 700;
  font-size: 13.5px;
  letter-spacing: .03em;
  opacity: .85;
}
.hero-cheer {
  display: block;
  margin: 12px 0 0;
  color: var(--sov-gold);
  font-weight: 900;
  font-size: 13px;
}
.actions { display: flex; gap: 12px; flex-wrap: wrap; }
.hero-btn { padding: 10px 24px; font-size: 14px; }

.hero-badges {
  position: absolute; top: 12px; right: 12px;
  display: flex; align-items: flex-start; gap: 6px;
  flex-wrap: wrap; justify-content: flex-end;
  max-width: 150px;
}
.achievement { display: flex; flex-direction: column; align-items: center; gap: 3px; }
.hero-blocks { position: absolute; right: 18px; bottom: 14px; display: flex; flex-direction: column; gap: 5px; }
.blk {
  width: 22px; height: 22px;
  transform: rotate(45deg);
  border: 3px solid var(--sov-black);
  box-shadow: var(--shadow-sm);
}
.blk.red { background: var(--sov-red); }
.blk.gold { background: var(--sov-gold); }
.blk.paper { background: var(--sov-paper); }

/* 引导横幅 */
.banner {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 12px 14px; flex-wrap: wrap;
}
.banner-body { display: flex; align-items: center; gap: 8px; flex: 1; }
.banner-text { font-weight: 700; font-size: 13px; }
.banner-actions { display: flex; gap: 8px; }

/* 2×2 统计 */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat { padding: 12px 14px; display: flex; flex-direction: column; gap: 2px; }
.stat-label { font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: .06em; color: var(--sov-brown); display: block; }
.stat-val { font-size: 24px; font-weight: 900; line-height: 1.1; display: block; }
.stat-sub { font-size: 11px; font-weight: 700; color: var(--sov-brown); display: block; }

/* 板块标题 */
.section { display: flex; flex-direction: column; gap: 8px; }
.sec-title { margin: 4px 0 0; font-size: 15px; border-bottom: 3px solid var(--sov-black); padding-bottom: 6px; display: block; }

/* 复习提醒 */
.review-list { display: flex; flex-direction: column; gap: 8px; }
.review { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 14px; }
.review.due { border-left: 8px solid var(--sov-red); }
.rv-info { display: flex; flex-direction: column; gap: 1px; }
.rv-name { font-size: 14px; font-weight: 900; display: block; }
.rv-desc { font-size: 11.5px; color: var(--sov-brown); font-weight: 700; display: block; }
.rv-actions { display: flex; gap: 6px; }

/* 学习路径 */
.path-card { padding: 0; }
.path-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 13px 16px;
}
.path-title { display: flex; align-items: center; gap: 8px; }
.path-h2 { font-size: 15px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.path-toggle { font-size: 12px; font-weight: 900; color: var(--sov-brown); }
.path-body { padding: 0 16px 14px; border-top: 2px solid var(--sov-paper); padding-top: 10px; }
.path-tip { display: block; margin: 0 0 8px; color: var(--sov-brown); font-size: 12px; font-weight: 700; }
.modal-error { display: block; margin: 0 0 8px; color: var(--sov-red); font-size: 12px; font-weight: 900; }
.path-saved {
  display: inline-block; margin: 0 0 8px;
  background: #00a074; color: var(--sov-paper);
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
.path-name { flex: 1; font-weight: 900; font-size: 13.5px; display: block; }
.path-btns { display: flex; gap: 5px; }
.arrow {
  width: 30px; height: 30px; border: 2px solid var(--sov-black);
  background: var(--sov-white); font-weight: 900;
  display: inline-flex; align-items: center; justify-content: center;
}
.arrow.disabled { opacity: .35; }
.path-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.disabled { opacity: .5; }
</style>
