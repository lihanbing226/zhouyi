<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="navbar-left">
        <button class="menu-btn" @click="$emit('toggle-sidebar')">
          <span class="menu-icon">&#9776;</span>
        </button>
        <router-link to="/" class="navbar-brand">
          <span class="brand-symbol">&#9776;</span>
          <span class="brand-text">周易</span>
        </router-link>
      </div>

      <div class="navbar-center">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: isActive(item.path) }"
        >
          {{ item.label }}
        </router-link>
      </div>

      <div class="navbar-right">
        <template v-if="authStore.isAuthenticated">
          <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
          <button class="auth-btn" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <router-link to="/auth" class="auth-btn">登录</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineEmits<{
  'toggle-sidebar': []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navItems = [
  { path: '/', label: '首页' },
  { path: '/divination', label: '卜卦' },
  { path: '/bazi', label: '八字' },
  { path: '/dashboard', label: '看板' },
  { path: '/history', label: '历史' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(180deg, #111118 0%, #0d0d14 100%);
  border-bottom: 1px solid #2a2a35;
  z-index: 1000;
}

.navbar-inner {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  color: #e8dcc8;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.brand-symbol {
  font-size: 20px;
  color: #c9a84c;
}

.brand-text {
  font-size: 20px;
  font-weight: 600;
  color: #c9a84c;
  letter-spacing: 2px;
}

.navbar-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  color: #a09070;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #e8dcc8;
  background: rgba(201, 168, 76, 0.08);
}

.nav-link.active {
  color: #c9a84c;
  background: rgba(201, 168, 76, 0.12);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  color: #a09070;
  font-size: 14px;
}

.auth-btn {
  color: #c9a84c;
  background: rgba(201, 168, 76, 0.1);
  border: 1px solid rgba(201, 168, 76, 0.3);
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.auth-btn:hover {
  background: rgba(201, 168, 76, 0.2);
  border-color: #c9a84c;
}

@media (max-width: 768px) {
  .menu-btn {
    display: block;
  }

  .navbar-center {
    display: none;
  }
}
</style>
