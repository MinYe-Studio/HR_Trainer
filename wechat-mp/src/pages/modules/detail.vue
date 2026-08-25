<script setup>
import { computed, ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import client from '../../api/client'
import ModuleBadge from '../../components/ModuleBadge.vue'

const module = ref(null)
const progress = ref({})
const examInfo = ref(null)
const examLatest = ref(null)
const loading = ref(true)
const error = ref('')
const code = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const mod = await client.get(`/modules/${code.value}`)
    module.value = mod
    const [prog, examInf, examLat] = await Promise.all([
      client.get('/progress'),
      client.get(`/modules/${code.value}/exam`).catch(() => null),
      client.get(`/exam/latest?module_code=${code.value}`).catch(() => null),
    ])
    progress.value = prog.chapter_progress || {}
    examInfo.value = examInf
    examLatest.value = examLat
  } catch (e) {
    error.value = e.response?.data?.detail || '模块加载失败'
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  code.value = options.code || ''
  load()
})
// 从章节/训练返回时刷新完成状态
onShow(() => { if (module.value) load() })

function isDone(ch) {
  return progress.value[ch.id]?.completed === true
}

// 徽章成长状态
const badgeState = computed(() => {
  const chs = module.value?.chapters || []
  return {
    code: code.value,
    name: module.value?.name || '',
    chaptersCompleted: chs.filter(isDone).length,
    chaptersTotal: chs.length,
    examPassed: !!examLatest.value?.passed,
  }
})

function goBack() { uni.navigateBack() }
function goChapter(ch) {
  uni.navigateTo({ url: `/pages/modules/chapter?code=${code.value}&id=${ch.id}` })
}
function goExam() {
  uni.navigateTo({ url: `/pages/modules/exam?code=${code.value}` })
}
</script>

<template>
  <view class="mdetail">
    <text class="back" @click="goBack">← 返回模块列表</text>

    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <template v-if="module">
      <view class="card head-card">
        <ModuleBadge
          class="head-badge"
          :code="badgeState.code"
          :name="badgeState.name"
          :chapters-completed="badgeState.chaptersCompleted"
          :chapters-total="badgeState.chaptersTotal"
          :exam-passed="badgeState.examPassed"
          :size="64"
        />
        <view class="head-inner">
          <text class="mod-name">{{ module.name }}</text>
          <text class="desc">{{ module.description }}</text>
        </view>
        <view class="meta">
          <text class="badge black">{{ module.chapters.length }} 章</text>
          <text class="badge red">{{ module.chapters.filter(isDone).length }} 已完成</text>
        </view>
      </view>

      <text class="sec-title">章节讲解</text>
      <view class="chapters">
        <view
          v-for="ch in module.chapters"
          :key="ch.id"
          class="card chapter"
          @click="goChapter(ch)"
        >
          <view class="ch-no" :class="{ done: isDone(ch) }"><text>{{ ch.sort_order + 1 }}</text></view>
          <view class="ch-body">
            <text class="ch-title">{{ ch.title }}</text>
            <text class="summary">{{ ch.summary }}</text>
          </view>
          <!-- 书签式状态标记 -->
          <text class="bookmark" :class="{ done: isDone(ch) }">{{ isDone(ch) ? '已完成' : '未学习' }}</text>
        </view>
      </view>

      <!-- 模块考核卡片 -->
      <view v-if="examInfo" class="card exam-card">
        <view class="exam-top">
          <text class="exam-title">模块考核</text>
          <text class="exam-desc">{{ examInfo.description }}</text>
        </view>
        <view class="exam-meta">
          <text class="mini-badge">随机 {{ examInfo.knowledge_count >= 7 ? 7 : examInfo.knowledge_count }} 知识 + 3 案例</text>
          <text class="mini-badge gold">通过线 {{ examInfo.pass_score }} 分</text>
          <text v-if="examLatest" class="mini-badge" :class="examLatest.passed ? 'done' : 'fail'">
            {{ examLatest.passed ? '已通过' : '未通过' }} {{ examLatest.score }} 分
          </text>
          <text v-else class="mini-badge fail">未考核</text>
        </view>
        <view class="exam-foot">
          <view class="btn primary" @click="goExam"><text>{{ examLatest ? '重新考核' : '去考核' }}</text></view>
        </view>
      </view>
    </template>
  </view>
</template>

<style scoped>
.mdetail { display: flex; flex-direction: column; gap: 12px; padding: 14px 14px 40px; }
.back { font-weight: 900; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.head-card {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 20px; flex-wrap: wrap;
}
.head-badge { flex-shrink: 0; }
.head-inner { flex: 1; min-width: 160px; }
.mod-name { display: block; font-size: 22px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; margin: 0 0 6px; }
.desc { display: block; color: var(--sov-brown); font-weight: 700; font-size: 13px; }
.meta { display: flex; gap: 8px; flex-wrap: wrap; }

.sec-title { font-size: 18px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; display: block; }

/* 章节列表 */
.chapters { display: flex; flex-direction: column; gap: 12px; }
.chapter {
  position: relative;
  display: flex; gap: 12px; padding: 14px 14px;
}
.ch-no {
  display: flex; align-items: center; justify-content: center;
  width: 30px; flex-shrink: 0;
  font-size: 14px; font-weight: 900;
  background: var(--sov-paper); color: var(--sov-black);
  border: 3px solid var(--sov-black);
}
.ch-no.done { background: var(--sov-red); color: var(--sov-paper); }
.ch-body { flex: 1; min-width: 0; padding-right: 54px; display: flex; flex-direction: column; gap: 3px; }
.ch-title { font-size: 15px; font-weight: 900; line-height: 1.35; }
.summary { color: var(--sov-brown); font-size: 12.5px; font-weight: 700; display: block; }

/* 书签式状态标记 */
.bookmark {
  position: absolute; top: 0; right: 0;
  padding: 4px 12px;
  background: var(--sov-gold); color: var(--sov-black);
  font-size: 11px; font-weight: 900;
  border-left: 3px solid var(--sov-black);
  border-bottom: 3px solid var(--sov-black);
}
.bookmark.done { background: var(--sov-red); color: var(--sov-paper); }

/* 考核卡片 */
.exam-card { padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; }
.exam-top { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.exam-title { font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; flex-shrink: 0; }
.exam-desc {
  color: var(--sov-brown); font-size: 12px; font-weight: 700;
  overflow: hidden; text-overflow: ellipsis;
  display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical;
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
</style>
