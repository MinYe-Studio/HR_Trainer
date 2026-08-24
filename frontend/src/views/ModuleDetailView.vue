<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const module = ref(null)
const progress = ref({})
const examInfo = ref(null)
const examLatest = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const mod = await client.get(`/modules/${route.params.code}`)
    module.value = mod
    const [prog, examInf, examLat] = await Promise.all([
      client.get('/progress'),
      client.get(`/modules/${route.params.code}/exam`).catch(() => null),
      client.get(`/exam/latest?module_code=${route.params.code}`).catch(() => null),
    ])
    progress.value = prog.chapter_progress || {}
    examInfo.value = examInf
    examLatest.value = examLat
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
            <h3>{{ ch.title }}</h3>
            <p class="summary">{{ ch.summary }}</p>
          </div>
          <!-- 书签式状态标记（右上角） -->
          <span class="bookmark" :class="{ done: isDone(ch) }">{{ isDone(ch) ? '已完成' : '未学习' }}</span>
        </RouterLink>
      </div>

      <!-- 模块考核卡片 -->
      <div v-if="examInfo" class="card exam-card">
        <div class="exam-top">
          <h2 class="exam-title">模块考核</h2>
          <p class="exam-desc">{{ examInfo.description }}</p>
        </div>
        <div class="exam-meta">
          <span class="mini-badge">随机 {{ examInfo.knowledge_count >= 7 ? 7 : examInfo.knowledge_count }} 知识 + 3 案例</span>
          <span class="mini-badge gold">通过线 {{ examInfo.pass_score }} 分</span>
          <span v-if="examLatest" class="mini-badge" :class="examLatest.passed ? 'done' : 'fail'">
            {{ examLatest.passed ? '已通过' : '未通过' }} {{ examLatest.score }} 分
          </span>
          <span v-else class="mini-badge fail">未考核</span>
        </div>
        <div class="exam-foot">
          <RouterLink :to="`/modules/${module.code}/exam`" class="btn primary">
            <span>{{ examLatest ? '重新考核' : '去考核' }}</span>
          </RouterLink>
        </div>
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
.sec-title.inline { margin: 0 0 6px; display: inline-block; border-bottom: none; padding-bottom: 0; font-size: 20px; }

/* 考核卡片（纵向布局：标题行 / 徽章行 / 底部按钮） */
.exam-card { padding: 16px 18px; margin-top: 22px; display: flex; flex-direction: column; gap: 10px; }
.exam-top { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.exam-title { margin: 0; font-size: 17px; flex-shrink: 0; }
.exam-desc {
  margin: 0;
  color: var(--sov-brown); font-size: 12px; font-weight: 700;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.exam-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.mini-badge {
  display: inline-block;
  padding: 3px 10px;
  border: 2px solid var(--sov-black);
  background: var(--sov-paper);
  font-size: 12px; font-weight: 900;
  color: var(--sov-black);
}
.mini-badge.gold { background: var(--sov-gold); }
.mini-badge.done { background: var(--sov-black); color: var(--sov-paper); }
.mini-badge.fail { background: var(--sov-red); color: var(--sov-paper); }
.exam-foot { display: flex; justify-content: flex-end; }
.exam-foot .btn { padding: 9px 26px; font-size: 14px; }

/* 章节列表 */
.chapters { display: flex; flex-direction: column; gap: 12px; }
.chapter {
  position: relative;
  display: flex; gap: 12px; padding: 14px 14px;
  text-decoration: none; color: inherit;
  transition: transform 100ms linear, box-shadow 100ms linear;
}
.chapter:hover { transform: translate(3px, 3px); box-shadow: var(--shadow-sm); }
.chapter:active { transform: translate(5px, 5px); box-shadow: none; }
/* 章节序号方块（缩小，讲解为主体） */
.ch-no {
  display: flex; align-items: center; justify-content: center;
  width: 30px; flex-shrink: 0;
  font-size: 14px; font-weight: 900;
  background: var(--sov-paper); color: var(--sov-black);
  border: 3px solid var(--sov-black);
}
.ch-no.done { background: var(--sov-black); color: var(--sov-paper); }
.ch-body { flex: 1; min-width: 0; padding-right: 54px; }
.ch-body h3 { margin: 0 0 3px; font-size: 15px; line-height: 1.35; }
.summary { margin: 0; color: var(--sov-brown); font-size: 12.5px; font-weight: 700; }

/* 书签式状态标记（右上角） */
.bookmark {
  position: absolute; top: 0; right: 0;
  padding: 4px 12px;
  background: var(--sov-gold); color: var(--sov-black);
  font-size: 11px; font-weight: 900;
  border-left: 3px solid var(--sov-black);
  border-bottom: 3px solid var(--sov-black);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% calc(100% - 7px), 0 100%);
}
.bookmark.done { background: var(--sov-black); color: var(--sov-paper); }

@media (max-width: 720px) {
  .head-card { padding: 16px 14px; }
  .exam-top { flex-direction: column; align-items: flex-start; gap: 2px; }
  .exam-desc { white-space: normal; }
  .ch-body { padding-right: 48px; }
}
</style>
