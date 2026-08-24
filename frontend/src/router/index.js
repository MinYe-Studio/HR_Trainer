import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/modules', name: 'modules', component: () => import('../views/ModulesView.vue') },
  { path: '/modules/:code', name: 'module-detail', component: () => import('../views/ModuleDetailView.vue') },
  { path: '/modules/:code/chapters/:id', name: 'chapter', component: () => import('../views/ChapterView.vue') },
  { path: '/modules/:code/chapters/:id/practice', name: 'practice', component: () => import('../views/PracticeView.vue') },
  { path: '/tasks', name: 'tasks', component: () => import('../views/TasksView.vue') },
  { path: '/placement', name: 'placement-intro', component: () => import('../views/PlacementIntroView.vue') },
  { path: '/placement/test', name: 'placement-test', component: () => import('../views/PlacementTestView.vue') },
  { path: '/placement/result', name: 'placement-result', component: () => import('../views/PlacementResultView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 登录守卫：未登录跳转到登录页
router.beforeEach((to) => {
  const userStore = useUserStore()
  if (to.name !== 'login' && !userStore.token) {
    return { name: 'login' }
  }
  if (to.name === 'login' && userStore.token) {
    return { name: 'home' }
  }
})

export default router
