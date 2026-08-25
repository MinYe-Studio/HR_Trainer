<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import client from '../../api/client'

const result = ref(null)
const loading = ref(true)
const error = ref('')

const levelBadge = { focus: 'red', consolidate: 'gold', express: 'black' }
const levelText = { focus: '重点学习', consolidate: '巩固提升', express: '快速通道' }

onLoad(async () => {
  try {
    result.value = await client.get('/placement/latest')
  } catch (e) {
    error.value = e.response?.data?.detail || '结果加载失败'
  } finally {
    loading.value = false
  }
})

function goTasks() {
  uni.navigateTo({ url: '/pages/tasks/index' })
}
function retest() {
  uni.redirectTo({ url: '/pages/placement/test' })
}
</script>

<template>
  <view class="result">
    <text v-if="error" class="error">{{ error }}</text>
    <text v-if="loading" class="hint">加载中...</text>

    <template v-if="result">
      <view class="card total-card">
        <view class="total">
          <text class="total-label">摸底总分</text>
          <text class="total-score">{{ result.total_score }}</text>
          <text class="total-unit">分</text>
        </view>
        <view class="total-actions">
          <view class="btn primary" @click="goTasks"><text>查看教学任务</text></view>
          <view class="btn" @click="retest"><text>重新测试</text></view>
        </view>
      </view>

      <text class="sec-title">各模块得分</text>
      <view class="grid">
        <view v-for="m in result.module_scores" :key="m.module_id" class="card mcard">
          <view class="mhead">
            <text class="mname">{{ m.name }}</text>
            <text class="badge" :class="levelBadge[m.level]">{{ levelText[m.level] }}</text>
          </view>
          <view class="score-row">
            <text class="score">{{ m.score }}</text>
            <text class="score-detail">正确 {{ m.correct }}/{{ m.total }}</text>
          </view>
          <view class="bar">
            <view class="bar-fill" :class="levelBadge[m.level]" :style="{ width: m.score + '%' }"></view>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<style scoped>
.result { padding: 14px 14px 40px; display: flex; flex-direction: column; gap: 14px; }
.error { color: var(--sov-red); font-weight: 900; display: block; }
.hint { color: var(--sov-brown); font-weight: 700; display: block; }

.total-card {
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
  padding: 24px 20px; flex-wrap: wrap;
}
.total { display: flex; align-items: baseline; gap: 8px; }
.total-label {
  font-size: 14px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .1em;
  color: var(--sov-brown);
  margin-right: 8px;
}
.total-score { font-size: 56px; font-weight: 900; line-height: 1; color: var(--sov-red); }
.total-unit { font-size: 18px; font-weight: 900; }
.total-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.sec-title { font-size: 18px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; border-bottom: 4px solid var(--sov-black); padding-bottom: 8px; display: block; }
.grid { display: flex; flex-direction: column; gap: 14px; }
.mcard { padding: 18px; }
.mhead { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 14px; }
.mname { font-size: 16px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; display: block; }
.score-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.score { font-size: 34px; font-weight: 900; display: block; }
.score-detail { font-size: 12px; font-weight: 700; color: var(--sov-brown); display: block; }
.bar { height: 14px; border: 3px solid var(--sov-black); background: var(--sov-white); }
.bar-fill { height: 100%; transition: width 300ms linear; }
.bar-fill.red { background: var(--sov-red); }
.bar-fill.gold { background: var(--sov-gold); }
.bar-fill.black { background: var(--sov-black); }
</style>
