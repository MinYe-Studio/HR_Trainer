import { defineStore } from 'pinia'
import client, { getLocalProfile } from '../api/client'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 单机单用户：始终登录，档案存本地
    token: 'local',
    user: getLocalProfile(),
  }),
  actions: {
    async login(username, password) {
      const data = await client.post('/auth/login', { username, password })
      this.setAuth(data)
    },
    async register(username, password, nickname) {
      const data = await client.post('/auth/register', { username, password, nickname })
      this.setAuth(data)
    },
    setAuth({ token, user }) {
      this.token = token
      this.user = user
    },
    tryRestore() {
      client.get('/auth/me').then((user) => {
        this.user = user
      }).catch(() => {})
    },
    async updateNickname(nickname) {
      const user = await client.put('/auth/me', { nickname })
      this.user = user
      return user
    },
    logout() {
      // 单机模式：logout 不真正退出，仅保持本地档案
      this.token = 'local'
    },
  },
})
