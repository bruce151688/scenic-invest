<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const categoryId = ref(Number(route.params.id))

const products = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const categoryName = ref('')

onMounted(async () => {
  await loadCategoryName()
  loadProducts()
})

async function loadCategoryName() {
  try {
    const res = await api.get('/api/categories/all')
    const cat = res.items.find(c => c.id === categoryId.value)
    if (cat) categoryName.value = `${cat.icon} ${cat.name}`
  } catch (e) {}
}

async function loadProducts(isRefresh = false) {
  if (loading.value) return
  loading.value = true
  try {
    if (isRefresh) page.value = 1
    const res = await api.get('/api/products', {
      page: page.value,
      page_size: 20,
      category_id: categoryId.value
    })
    if (isRefresh) products.value = res.items
    else products.value.push(...res.items)
    finished.value = products.value.length >= res.total
    page.value++
  } catch (e) {} finally {
    loading.value = false
    refreshing.value = false
  }
}

function onRefresh() { refreshing.value = true; loadProducts(true) }
function onLoad() { if (!finished.value) loadProducts() }
function goDetail(id) { router.push(`/product/${id}`) }
</script>

<template>
  <div class="page-container">
    <van-nav-bar :title="categoryName || '分类产品'" left-text="返回" left-arrow @click-left="router.back()" />

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad" :immediate-check="false">
        <div class="product-grid">
          <ProductCard v-for="p in products" :key="p.id" :product="p" @click="goDetail(p.id)" />
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 12px;
}
</style>
