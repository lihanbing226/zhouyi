<template>
  <Teleport to="body">
    <Transition name="sidebar-overlay">
      <div v-if="visible" class="sidebar-overlay" @click="$emit('close')" />
    </Transition>
    <Transition name="sidebar-slide">
      <aside v-if="visible" class="sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">&#9776; 周易</span>
          <button class="close-btn" @click="$emit('close')">&times;</button>
        </div>
        <nav class="sidebar-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="sidebar-link"
            :class="{ active: isActive(item.path) }"
            @click="$emit('close')"
          >
            {{ item.label }}
          </router-link>
        </nav>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

defineProps<{
  visible: boolean
}>()

defineEmits<{
  close: []
}>()

const route = useRoute()

const navItems = [
  { path: '/', label: '首页' },
  { path: '/divination', label: '卜卦问事' },
  { path: '/bazi', label: '八字命盘' },
  { path: '/dashboard', label: '数据看板' },
  { path: '/history', label: '历史记录' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1100;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  background: #111118;
  border-right: 1px solid #2a2a35;
  z-index: 1200;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2a35;
}

.sidebar-title {
  color: #c9a84c;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 2px;
}

.close-btn {
  background: none;
  border: none;
  color: #a09070;
  font-size: 24px;
  cursor: pointer;
  padding: 0 4px;
}

.close-btn:hover {
  color: #e8dcc8;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 4px;
}

.sidebar-link {
  color: #a09070;
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
}

.sidebar-link:hover {
  color: #e8dcc8;
  background: rgba(201, 168, 76, 0.08);
}

.sidebar-link.active {
  color: #c9a84c;
  background: rgba(201, 168, 76, 0.12);
}

/* Transition animations */
.sidebar-overlay-enter-active,
.sidebar-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.sidebar-overlay-enter-from,
.sidebar-overlay-leave-to {
  opacity: 0;
}

.sidebar-slide-enter-active,
.sidebar-slide-leave-active {
  transition: transform 0.3s ease;
}

.sidebar-slide-enter-from,
.sidebar-slide-leave-to {
  transform: translateX(-100%);
}
</style>
