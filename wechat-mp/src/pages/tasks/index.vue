<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import client from '../../api/client'
import TabBar from '../../components/TabBar.vue'

const data = ref(null)
const examStatus = ref({})
const loading = ref(true)
const error = ref('')

const levelBadge = { focus: 'red', consolidate: 'gold', express: 'black' }
const levelText = { focus: '重点学习', consolidate: '巩固提升', express: '快速通道' }

onLoad(async () => {
  try {
    const [tasks, st] = await Promise.all([
      client.get('/placement/tasks'),
      client.get('/stats').catch(() => null),
    ])
    data.value = tasks
    const map = {}
    ;(st?.exams?.module_status || []).forEach((m) => {
      map[m.code] = m
    })
    examStatus.value = map
  } catch (e) {
    error.value = e.response?.data?.detail || '任务加载失败'
  } finally {
    loading.value = false
  }
})

function goPlacement() {
  uni.navigateTo({ url: '/pages/placement/intro' })
}
function goModule(code) {
  uni.navigateTo({ url: `/pages/modules/detail?code=${code}` })
}
</script>

<template>
  <view class="tasks">
    <view class="head">
      <text class="head-title">教学任务</text>
      <view class="head-bar red"></view>
    </view>
    <text class="tip">根据你的摸底测试成绩生成的个性化学习任务，按优先级排序。</text>

    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <!-- 未参加测试 -->
    <template v-if="data && !data.has_placement">
      <view class="card cta-card">
        <text class="cta-title">你还没有参加入营能力摸底测试</text>
        <text class="cta-desc">完成摸底测试后，系统将根据你的成绩生成个性化教学任务。</text>
        <view class="btn primary" @click="goPlacement"><text>去参加摸底测试</text></view>
      </view>
    </template>

    <!-- 任务清单 -->
    <template v-if="data && data.has_placement">
      <view class="list">
        <view v-for="t in data.tasks" :key="t.module_id" class="card task">
          <!-- 左侧序号竖条（贯穿整卡） -->
          <view class="order" :class="levelBadge[t.level]"><text>{{ t.order }}</text></view>
          <view class="task-body">
            <!-- 第一行：模块名 + 等级标签 -->
            <view class="task-head">
              <text class="task-name">{{ t.name }}</text>
              <text class="badge lv" :class="levelBadge[t.level]">{{ t.level_label }}</text>
            </view>
            <!-- 第二行：推荐动作 -->
            <text class="action">{{ t.recommended_action }}</text>
            <!-- 第三行：底部信息条 -->
            <view class="task-foot">
              <text class="score">摸底 {{ t.score }} 分</text>
              <text v-if="examStatus[t.code]" class="exam-state" :class="examStatus[t.code].exam_passed ? 'ok' : examStatus[t.code].exam_taken ? 'no' : 'none'">
                {{ examStatus[t.code].exam_passed ? '考核已通过 ✓' : examStatus[t.code].exam_taken ? `考核未通过 ${examStatus[t.code].exam_score}分` : '未考核' }}
              </text>
              <view class="btn mini enter" @click="goModule(t.code)"><text>进入模块</text></view>
            </view>
          </view>
        </view>
      </view>
    </template>

    <TabBar current="tasks" />
  </view>
</template>

<style scoped>
.tasks { padding: 14px 14px calc(80px + env(safe-area-inset-bottom)); display: flex; flex-direction: column; gap: 12px; }
.head { display: flex; align-items: center; gap: 12px; }
.head-title { font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.head-bar { display: inline-block; width: 46px; height: 8px; border: 4px solid var(--sov-black); }
.head-bar.red { background: var(--sov-red); }
.tip { color: var(--sov-brown); font-weight: 700; font-size: 12.5px; display: block; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.cta-card { padding: 26px 20px; display: flex; flex-direction: column; gap: 10px; align-items: center; text-align: center; }
.cta-title { font-size: 18px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.cta-desc { color: var(--sov-brown); font-weight: 700; font-size: 13.5px; }

.list { display: flex; flex-direction: column; gap: 14px; }
.task {
  display: flex;
  padding: 0; /* 内边距由 task-body 负责，让 order 竖条贯穿全卡 */
  align-items: stretch;
  min-height: 132px;
}
/* 左侧序号竖条：贯穿整卡高度 */
.order {
  display: flex; align-items: center; justify-content: center;
  width: 46px; flex-shrink: 0;
  font-size: 22px; font-weight: 900;
  color: var(--sov-paper);
  border-right: 4px solid var(--sov-black);
}
.order.red { background: var(--sov-red); }
.order.gold { background: var(--sov-gold); color: var(--sov-black); }
.order.black { background: var(--sov-black); }

/* 内容区：统一三段式（标题行 / 动作 / 底部信息条） */
.task-body {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column;
  padding: 14px 14px;
  gap: 10px;
}
.task-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px;
  flex-shrink: 0;
}
.task-name {
  flex: 1; min-width: 0;
  font-size: 17px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .02em;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.badge.lv { flex-shrink: 0; border-width: 3px; padding: 2px 10px; }
.action {
  flex: 1;
  color: var(--sov-brown); font-size: 13px; font-weight: 700;
  line-height: 1.5;
  display: block;
}
/* 底部信息条：信息 + 按钮固定一行，垂直居中 */
.task-foot {
  display: flex; align-items: center; justify-content: space-between;
  gap: 8px;
  flex-shrink: 0;
  border-top: 2px solid var(--sov-paper);
  padding-top: 10px;
}
.score {
  font-size: 12px; font-weight: 900;
  background: var(--sov-paper); border: 2px solid var(--sov-black);
  padding: 3px 8px;
  flex-shrink: 0;
}
.exam-state {
  flex: 1; min-width: 0;
  font-size: 12px; font-weight: 900;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.exam-state.ok { color: #00a074; }
.exam-state.no { color: var(--sov-red); }
.exam-state.none { color: var(--sov-brown); }
.btn.mini.enter { flex-shrink: 0; padding: 5px 14px; font-size: 12px; }
</style>
