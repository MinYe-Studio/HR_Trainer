<script setup>
const props = defineProps({
  current: { type: String, default: 'home' }, // home | modules | tasks
})

function go(url) {
  // reLaunch 重置页面栈，避免 tab 页堆叠
  uni.reLaunch({ url })
}
</script>

<template>
  <view class="tabbar safe-bottom">
    <view class="tab" :class="{ active: current === 'home' }" @click="go('/pages/index/index')">
      <text class="tab-ico">⌂</text>
      <text class="tab-label">首页</text>
    </view>
    <view class="tab" :class="{ active: current === 'modules' }" @click="go('/pages/modules/list')">
      <text class="tab-ico">▦</text>
      <text class="tab-label">技能模块</text>
    </view>
    <view class="tab" :class="{ active: current === 'tasks' }" @click="go('/pages/tasks/index')">
      <text class="tab-ico">✓</text>
      <text class="tab-label">教学任务</text>
    </view>
  </view>
</template>

<style scoped>
.tabbar {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 20;
  display: flex;
  background: var(--sov-paper);
  border-top: 3px solid var(--sov-black);
}
.tab {
  flex: 1;
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 0 6px;
  color: #55677a;
  font-size: 11px; font-weight: 900;
}
.tab.active { color: var(--sov-red); }
.tab-ico {
  font-size: 20px;
  font-weight: 900;
  line-height: 1;
  font-style: normal;
}
.tab-label { font-size: 11px; font-weight: 900; }
</style>
