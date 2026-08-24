<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'
import MarkdownBody from '../components/MarkdownBody.vue'
import { useStudyTimer } from '../composables/useStudyTimer'

useStudyTimer()

const route = useRoute()
const router = useRouter()
const code = route.params.code

const chapter = ref(null)
const moduleName = ref('')
const moduleChapters = ref([])
const completed = ref(false)
const saving = ref(false)
const loading = ref(true)
const error = ref('')

// 翻页式阅读：按段落分页
const pages = ref([])
const pageIdx = ref(0)
const totalPages = computed(() => pages.value.length)
const isLastPage = computed(() => pageIdx.value === totalPages.value - 1)

function splitPages(content) {
  const isH2 = (b) => /^##\s/.test(b)
  const isHr = (b) => /^-{3,}$/.test(b)
  // 属于"导学页"的标题（并入第一页）
  const INTRO_HEADS = ['案例引入', '带着问题学']

  // 语义分页：首页 = 标题+案例引入+思考+带着问题学；
  // 之后每个「## 知识点/进阶视角/案例复盘/费曼自检」为一页
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

onMounted(async () => {
  try {
    const [ch, mod, prog] = await Promise.all([
      client.get(`/modules/${code}/chapters/${route.params.id}`),
      client.get(`/modules/${code}`),
      client.get('/progress'),
    ])
    chapter.value = ch
    moduleName.value = mod.name || ''
    moduleChapters.value = mod.chapters || []
    completed.value = prog.chapter_progress?.[ch.id]?.completed === true
    pages.value = splitPages(ch.content || '')
    pageIdx.value = 0
  } catch (e) {
    error.value = e.response?.data?.detail || '章节加载失败'
  } finally {
    loading.value = false
  }
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
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 滑动手势翻页：左滑下一页，右滑上一页
let touchX = null
function onTouchStart(e) {
  touchX = e.changedTouches[0].clientX
}
function onTouchEnd(e) {
  if (touchX === null) return
  const dx = e.changedTouches[0].clientX - touchX
  if (Math.abs(dx) > 60) {
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
</script>

<template>
  <div class="chapter-page">
    <div class="crumbs">
      <RouterLink :to="`/modules/${code}`" class="back">← {{ moduleName || '返回模块' }}</RouterLink>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <template v-if="chapter">
      <h1 class="ch-title">{{ chapter.title }}</h1>

      <!-- 当前段（支持左右滑动翻页） -->
      <div
        class="card content-card"
        @touchstart.passive="onTouchStart"
        @touchend.passive="onTouchEnd"
      >
        <MarkdownBody :content="pages[pageIdx] || ''" />
      </div>

      <!-- 翻页提示（纯滑动翻页，无按钮） -->
      <div v-if="totalPages > 1" class="pager">
        <span class="swipe-hint">← 左右滑动翻页 →</span>
        <span class="page-ind">{{ pageIdx + 1 }} / {{ totalPages }}</span>
      </div>

      <!-- 最后一页：操作方块 -->
      <div v-if="isLastPage && totalPages" class="footer-bar">
        <button class="btn" :class="{ primary: !completed }" :disabled="saving" @click="toggleComplete">
          <span>{{ saving ? '保存中...' : completed ? '取消完成标记' : '标记已完成' }}</span>
        </button>
        <RouterLink :to="`/modules/${code}/chapters/${chapter.id}/practice`" class="btn primary">
          <span>本章训练</span>
        </RouterLink>
        <RouterLink v-if="nextChapter" :to="`/modules/${code}/chapters/${nextChapter.id}`" class="btn">
          <span>下一章</span>
        </RouterLink>
        <RouterLink :to="`/modules/${code}`" class="btn">
          <span>返回模块</span>
        </RouterLink>
      </div>
      <p v-if="isLastPage && completed" class="done-note">✓ 本章已学完</p>
    </template>
  </div>
</template>

<style scoped>
.crumbs { margin-bottom: 10px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.ch-title { margin: 0 0 12px; font-size: 20px; }

.content-card { padding: 26px 28px; margin-bottom: 12px; }

/* 翻页提示 */
.pager {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  margin-bottom: 14px;
}
.page-ind { font-size: 13px; font-weight: 900; color: var(--sov-brown); }
.swipe-hint { font-size: 11.5px; font-weight: 900; color: var(--sov-ink-3, #93a1b1); }

/* 最后一页操作按钮（统一方块） */
.footer-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.footer-bar .btn { width: 100%; padding: 12px 8px; font-size: 13.5px; }
.done-note {
  margin: 10px 0 0; text-align: center;
  font-weight: 900; color: var(--sov-green-dark, #00a074);
  border: 3px solid var(--sov-black);
  background: var(--sov-paper);
  padding: 8px 14px;
  font-size: 13px;
}

@media (min-width: 768px) {
  .content-card { padding: 34px 36px; }
  .footer-bar { grid-template-columns: repeat(4, auto); justify-content: start; }
  .footer-bar .btn { width: auto; }
}

@media (max-width: 720px) {
  .content-card { padding: 18px 14px; }
  .ch-title { font-size: 18px; }
}
</style>
