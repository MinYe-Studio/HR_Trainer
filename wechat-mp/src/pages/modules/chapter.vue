<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import client from '../../api/client'
import MarkdownBody from '../../components/MarkdownBody.vue'
import { useStudyTimer } from '../../composables/useStudyTimer'

useStudyTimer()

const code = ref('')
const chapterId = ref(0)
const chapter = ref(null)
const moduleName = ref('')
const moduleChapters = ref([])
const completed = ref(false)
const saving = ref(false)
const loading = ref(true)
const error = ref('')

// 翻页式阅读：按段落分页
const pages = ref([])
const pageHasTable = ref([]) // 每页是否含表格（表格页提高翻页阈值，防误触）
const pageIdx = ref(0)
const totalPages = computed(() => pages.value.length)
const isLastPage = computed(() => pageIdx.value === totalPages.value - 1)

function splitPages(content) {
  const isH2 = (b) => /^##\s/.test(b)
  const isHr = (b) => /^-{3,}$/.test(b)
  const INTRO_HEADS = ['案例引入', '带着问题学']

  const pages = []
  let cur = ''
  for (const b of content.split(/\n{2,}/).map((x) => x.trim()).filter(Boolean)) {
    if (isHr(b)) continue
    if (isH2(b)) {
      const isIntro = INTRO_HEADS.some((h) => b.includes(h))
      if (!isIntro && cur) {
        pages.push(cur)
        cur = ''
      }
    }
    cur = cur ? cur + '\n\n' + b : b
  }
  if (cur) pages.push(cur)
  return pages
}

// 检测分页内容是否含 markdown 表格（|---| 分隔行）
function detectTables(pageList) {
  return pageList.map((p) => /^\s*\|.*\|.*\n\s*\|[-:\s|]+\|/m.test(p))
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [ch, mod, prog] = await Promise.all([
      client.get(`/modules/${code.value}/chapters/${chapterId.value}`),
      client.get(`/modules/${code.value}`),
      client.get('/progress'),
    ])
    chapter.value = ch
    moduleName.value = mod.name || ''
    moduleChapters.value = mod.chapters || []
    completed.value = prog.chapter_progress?.[ch.id]?.completed === true
    pages.value = splitPages(ch.content || '')
    pageHasTable.value = detectTables(pages.value)
    pageIdx.value = 0
  } catch (e) {
    error.value = e.response?.data?.detail || '章节加载失败'
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  code.value = options.code || ''
  chapterId.value = Number(options.id) || 0
  load()
})

const nextChapter = computed(() => {
  if (!chapter.value || !moduleChapters.value.length) return null
  const idx = moduleChapters.value.findIndex((c) => c.id === chapter.value.id)
  return idx >= 0 && idx < moduleChapters.value.length - 1
    ? moduleChapters.value[idx + 1]
    : null
})

function go(delta) {
  const next = pageIdx.value + delta
  if (next >= 0 && next < totalPages.value) {
    pageIdx.value = next
    uni.pageScrollTo({ scrollTop: 0, duration: 200 })
  }
}

// 滑动手势翻页：左滑下一页，右滑上一页
// 垂直滑动（滚动页面）不翻页；含表格的页提高横向阈值，防止表格内横滑误翻页
let touchX = null
let touchY = null
function onTouchStart(e) {
  touchX = e.touches[0].clientX
  touchY = e.touches[0].clientY
}
function onTouchEnd(e) {
  if (touchX === null) return
  const dx = e.changedTouches[0].clientX - touchX
  const dy = e.changedTouches[0].clientY - touchY
  // 垂直滑动大于水平：视为页面滚动，不翻页
  if (Math.abs(dy) > Math.abs(dx)) { touchX = null; return }
  // 含表格页：需要更明显的横向滑动才翻页（避免表格内滑动误触）
  const threshold = pageHasTable.value[pageIdx.value] ? 90 : 60
  if (Math.abs(dx) > threshold) {
    if (dx < 0) go(1)
    else go(-1)
  }
  touchX = null
}

async function toggleComplete() {
  saving.value = true
  try {
    const res = await client.post('/progress/complete', {
      chapter_id: chapter.value.id,
      completed: !completed.value,
    })
    completed.value = res.completed
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败'
  } finally {
    saving.value = false
  }
}

function goBack() { uni.navigateBack() }
function goPractice() {
  uni.navigateTo({ url: `/pages/modules/practice?code=${code.value}&id=${chapter.value.id}` })
}
function goNextChapter() {
  if (nextChapter.value) {
    uni.redirectTo({ url: `/pages/modules/chapter?code=${code.value}&id=${nextChapter.value.id}` })
  }
}
function goModule() {
  // 章节页由模块详情 navigateTo 进入，返回一层即详情
  uni.navigateBack({ delta: 1 })
}
</script>

<template>
  <view class="chapter-page">
    <text class="back" @click="goBack">← {{ moduleName || '返回模块' }}</text>

    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <template v-if="chapter">
      <text class="ch-title">{{ chapter.title }}</text>

      <!-- 当前段（支持左右滑动翻页） -->
      <view
        class="card content-card"
        @touchstart="onTouchStart"
        @touchend="onTouchEnd"
      >
        <MarkdownBody :content="pages[pageIdx] || ''" />
      </view>

      <!-- 翻页提示 -->
      <view v-if="totalPages > 1" class="pager">
        <text class="swipe-hint">← 左右滑动翻页 →</text>
        <text class="page-ind">{{ pageIdx + 1 }} / {{ totalPages }}</text>
      </view>

      <!-- 最后一页：操作方块 -->
      <view v-if="isLastPage && totalPages" class="footer-bar">
        <view class="btn" :class="{ primary: !completed, disabled: saving }" @click="toggleComplete">
          <text>{{ saving ? '保存中...' : completed ? '取消完成标记' : '标记已完成' }}</text>
        </view>
        <view class="btn primary" @click="goPractice"><text>本章训练</text></view>
        <view v-if="nextChapter" class="btn" @click="goNextChapter"><text>下一章</text></view>
        <view class="btn" @click="goModule"><text>返回模块</text></view>
      </view>
      <text v-if="isLastPage && completed" class="done-note">✓ 本章已学完</text>
    </template>
  </view>
</template>

<style scoped>
.chapter-page { padding: 14px 14px 40px; }
.back { display: inline-block; margin-bottom: 10px; font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.ch-title { display: block; margin: 0 0 12px; font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }

.content-card { padding: 18px 14px; margin-bottom: 12px; }

/* 翻页提示 */
.pager {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  margin-bottom: 14px;
}
.page-ind { font-size: 13px; font-weight: 900; color: var(--sov-brown); display: block; }
.swipe-hint { font-size: 11.5px; font-weight: 900; color: #93a1b1; display: block; }

/* 最后一页操作按钮 */
.footer-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.footer-bar .btn { width: 100%; padding: 12px 8px; font-size: 13.5px; }
.done-note {
  display: block;
  margin: 10px 0 0; text-align: center;
  font-weight: 900; color: #00a074;
  border: 3px solid var(--sov-black);
  background: var(--sov-paper);
  padding: 8px 14px;
  font-size: 13px;
}
.disabled { opacity: .5; }
</style>
