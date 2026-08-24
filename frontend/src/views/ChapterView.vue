<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'
import MarkdownBody from '../components/MarkdownBody.vue'

const route = useRoute()
const router = useRouter()
const code = route.params.code

const chapter = ref(null)
const moduleName = ref('')
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
    completed.value = prog.chapter_progress?.[ch.id]?.completed === true
  } catch (e) {
    error.value = e.response?.data?.detail || '章节加载失败'
  } finally {
    loading.value = false
  }
})

const nextChapterId = computed(() => {
  return null // 下一章导航由模块内章节顺序决定，S7 完善
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
          <span>{{ saving ? '保存中...' : completed ? '取消完成标记' : '标记为已完成' }}</span>
        </button>
        <RouterLink :to="`/modules/${code}/chapters/${chapter.id}/practice`" class="btn primary">
          <span>本章训练 →</span>
        </RouterLink>
        <RouterLink :to="`/modules/${code}`" class="btn">
          <span>返回模块</span>
        </RouterLink>
        <span v-if="completed" class="done-note">✓ 本章已学完</span>
      </div>
    </template>
  </div>
</template>

<style scoped>
.crumbs { margin-bottom: 16px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.content-card { padding: 34px 36px; margin-bottom: 20px; }
.footer-bar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.done-note {
  font-weight: 900; color: var(--sov-green-dark, #00a074);
  border: 3px solid var(--sov-black);
  background: var(--sov-paper);
  padding: 8px 14px;
  font-size: 13px;
}

@media (max-width: 720px) {
  .content-card { padding: 22px 18px; }
}
</style>
