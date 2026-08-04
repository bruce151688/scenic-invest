<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import api from '../api'

const sources = ref([])
const loading = ref(false)
const showAdd = ref(false)
const editingSource = ref(null)

const form = ref({
  name: '', url: '', scraper_type: 'html',
  crawl_frequency_hours: 24, is_active: true, notes: ''
})

onMounted(() => { loadSources() })

async function loadSources() {
  loading.value = true
  try {
    const res = await api.get('/api/sources')
    sources.value = res.items
  } catch (e) {} finally { loading.value = false }
}

function openAdd() {
  editingSource.value = null
  form.value = { name: '', url: '', scraper_type: 'html', crawl_frequency_hours: 24, is_active: true, notes: '' }
  showAdd.value = true
}

function openEdit(source) {
  editingSource.value = source
  form.value = { ...source }
  showAdd.value = true
}

async function saveSource() {
  try {
    if (editingSource.value) {
      await api.put(`/api/sources/${editingSource.value.id}`, form.value)
      showToast('更新成功')
    } else {
      await api.post('/api/sources', form.value)
      showToast('添加成功')
    }
    showAdd.value = false
    loadSources()
  } catch (e) {}
}

async function deleteSource(id) {
  try {
    await showConfirmDialog({ title: '确认删除', message: '删除后将无法恢复，确定继续？' })
    await api.delete(`/api/sources/${id}`)
    showToast('已删除')
    loadSources()
  } catch (e) {}
}

async function triggerCrawl(id) {
  try {
    await api.post(`/api/sources/${id}/crawl`)
    showToast({ message: '已触发抓取，请稍后刷新查看', icon: 'success' })
  } catch (e) {}
}

async function triggerCrawlAll() {
  try {
    await api.post('/api/sources/crawl-all')
    showToast({ message: '已触发全部抓取', icon: 'success' })
  } catch (e) {}
}

function openLogs(sourceId) {
  // Navigate to logs view or show popup
  showToast('日志功能可扩展')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="抓取源管理" left-text="返回" left-arrow @click-left="$router.back()">
      <template #right>
        <van-button size="small" type="primary" @click="triggerCrawlAll">抓取全部</van-button>
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div style="margin-bottom: 12px">
        <van-button block type="primary" @click="openAdd" icon="plus">添加抓取源</van-button>
      </div>

      <van-pull-refresh v-model="loading" @refresh="loadSources">
        <div v-if="sources.length === 0">
          <van-empty description="暂无抓取源，点击上方按钮添加" />
        </div>
        <div v-for="source in sources" :key="source.id" class="source-card">
          <div class="source-header">
            <span class="source-name">{{ source.name }}</span>
            <van-switch v-model="source.is_active" size="20" @change="api.put(`/api/sources/${source.id}`, { is_active: source.is_active })" />
          </div>
          <div class="source-url">{{ source.url }}</div>
          <div class="source-meta">
            <van-tag :type="source.last_crawl_status === 'success' ? 'success' : source.last_crawl_status === 'failed' ? 'danger' : 'default'" size="small">
              {{ source.last_crawl_status === 'success' ? '成功' : source.last_crawl_status === 'failed' ? '失败' : '未抓取' }}
            </van-tag>
            <span v-if="source.last_crawl_at">最近抓取: {{ new Date(source.last_crawl_at).toLocaleString('zh-CN') }}</span>
            <span>{{ source.product_count }}个产品</span>
          </div>
          <div class="source-actions">
            <van-button size="small" type="primary" plain @click="triggerCrawl(source.id)">立即抓取</van-button>
            <van-button size="small" plain @click="openEdit(source)">编辑</van-button>
            <van-button size="small" type="danger" plain @click="deleteSource(source.id)">删除</van-button>
          </div>
        </div>
      </van-pull-refresh>
    </div>

    <!-- 添加/编辑弹窗 -->
    <van-popup v-model:show="showAdd" position="bottom" round :style="{ height: '70%' }">
      <div class="popup-content">
        <h3>{{ editingSource ? '编辑抓取源' : '添加抓取源' }}</h3>
        <van-form @submit="saveSource">
          <van-field v-model="form.name" label="名称" placeholder="如：景区产品网" required />
          <van-field v-model="form.url" label="网址" placeholder="https://example.com/products" required />
          <van-field v-model="form.scraper_type" label="类型" placeholder="html / rss / api" />
          <van-field v-model.number="form.crawl_frequency_hours" label="抓取频率(小时)" type="number" />
          <van-field v-model="form.notes" label="备注" placeholder="选填" type="textarea" rows="2" />
          <div style="margin: 16px">
            <van-button block round type="primary" native-type="submit">保存</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.source-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 10px;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.source-name {
  font-size: 16px;
  font-weight: 600;
}

.source-url {
  font-size: 12px;
  color: #969799;
  word-break: break-all;
  margin-bottom: 8px;
}

.source-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #969799;
  margin-bottom: 12px;
}

.source-actions {
  display: flex;
  gap: 8px;
}

.popup-content {
  padding: 20px 0;
}

.popup-content h3 {
  text-align: center;
  font-size: 18px;
  margin-bottom: 16px;
}
</style>
