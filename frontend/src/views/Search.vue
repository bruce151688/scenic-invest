<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const router = useRouter()

const keyword = ref('')
const products = ref([])
const loading = ref(false)
const finished = ref(false)
const page = ref(1)
const searched = ref(false)

// 筛选条件
const filterCategory = ref(null)
const filterProvince = ref('')
const filterInvest = ref('')

const categories = ref([])
const provinces = ref([
  '北京', '上海', '广东', '浙江', '江苏', '四川', '云南', '海南',
  '广西', '湖南', '湖北', '福建', '山东', '陕西', '河南', '贵州',
  '重庆', '河北', '辽宁', '黑龙江', '安徽', '江西', '山西'
])

onMounted(async () => {
  try {
    const res = await api.get('/api/categories/all')
    categories.value = res.items
  } catch (e) {}
})

async function doSearch(isRefresh = false) {
  if (!keyword.value.trim() && !filterCategory.value && !filterProvince.value && !filterInvest.value) {
    return
  }
  if (loading.value) return
  loading.value = true
  searched.value = true
  try {
    if (isRefresh) page.value = 1
    const res = await api.get('/api/products', {
      page: page.value,
      page_size: 20,
      keyword: keyword.value,
      category_id: filterCategory.value,
      province: filterProvince.value,
      invest_range: filterInvest.value
    })
    if (isRefresh) products.value = res.items
    else products.value.push(...res.items)
    finished.value = products.value.length >= res.total
    page.value++
  } catch (e) {} finally {
    loading.value = false
  }
}

function onSearch() { products.value = []; doSearch(true) }
function onLoad() { if (!finished.value) doSearch() }
function goDetail(id) { router.push(`/product/${id}`) }

const showFilter = ref(false)
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="搜索产品" />

    <div class="search-bar">
      <van-search
        v-model="keyword"
        placeholder="搜索产品名称、描述、景区..."
        shape="round"
        show-action
        @search="onSearch"
      >
        <template #action>
          <div @click="onSearch">搜索</div>
        </template>
      </van-search>
    </div>

    <!-- 快捷筛选 -->
    <div class="quick-filters">
      <van-dropdown-menu>
        <van-dropdown-item v-model="filterCategory" :options="categories.map(c => ({ text: c.icon + ' ' + c.name, value: c.id }))" title="分类" />
        <van-dropdown-item v-model="filterProvince" :options="provinces.map(p => ({ text: p, value: p }))" title="地区" />
        <van-dropdown-item v-model="filterInvest" :options="[
          { text: '全部投资', value: '' },
          { text: '10万以内', value: '0-10万' },
          { text: '10-50万', value: '10-50万' },
          { text: '50-200万', value: '50-200万' },
          { text: '200万以上', value: '200万以上' }
        ]" title="投资" />
      </van-dropdown-menu>
    </div>

    <!-- 结果 -->
    <div class="search-results">
      <van-empty v-if="searched && products.length === 0 && !loading" description="暂无搜索结果，请尝试其他关键词" />
      <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad" :immediate-check="false">
        <div class="product-grid">
          <ProductCard v-for="p in products" :key="p.id" :product="p" @click="goDetail(p.id)" />
        </div>
      </van-list>
    </div>

    <van-tabbar :model-value="2" route>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/category">分类</van-tabbar-item>
      <van-tabbar-item icon="search" to="/search">搜索</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.search-bar { background: #fff; padding: 0 8px; }
.quick-filters { background: #fff; padding-bottom: 8px; }
.search-results { min-height: 200px; }

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 12px;
}
</style>
