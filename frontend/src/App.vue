<script setup>
import { useUserStore } from './stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()
onMounted(() => userStore.tryRestore())
</script>

<template>
  <div class="app-shell">
    <!-- 顶部品牌栏（含安全区适配） -->
    <header class="topbar">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
            <path d="M12 2 21 7v10l-9 5-9-5V7l9-5Z" stroke="currentColor" stroke-width="2.5" />
            <path d="M12 2v20M21 7l-9 5-9-5" stroke="currentColor" stroke-width="1.8" opacity=".7" />
          </svg>
        </span>
        <span class="brand-name">RHINE·HR</span>
      </RouterLink>
    </header>

    <!-- 桌面端顶栏导航 -->
    <nav class="desktop-nav">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/modules">技能模块</RouterLink>
      <RouterLink to="/tasks">教学任务</RouterLink>
    </nav>

    <main class="main">
      <RouterView />
    </main>

    <!-- 移动端底部 Tab 导航（含安全区适配） -->
    <nav class="tabbar">      <RouterLink to="/" class="tab">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>
        </svg>
        <span>首页</span>
      </RouterLink>
      <RouterLink to="/modules" class="tab">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="8" height="8"/><rect x="13" y="3" width="8" height="8"/><rect x="3" y="13" width="8" height="8"/><rect x="13" y="13" width="8" height="8"/>
        </svg>
        <span>技能模块</span>
      </RouterLink>
      <RouterLink to="/tasks" class="tab">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>
        </svg>
        <span>教学任务</span>
      </RouterLink>
    </nav>
  </div>
</template>

<style scoped>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }

/* 顶部品牌栏：紧凑 + 安全区 */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: calc(env(safe-area-inset-top, 0px) + 10px) 16px 10px;
  background: var(--sov-paper);
  border-bottom: 3px solid var(--sov-black);
  position: sticky; top: 0; z-index: 20;
}
.brand { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 3px solid var(--sov-black);
}
.brand-name { font-weight: 900; font-size: 14px; text-transform: uppercase; letter-spacing: .05em; color: var(--sov-black); }

/* 桌面端顶栏导航（≥768px 显示） */
.desktop-nav {
  display: none;
  align-items: center; gap: 2px;
  background: var(--sov-paper);
  border-bottom: 4px solid var(--sov-black);
  padding: 0 24px;
  position: sticky; top: 0; z-index: 15;
}
.desktop-nav a {
  color: var(--sov-black); text-decoration: none;
  padding: 10px 16px; font-size: 14px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .04em;
  border-bottom: 4px solid transparent;
}
.desktop-nav a:hover { color: var(--sov-red); border-bottom-color: var(--sov-gold); }
.desktop-nav a.router-link-active { color: var(--sov-red); border-bottom-color: var(--sov-red); }

.main { flex: 1; padding: 14px; max-width: 1080px; width: 100%; margin: 0 auto; }

/* 移动端底部 Tab（<768px 显示，含安全区） */
.tabbar {
  display: flex;
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 20;
  background: var(--sov-paper);
  border-top: 3px solid var(--sov-black);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
.tab {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 0 6px;
  color: var(--sov-ink-2, #55677a);
  text-decoration: none;
  font-size: 11px; font-weight: 900;
}
.tab.router-link-active { color: var(--sov-red); }

@media (min-width: 768px) {
  .desktop-nav { display: flex; }
  .tabbar { display: none; }
  .main { padding: 24px; }
}
</style>
