import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/components/common/AppLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'divination',
        name: 'Divination',
        component: () => import('@/views/DivinationView.vue'),
        meta: { title: '卜卦', requiresAuth: true },
      },
      {
        path: 'bazi',
        name: 'Bazi',
        component: () => import('@/views/BaziView.vue'),
        meta: { title: '八字命盘', requiresAuth: true },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/HistoryView.vue'),
        meta: { title: '历史记录', requiresAuth: true },
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '数据看板' },
      },
    ],
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/AuthView.vue'),
    meta: { title: '登录', guest: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：受保护路由需要登录
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  document.title = `${to.meta.title || '周易'} - 周易`

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Auth', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
