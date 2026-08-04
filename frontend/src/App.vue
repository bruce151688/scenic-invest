<script setup>
import { useAuthStore } from './store'
</script>

<template>
  <router-view />
</template>

<style>
:root {
  --van-primary-color: #1989fa;
  --van-nav-bar-background: #1989fa;
  --van-nav-bar-title-text-color: #fff;
  --van-nav-bar-icon-color: #fff;
  --van-nav-bar-text-color: #fff;
  --van-tabbar-item-active-color: #1989fa;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
  background-color: #f7f8fa;
  -webkit-font-smoothing: antialiased;
}

body {
  max-width: 100vw;
  overflow-x: hidden;
}

a {
  color: inherit;
  text-decoration: none;
}

.page-container {
  padding-bottom: 60px;
  min-height: 100vh;
}

.page-content {
  padding: 12px;
}

/* 产品卡片网格 */
.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 12px;
}

/* 安全区域适配 */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .page-container {
    padding-bottom: calc(60px + env(safe-area-inset-bottom));
  }
}
</style>
