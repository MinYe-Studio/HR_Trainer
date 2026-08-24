<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="intro grid-pattern">
    <div class="card intro-card">
      <h1>入营能力摸底测试</h1>
      <p class="lead">六大技能模块 · 每模块随机抽 5 题（题库抽选）· 共 30 题，约 10~15 分钟</p>

      <div class="rules">
        <div class="rule">
          <span class="badge red">重点学习</span>
          <span>得分低于 60 分 → 该模块标记为重点学习</span>
        </div>
        <div class="rule">
          <span class="badge gold">巩固提升</span>
          <span>得分 60~79 分 → 该模块标记为巩固提升</span>
        </div>
        <div class="rule">
          <span class="badge black">快速通道</span>
          <span>得分 80 分及以上 → 该模块标记为快速通道</span>
        </div>
      </div>

      <p class="note">测试结果将为你生成<b>个性化教学任务</b>，测试可随时重新参加。</p>

      <div class="actions">
        <button class="btn primary" @click="router.push('/placement/test')">
          <span>开始测试</span>
        </button>
        <button class="btn" @click="router.push('/')">
          <span>跳过，稍后补测</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.intro {
  min-height: calc(100vh - 116px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px 0;
}
.intro-card {
  width: 520px; max-width: 94vw;
  padding: 36px 32px;
}
h1 { margin: 0 0 6px; font-size: 26px; }
.lead { margin: 0 0 22px; color: var(--sov-brown); font-weight: 700; }
.rules { display: flex; flex-direction: column; gap: 12px; margin-bottom: 22px; }
.rule {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px;
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
  font-size: 14px; font-weight: 700;
}
.note { margin: 0 0 26px; color: var(--sov-brown); font-size: 13.5px; }
.note b { color: var(--sov-black); }
.actions { display: flex; gap: 14px; flex-wrap: wrap; }
.actions .btn { flex: 1; min-width: 160px; }
</style>
