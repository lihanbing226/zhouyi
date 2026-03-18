<template>
  <router-view />
</template>

<script setup lang="ts">
// App 根组件：仅作为 router-view 容器
</script>

<style>
/* 全局基础样式 */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
  background-color: #0a0a0f;
  color: #e8dcc8;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: #c9a84c;
  text-decoration: none;
}

a:hover {
  color: #e8c56a;
}

/* Element Plus 暗色覆盖 */
:root {
  --el-color-primary: #c9a84c;
  --el-color-primary-light-3: #d4b86e;
  --el-color-primary-light-5: #dfc890;
  --el-color-primary-light-7: #eadab2;
  --el-color-primary-light-9: #f5ecd5;
  --el-color-primary-dark-2: #a0863d;
  --el-bg-color: #111118;
  --el-bg-color-page: #0a0a0f;
  --el-bg-color-overlay: #1a1a24;
  --el-text-color-primary: #e8dcc8;
  --el-text-color-regular: #c0b8a8;
  --el-text-color-secondary: #a09070;
  --el-text-color-placeholder: #665e50;
  --el-border-color: #2a2a35;
  --el-border-color-light: #222230;
  --el-fill-color-blank: #111118;
}
</style>
