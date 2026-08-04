<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { useAuthStore } from '../store'
import api, { setServerURL, getServerURL } from '../api'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({ total_products: 0, today_new: 0, by_category: [] })
const serverUrl = ref(getServerURL())
const showServerInput = ref(false)

onMounted(async () => {
  if (!authStore.isLoggedIn) {
    router.replace('/login')
    return
  }
  try {
    stats.value = await api.get('/api/products/stats/summary')
  } catch (e) {}
})

async function handleLogout() {
  try {
    await showConfirmDialog({ title: '退出登录', message: '确定要退出吗？' })
    authStore.logout()
    router.replace('/login')
  } catch (e) {}
}

function saveServerUrl() {
  let url = serverUrl.value.trim()
  if (url && !url.startsWith('http')) {
    url = 'http://' + url
  }
  if (url && url.endsWith('/')) {
    url = url.slice(0, -1)
  }
  setServerURL(url)
  serverUrl.value = url
  showServerInput.value = false
  showToast({ message: '服务器地址已保存，请重新登录', icon: 'success' })
}

function goSources() {
  router.push('/sources')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="我的" />

    <div class="page-content">
      <!-- 用户信息 -->
      <div class="user-card">
        <div class="user-avatar">{{ (authStore.user?.display_name || authStore.user?.username || 'U')[0].toUpperCase() }}</div>
        <div class="user-info">
          <div class="user-name">{{ authStore.user?.display_name || authStore.user?.username }}</div>
          <div class="user-role">
            <van-tag :type="authStore.isAdmin ? 'danger' : authStore.isEditor ? 'warning' : 'primary'" size="small">
              {{ authStore.isAdmin ? '管理员' : authStore.isEditor ? '编辑' : '观察者' }}
            </van-tag>
          </div>
        </div>
      </div>

      <!-- 数据概览 -->
      <div class="stats-box">
        <div class="stats-row">
          <div class="stats-cell">
            <span class="stats-num">{{ stats.total_products }}</span>
            <span class="stats-label">总产品数</span>
          </div>
          <div class="stats-cell">
            <span class="stats-num">{{ stats.today_new }}</span>
            <span class="stats-label">今日新增</span>
          </div>
        </div>
      </div>

      <!-- 功能菜单 -->
      <van-cell-group>
        <van-cell title="📡 抓取源管理" is-link @click="goSources" label="配置和管理自动抓取的数据源" />
        <van-cell title="🔗 服务器地址" :value="serverUrl || '未设置（默认当前地址）'" @click="showServerInput = true" is-link label="设置后端API服务器地址" />
        <van-cell title="📊 产品统计" is-link label="查看分类统计数据" />
        <van-cell title="⭐ 我的收藏" is-link label="已收藏的产品" />
        <van-cell title="📋 待审核产品" is-link :label="'爬虫抓取的待审核产品'" />
      </van-cell-group>

      <!-- 服务器地址弹窗 -->
      <van-popup v-model:show="showServerInput" position="bottom" round :style="{ height: '40%' }">
        <div class="popup-content" style="padding: 24px">
          <h3 style="text-align:center;margin-bottom:16px">设置服务器地址</h3>
          <p style="font-size:13px;color:#969799;margin-bottom:12px">
            如果API无法连接，请在此设置后端服务器地址。<br/>
            例如：http://192.168.1.100:8000
          </p>
          <van-field v-model="serverUrl" placeholder="例如: http://192.168.1.100:8000" clearable />
          <div style="margin:16px">
            <van-button block round type="primary" @click="saveServerUrl">保存地址</van-button>
          </div>
          <div style="text-align:center">
            <van-button size="small" plain @click="serverUrl='';saveServerUrl()">恢复默认</van-button>
          </div>
        </div>
      </van-popup>

      <div style="margin: 24px 0">
        <van-button block round type="danger" @click="handleLogout">退出登录</van-button>
      </div>

      <div class="app-version">
        <p>景区二消产品搜罗平台 v1.0.0</p>
        <p>Made with ❤️ for Scenic Investment</p>
      </div>
    </div>

    <van-tabbar :model-value="3" route>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/category">分类</van-tabbar-item>
      <van-tabbar-item icon="search" to="/search">搜索</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.user-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #1989fa, #07c160);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
}

.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin-right: 16px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.stats-box {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
}

.stats-row {
  display: flex;
}

.stats-cell {
  flex: 1;
  text-align: center;
  padding: 20px;
}

.stats-cell:first-child {
  border-right: 1px solid #f0f0f0;
}

.stats-num {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1989fa;
}

.stats-label {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

.app-version {
  text-align: center;
  color: #c8c9cc;
  font-size: 12px;
  line-height: 1.8;
}
</style>
