<script setup>
import { useUserStore } from '../stores/user'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const userStore = useUserStore()
const router = useRouter()

// 入营测试引导横幅：未参加测试时显示，可关闭（本次会话内不再提示）
const showBanner = ref(false)
const dismissed = sessionStorage.getItem('placement_banner_dismissed') === '1'

onMounted(async () => {
  try {
    const latest = await client.get('/placement/latest')
    showBanner.value = !latest && !dismissed
  } catch {
    // 网络异常时静默跳过引导
  }
})

function goPlacement() {
  sessionStorage.setItem('placement_banner_dismissed', '1')
  router.push('/placement')
}
function dismissBanner() {
  sessionStorage.setItem('placement_banner_dismissed', '1')
  showBanner.value = false
}
</script>

<template>
  <div class="home">
    <!-- 入营测试引导横幅（可关闭） -->
    <div v-if="showBanner" class="card banner">
      <div class="banner-body">
        <span class="badge red">NEW</span>
        <p>你还没有参加入营能力摸底测试，完成测试将生成你的个性化教学任务。</p>
      </div>
      <div class="banner-actions">
        <button class="btn primary small" @click="goPlacement"><span>去测试</span></button>
        <button class="btn small" @click="dismissBanner"><span>稍后再说</span></button>
      </div>
    </div>

    <!-- Hero：纯黑底 + 莱茵生命网格构图 -->
    <section class="hero">
      <div class="hero-grid grid-pattern on-dark"></div>
      <div class="hero-content">
        <h1>欢迎回来，<br />{{ userStore.user?.nickname || userStore.user?.username }}</h1>
        <p class="hero-sub">系统学习六大 HR 核心技能 · 章节训练巩固 · 模块考核认证</p>
        <div class="actions">
          <RouterLink class="btn primary" to="/modules"><span>开始学习</span></RouterLink>
          <RouterLink class="btn primary" to="/tasks"><span>教学任务</span></RouterLink>
        </div>
      </div>
      <!-- 几何块面（右下角） -->
      <div class="hero-blocks">
        <span class="blk red"></span>
        <span class="blk gold"></span>
        <span class="blk paper"></span>
      </div>
    </section>

    <div class="notice">
      <p>🚧 骨架阶段：此页面后续将展示学习进度统计与继续学习入口（S7 实现）。</p>
    </div>
  </div>
</template>

<style scoped>
.hero {
  position: relative; overflow: hidden;
  background: var(--sov-black);
  color: var(--sov-paper);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-lg);
  padding: 52px 40px;
}
.hero-grid { position: absolute; inset: 0; pointer-events: none; }
.hero-content { position: relative; z-index: 1; max-width: 640px; }
.hero h1 {
  margin: 0 0 14px;
  color: var(--sov-paper);
  font-size: 40px;
  text-transform: uppercase;
  letter-spacing: .01em;
  line-height: 1.15;
}
.hero-sub {
  margin: 0 0 30px;
  color: var(--sov-paper);
  font-weight: 700;
  font-size: 15px;
  letter-spacing: .03em;
  opacity: .85;
  max-width: 52ch;
}
.actions { display: flex; gap: 16px; flex-wrap: wrap; }
.actions .btn { padding: 12px 34px; font-size: 15px; }

/* 几何块面（构成主义，右下角） */
.hero-blocks { position: absolute; right: 30px; bottom: 26px; display: flex; gap: 10px; }
.hero-blocks .blk {
  width: 40px; height: 40px;
  transform: rotate(45deg);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-sm);
}
.hero-blocks .blk.red { background: var(--sov-red); }
.hero-blocks .blk.gold { background: var(--sov-gold); }
.hero-blocks .blk.paper { background: var(--sov-paper); }

.diag-line { margin: 22px 0; width: 100%; }

/* 引导横幅 */
.banner {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 16px 20px; margin-bottom: 20px;
  flex-wrap: wrap;
}
.banner-body { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 240px; }
.banner-body p { margin: 0; font-weight: 700; font-size: 13.5px; }
.banner-actions { display: flex; gap: 10px; }
.btn.small { padding: 7px 16px; font-size: 13px; box-shadow: var(--shadow-sm); }

.notice {
  padding: 16px 20px;
  background: var(--sov-white);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-md);
}
.notice p { margin: 0; font-weight: 700; color: var(--sov-brown); font-size: 13.5px; }

@media (max-width: 720px) {
  .hero { padding: 34px 22px; }
  .hero h1 { font-size: 28px; }
  .hero-blocks { display: none; }
}
</style>
