<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const mode = ref('login') // login | register
const username = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const notice = ref(localStorage.getItem('auth_message') || '')
const loading = ref(false)

if (notice.value) {
  localStorage.removeItem('auth_message')
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await userStore.login(username.value, password.value)
    } else {
      await userStore.register(username.value, password.value, nickname.value)
    }
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap grid-pattern">
    <!-- 莱茵生命网格构图：直条色块点缀（无旋转） -->
    <div class="accent accent-red"></div>
    <div class="accent accent-gold"></div>
    <div class="accent accent-black"></div>

    <div class="login-card card">
      <div class="brand-head">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none">
            <path d="M12 2 21 7v10l-9 5-9-5V7l9-5Z" stroke="currentColor" stroke-width="2.5" />
            <path d="M12 2v20M21 7l-9 5-9-5" stroke="currentColor" stroke-width="1.8" opacity=".7" />
          </svg>
        </div>
        <div>
          <h1>RHINE·HR 训练营</h1>
          <p class="subtitle">讲解 · 训练 · 考核 一体化学习平台</p>
        </div>
      </div>

      <div class="tabs">
        <button
          type="button"
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'"
        >登录</button>
        <button
          type="button"
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'"
        >注册</button>
      </div>

      <form @submit.prevent="submit">
        <input class="input" v-model="username" placeholder="用户名" required autocomplete="username" />
        <input v-if="mode === 'register'" class="input" v-model="nickname" placeholder="昵称（可选）" />
        <input class="input" v-model="password" type="password" placeholder="密码（至少6位）" required :minlength="6" autocomplete="current-password" />
        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn primary submit" :disabled="loading">
          <span>{{ loading ? '请稍候...' : mode === 'login' ? '登 录' : '注册并登录' }}</span>
        </button>
      </form>

      <p class="foot-note">新用户注册后将进行入营能力摸底测试，为你生成个性化教学任务</p>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: calc(100vh - 48px);
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  padding: 24px;
}
/* 网格对齐的直条色块（莱茵生命构图，无旋转） */
.accent { position: absolute; }
.accent-red {
  top: 14%; left: 12%;
  width: 72px; height: 10px;
  background: var(--sov-red);
  border: 4px solid var(--sov-black);
}
.accent-gold {
  top: 20%; left: 12%;
  width: 36px; height: 10px;
  margin-left: 40px;
  background: var(--sov-gold);
  border: 4px solid var(--sov-black);
}
.accent-black {
  bottom: 18%; right: 12%;
  width: 84px; height: 10px;
  background: var(--sov-black);
}

.login-card {
  width: 420px; max-width: 94vw;
  padding: 34px 30px;
  position: relative; z-index: 1;
}
.brand-head { display: flex; align-items: center; gap: 14px; margin-bottom: 26px; }
.brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 50px; height: 50px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 4px solid var(--sov-black);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}
h1 { margin: 0; font-size: 20px; }
.subtitle { margin: 3px 0 0; font-size: 12.5px; font-weight: 700; color: var(--sov-brown); }

.tabs { display: flex; gap: 10px; margin-bottom: 22px; }
.tabs button {
  flex: 1; padding: 10px 0;
  border: 4px solid var(--sov-black);
  border-radius: 0;
  background: var(--sov-paper);
  cursor: pointer;
  color: var(--sov-black);
  font-family: var(--font-sans);
  font-size: 14px; font-weight: 900;
  text-transform: uppercase; letter-spacing: .08em;
  box-shadow: var(--shadow-sm);
  transition: transform 100ms linear, box-shadow 100ms linear,
    background-color 100ms linear, color 100ms linear;
}
.tabs button:hover { transform: translate(2px, 2px); box-shadow: none; }
.tabs button.active {
  background: var(--sov-red);
  color: var(--sov-paper);
  box-shadow: var(--shadow-md);
}
.tabs button.active:active { background: var(--sov-black); color: var(--sov-red); box-shadow: none; transform: translate(3px, 3px); }

form { display: flex; flex-direction: column; gap: 14px; }
.notice {
  margin: 0;
  color: var(--sov-red-dark);
  background: var(--sov-paper);
  border: 3px solid var(--sov-red);
  padding: 10px 12px;
  font-size: 13px; font-weight: 900;
}
.error { color: var(--sov-red); font-size: 13px; margin: 0; font-weight: 900; }
.submit { width: 100%; padding: 12px 0; font-size: 15px; letter-spacing: .14em; }
.foot-note {
  margin: 20px 0 0; font-size: 12px; font-weight: 700;
  color: var(--sov-brown);
  text-align: center; line-height: 1.6;
}
</style>
