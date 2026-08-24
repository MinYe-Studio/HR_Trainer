import { defineStore } from 'pinia'
import client from '../api/client'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
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
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    tryRestore() {
      // 已有 token 时静默校验一次；失败（账号已删除/令牌过期）则清理登录态
      if (this.token) {
        client.get('/auth/me').then((user) => {
          this.user = user
          localStorage.setItem('user', JSON.stringify(user))
        }).catch(() => {
          this.logout()
        })
      }
    },
    async updateNickname(nickname) {
      const user = await client.put('/auth/me', { nickname })
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
      return user
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
