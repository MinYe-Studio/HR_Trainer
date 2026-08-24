<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const module = ref(null)
const progress = ref({})
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [mod, prog] = await Promise.all([
      client.get(`/modules/${route.params.code}`),
      client.get('/progress'),
    ])
    module.value = mod
    progress.value = prog.chapter_progress || {}
  } catch (e) {
    error.value = e.response?.data?.detail || '模块加载失败'
  } finally {
    loading.value = false
  }
})

function isDone(ch) {
  return progress.value[ch.id]?.completed === true
}
</script>

<template>
  <div class="mdetail">
    <RouterLink to="/modules" class="back">← 返回模块列表</RouterLink>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">加载中...</p>

    <template v-if="module">
      <div class="card head-card">
        <div class="head-inner">
          <h1>{{ module.name }}</h1>
          <p class="desc">{{ module.description }}</p>
        </div>
        <div class="meta">
          <span class="badge black">{{ module.chapters.length }} 章</span>
          <span class="badge red">{{ module.chapters.filter(isDone).length }} 已完成</span>
        </div>
      </div>

      <h2 class="sec-title">章节讲解</h2>
      <div class="chapters">
        <RouterLink
          v-for="ch in module.chapters"
          :key="ch.id"
          :to="`/modules/${module.code}/chapters/${ch.id}`"
          class="card chapter"
        >
          <div class="ch-no" :class="{ done: isDone(ch) }">{{ ch.sort_order + 1 }}</div>
          <div class="ch-body">
            <div class="ch-head">
              <h3>{{ ch.title }}</h3>
              <span class="badge" :class="isDone(ch) ? 'black' : 'gold'">
                {{ isDone(ch) ? '已完成' : '未学习' }}
              </span>
            </div>
            <p class="summary">{{ ch.summary }}</p>
          </div>
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 16px; font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; }
.hint { color: var(--sov-brown); font-weight: 700; }

.head-card {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 20px;
  padding: 26px; margin-bottom: 26px; flex-wrap: wrap;
}
.head-inner h1 { margin: 0 0 8px; font-size: 26px; }
.desc { margin: 0; color: var(--sov-brown); font-weight: 700; max-width: 60ch; }
.meta { display: flex; gap: 10px; flex-wrap: wrap; }

.sec-title { margin: 0 0 16px; font-size: 18px; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; }
.chapters { display: flex; flex-direction: column; gap: 14px; }
.chapter {
  display: flex; gap: 16px; padding: 16px 18px;
  text-decoration: none; color: inherit;
  transition: transform 100ms linear, box-shadow 100ms linear;
}
.chapter:hover { transform: translate(3px, 3px); box-shadow: var(--shadow-sm); }
.chapter:active { transform: translate(5px, 5px); box-shadow: none; }
.ch-no {
  display: flex; align-items: center; justify-content: center;
  width: 42px; flex-shrink: 0;
  font-size: 18px; font-weight: 900;
  background: var(--sov-paper); color: var(--sov-black);
  border: 3px solid var(--sov-black);
}
.ch-no.done { background: var(--sov-black); color: var(--sov-paper); }
.ch-body { flex: 1; }
.ch-head { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.ch-head h3 { margin: 0; font-size: 16px; }
.summary { margin: 0; color: var(--sov-brown); font-size: 13.5px; font-weight: 700; }
</style>
