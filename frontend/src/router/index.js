import { createRouter, createWebHashHistory } from "vue-router"

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/modules', name: 'modules', component: () => import('../views/ModulesView.vue') },
  { path: '/modules/:code', name: 'module-detail', component: () => import('../views/ModuleDetailView.vue') },
  { path: '/modules/:code/chapters/:id', name: 'chapter', component: () => import('../views/ChapterView.vue') },
  { path: '/modules/:code/chapters/:id/practice', name: 'practice', component: () => import('../views/PracticeView.vue') },
  { path: '/modules/:code/exam', name: 'exam', component: () => import('../views/ExamTakeView.vue') },
  { path: '/modules/:code/exam/result/:id', name: 'exam-result', component: () => import('../views/ExamResultView.vue') },
  { path: '/tasks', name: 'tasks', component: () => import('../views/TasksView.vue') },
  { path: '/placement', name: 'placement-intro', component: () => import('../views/PlacementIntroView.vue') },
  { path: '/placement/test', name: 'placement-test', component: () => import('../views/PlacementTestView.vue') },
  { path: '/placement/result', name: 'placement-result', component: () => import('../views/PlacementResultView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 单机单用户模式：无需登录守卫，登录页直接跳转首页
router.beforeEach((to) => {
  if (to.name === 'login') {
    return { name: 'home' }
  }
})

export default router
