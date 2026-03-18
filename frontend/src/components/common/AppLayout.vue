<template>
  <div class="app-layout">
    <AppNavbar @toggle-sidebar="sidebarVisible = !sidebarVisible" />
    <div class="layout-body">
      <AppSidebar :visible="sidebarVisible" @close="sidebarVisible = false" />
      <main class="layout-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from './AppNavbar.vue'
import AppSidebar from './AppSidebar.vue'

const sidebarVisible = ref(false)
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-body {
  display: flex;
  flex: 1;
  padding-top: 60px; /* navbar 高度 */
}

.layout-main {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .layout-main {
    padding: 16px;
  }
}
</style>
