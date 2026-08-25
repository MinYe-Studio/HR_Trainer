<script setup>
function goTest() {
  uni.navigateTo({ url: '/pages/placement/test' })
}
function goHome() {
  uni.navigateBack()
}
</script>

<template>
  <view class="intro grid-pattern">
    <view class="card intro-card">
      <text class="title">入营能力摸底测试</text>
      <text class="lead">六大技能模块 · 每模块随机抽 5 题（题库抽选）· 共 30 题，约 10~15 分钟</text>

      <view class="rules">
        <view class="rule">
          <text class="badge red">重点学习</text>
          <text>得分低于 60 分 → 该模块标记为重点学习</text>
        </view>
        <view class="rule">
          <text class="badge gold">巩固提升</text>
          <text>得分 60~79 分 → 该模块标记为巩固提升</text>
        </view>
        <view class="rule">
          <text class="badge black">快速通道</text>
          <text>得分 80 分及以上 → 该模块标记为快速通道</text>
        </view>
      </view>

      <text class="note">测试结果将为你生成<text class="nb">个性化教学任务</text>，测试可随时重新参加。</text>

      <view class="actions">
        <view class="btn primary act" @click="goTest"><text>开始测试</text></view>
        <view class="btn act" @click="goHome"><text>跳过，稍后补测</text></view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.intro {
  min-height: 100vh;
  display: flex; align-items: flex-start; justify-content: center;
  padding: 24px 14px;
}
.intro-card {
  width: 100%;
  padding: 28px 22px;
}
.title { display: block; margin: 0 0 6px; font-size: 24px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.lead { display: block; margin: 0 0 20px; color: var(--sov-brown); font-weight: 700; font-size: 13.5px; }
.rules { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.rule {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px;
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
  font-size: 13.5px; font-weight: 700;
}
.note { display: block; margin: 0 0 24px; color: var(--sov-brown); font-size: 13.5px; }
.nb { color: var(--sov-black); font-weight: 900; }
.actions { display: flex; gap: 12px; }
.act { flex: 1; }
</style>
