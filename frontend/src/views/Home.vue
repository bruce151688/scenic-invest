<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const router = useRouter()
const activeTab = ref(0)

const products = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const stats = ref({ total_products: 0, today_new: 0, by_category: [] })

onMounted(() => {
  loadProducts()
  loadStats()
})

async function loadStats() {
  try {
    const res = await api.get('/api/products/stats/summary')
    stats.value = res
  } catch (e) { /* ignore */ }
}

async function loadProducts(isRefresh = false) {
  if (loading.value) return
  loading.value = true
  try {
    if (isRefresh) {
      page.value = 1
    }
    const res = await api.get('/api/products', {
      page: page.value,
      page_size: 20,
      sort_by: activeTab.value === 1 ? 'popular' : 'newest'
    })
    if (isRefresh) {
      products.value = res.items
    } else {
      products.value.push(...res.items)
    }
    finished.value = products.value.length >= res.total
    page.value++
  } catch (e) {
    /* ignore */
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onRefresh() {
  refreshing.value = true
  loadProducts(true)
}

function onLoad() {
  if (!finished.value) {
    loadProducts()
  }
}

function goDetail(id) {
  router.push(`/product/${id}`)
}

function goSearch() {
  router.push('/search')
}
</script>

<template>
  <div class="page-container">
    <!-- 顶部导航 -->
    <van-sticky>
      <van-nav-bar title="景区二消产品搜罗" fixed>
        <template #right>
          <van-icon name="search" size="20" @click="goSearch" />
        </template>
      </van-nav-bar>
    </van-sticky>

    <!-- 统计概览 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-num">{{ stats.total_products }}</span>
        <span class="stat-label">收录产品</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ stats.today_new }}</span>
        <span class="stat-label">今日新增</span>
      </div>
      <div class="stat-item" v-for="cat in stats.by_category?.slice(0, 3)" :key="cat.category">
        <span class="stat-num">{{ cat.count }}</span>
        <span class="stat-label">{{ cat.icon }} {{ cat.category }}</span>
      </div>
    </div>

    <!-- 标签页 -->
    <van-tabs v-model:active="activeTab" @change="loadProducts(true)" sticky offset-top="46">
      <van-tab title="最新产品" />
      <van-tab title="热门浏览" />
    </van-tabs>

    <!-- 产品列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
        :immediate-check="false"
      >
        <div class="product-grid">
          <ProductCard
            v-for="product in products"
            :key="product.id"
            :product="product"
            @click="goDetail(product.id)"
          />
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" route>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/category">分类</van-tabbar-item>
      <van-tabbar-item icon="search" to="/search">搜索</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.stats-bar {
  display: flex;
  overflow-x: auto;
  padding: 12px;
  background: #fff;
  gap: 12px;
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
  padding: 8px 12px;
  background: #f7f8fa;
  border-radius: 8px;
}

.stat-num {
  font-size: 20px;
  font-weight: 700;
  color: #1989fa;
}

.stat-label {
  font-size: 11px;
  color: #969799;
  margin-top: 2px;
  white-space: nowrap;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 12px;
}
</style>
