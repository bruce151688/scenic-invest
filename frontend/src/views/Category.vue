<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const categories = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/api/categories')
    categories.value = res.items
  } catch (e) { /* ignore */ }
})

function goCategory(cat) {
  router.push(`/category/${cat.id}`)
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="产品分类" />

    <div class="page-content">
      <div v-for="parent in categories" :key="parent.id" class="category-group">
        <div class="category-title" @click="goCategory(parent)">
          <span class="cat-icon">{{ parent.icon }}</span>
          <span class="cat-name">{{ parent.name }}</span>
          <span class="cat-count">{{ parent.product_count }}个</span>
          <van-icon name="arrow" />
        </div>
        <div class="sub-categories">
          <div
            v-for="child in parent.children"
            :key="child.id"
            class="sub-cat-item"
            @click="goCategory(child)"
          >
            <span class="sub-cat-icon">{{ child.icon }}</span>
            <span class="sub-cat-name">{{ child.name }}</span>
            <span class="sub-cat-count">{{ child.product_count }}</span>
          </div>
        </div>
      </div>
    </div>

    <van-tabbar :model-value="1" route>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/category">分类</van-tabbar-item>
      <van-tabbar-item icon="search" to="/search">搜索</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.category-group {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
}

.category-title {
  display: flex;
  align-items: center;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.cat-icon { font-size: 22px; margin-right: 8px; }
.cat-name { flex: 1; }
.cat-count { font-size: 12px; color: #969799; font-weight: 400; margin-right: 4px; }

.sub-categories {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: #f0f0f0;
}

.sub-cat-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}

.sub-cat-item:active {
  background: #f7f8fa;
}

.sub-cat-icon { font-size: 18px; margin-right: 6px; }
.sub-cat-name { flex: 1; }
.sub-cat-count { font-size: 11px; color: #c8c9cc; }
</style>
