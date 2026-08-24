<script setup>
import { useUserStore } from './stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()
onMounted(() => userStore.tryRestore())
</script>

<template>
  <div class="app-shell">
    <header v-if="userStore.token" class="topbar">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
            <path d="M12 2 21 7v10l-9 5-9-5V7l9-5Z" stroke="currentColor" stroke-width="2.5" />
            <path d="M12 2v20M21 7l-9 5-9-5" stroke="currentColor" stroke-width="1.8" opacity=".7" />
          </svg>
        </span>
        <span class="brand-name">RHINE·HR</span>
        <span class="brand-sub">训练营</span>
      </RouterLink>
      <nav class="nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/modules">技能模块</RouterLink>
        <RouterLink to="/tasks">教学任务</RouterLink>
      </nav>
      <div class="user-area">
        <span class="nickname">{{ userStore.user?.nickname || userStore.user?.username }}</span>
        <button class="logout" @click="userStore.logout">退出</button>
      </div>
      <!-- 构成主义红色块面分割 -->
      <div class="topbar-stripe"></div>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
.topbar {
  display: flex; align-items: center; gap: 26px;
  padding: 0 28px; height: 62px;
  background: var(--sov-paper);
  border-bottom: 4px solid var(--sov-black);
  position: sticky; top: 0; z-index: 10;
}
/* 底边红色块面（红黑对比） */
.topbar-stripe {
  position: absolute; left: 0; right: 0; bottom: -4px;
  height: 4px; width: 30%;
  background: var(--sov-red);
  pointer-events: none;
}

.brand { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-sm);
}
.brand-name {
  font-weight: 900; font-size: 16px;
  text-transform: uppercase; letter-spacing: .05em;
  color: var(--sov-black);
}
.brand-sub {
  font-size: 12px; font-weight: 900;
  color: var(--sov-red-dark);
  border-left: 4px solid var(--sov-gold);
  padding-left: 10px;
}

.nav { display: flex; gap: 2px; flex: 1; }
.nav a {
  color: var(--sov-black); text-decoration: none;
  padding: 8px 14px; font-size: 14px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .04em;
  border-bottom: 4px solid transparent;
}
.nav a:hover { color: var(--sov-red); border-bottom-color: var(--sov-gold); }
.nav a.router-link-active { color: var(--sov-red); border-bottom-color: var(--sov-red); }

.user-area { display: flex; align-items: center; gap: 14px; }
.nickname { font-size: 13px; font-weight: 900; color: var(--sov-black); }
.logout {
  background: none;
  border: 4px solid var(--sov-black);
  border-radius: 0;
  color: var(--sov-black);
  padding: 4px 12px;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 13px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .04em;
  box-shadow: var(--shadow-sm);
  transition: transform 100ms linear, box-shadow 100ms linear,
    background-color 100ms linear, color 100ms linear;
}
.logout:hover { transform: translate(2px, 2px); box-shadow: none; background: var(--sov-red); color: var(--sov-paper); }
.logout:active { transform: translate(3px, 3px); box-shadow: none; background: var(--sov-black); }

.main { flex: 1; padding: 28px; max-width: 1080px; width: 100%; margin: 0 auto; }

@media (max-width: 720px) {
  .topbar { gap: 10px; padding: 0 14px; }
  .brand-sub { display: none; }
  .nav a { padding: 8px 6px; font-size: 12.5px; }
  .main { padding: 16px; }
}
</style>
