<script setup>
import { onMounted, ref, computed } from 'vue'
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
  } catch (e) {
    error.value = e.response?.data?.detail || '章节加载失败'
  } finally {
    loading.value = false
  }
})

// 下一章导航
const nextChapter = computed(() => {
  if (!chapter.value || !moduleChapters.value.length) return null
  const idx = moduleChapters.value.findIndex((c) => c.id === chapter.value.id)
  return idx >= 0 && idx < moduleChapters.value.length - 1
    ? moduleChapters.value[idx + 1]
    : null
})

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
      <div class="card content-card">
        <MarkdownBody :content="chapter.content" />
      </div>

      <div class="footer-bar">
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
      <p v-if="completed" class="done-note">✓ 本章已学完</p>
    </template>
  </div>
</template>

<style scoped>
.crumbs { margin-bottom: 16px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.content-card { padding: 34px 36px; margin-bottom: 16px; }
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
}
</style>
