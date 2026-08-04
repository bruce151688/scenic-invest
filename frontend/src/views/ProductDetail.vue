<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showImagePreview } from 'vant'
import api from '../api'
import ImageGallery from '../components/ImageGallery.vue'
import VideoPlayer from '../components/VideoPlayer.vue'

const route = useRoute()
const router = useRouter()
const productId = ref(Number(route.params.id))

const product = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    product.value = await api.get(`/api/products/${productId.value}`)
  } catch (e) {
    showToast('产品不存在或已删除')
    router.back()
  } finally {
    loading.value = false
  }
})

function previewImages() {
  if (product.value?.images?.length) {
    const urls = product.value.images.map(img =>
      img.url.startsWith('http') ? img.url : `${window.location.origin}/${img.local_path}`
    )
    showImagePreview({ images: urls, closeable: true })
  }
}

function openUrl(url) {
  if (url) window.open(url)
}

function callPhone(phone) {
  if (phone) window.location.href = `tel:${phone}`
}

function copyText(text, label) {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    showToast(`${label}已复制`)
  })
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="产品详情" left-text="返回" left-arrow @click-left="goBack" />

    <van-skeleton title avatar :row="3" :loading="loading">
      <template v-if="product">
        <!-- 图片画廊 -->
        <ImageGallery
          v-if="product.images?.length"
          :images="product.images"
          @click="previewImages"
        />

        <!-- 基本信息 -->
        <div class="detail-section">
          <h1 class="product-title">{{ product.title }}</h1>
          <div class="product-meta">
            <van-tag type="primary" size="medium">{{ product.category_icon }} {{ product.category_name }}</van-tag>
            <van-tag v-if="product.invest_range" type="warning" size="medium" style="margin-left: 6px">
              💰 {{ product.invest_range }}
            </van-tag>
            <span class="view-count">
              <van-icon name="eye-o" /> {{ product.view_count }}
            </span>
          </div>
          <div v-if="product.tags?.length" class="product-tags">
            <van-tag v-for="tag in product.tags" :key="tag" plain type="primary" size="small" style="margin-right: 6px">
              {{ tag }}
            </van-tag>
          </div>
        </div>

        <!-- 位置信息 -->
        <div class="detail-section" v-if="product.location?.province || product.location?.scenic_name">
          <van-cell-group>
            <van-cell title="📍 所在地区" :value="[product.location.province, product.location.city].filter(Boolean).join(' - ') || '未知'" />
            <van-cell v-if="product.location.scenic_name" title="🏞️ 景区名称" :value="product.location.scenic_name" />
            <van-cell v-if="product.invest_range" title="💰 投资区间" :value="product.invest_range" />
            <van-cell v-if="product.price_range" title="💵 产品价格" :value="product.price_range" />
          </van-cell-group>
        </div>

        <!-- 视频播放 -->
        <div class="detail-section" v-if="product.videos?.length">
          <h3 class="section-title">🎬 视频展示</h3>
          <VideoPlayer
            v-for="video in product.videos"
            :key="video.id"
            :video="video"
          />
        </div>

        <!-- 产品描述 -->
        <div class="detail-section" v-if="product.description">
          <h3 class="section-title">📝 产品介绍</h3>
          <div class="product-desc">{{ product.description }}</div>
        </div>

        <!-- 联系方式 -->
        <div class="detail-section" v-if="product.contact_info && Object.values(product.contact_info).some(v => v)">
          <h3 class="section-title">📞 商家联系方式</h3>
          <van-cell-group>
            <van-cell
              v-if="product.contact_info.phone"
              title="电话"
              :value="product.contact_info.phone"
              clickable
              @click="callPhone(product.contact_info.phone)"
              icon="phone-o"
            >
              <template #right-icon>
                <van-button size="small" type="primary" round @click.stop="copyText(product.contact_info.phone, '电话')">
                  复制
                </van-button>
              </template>
            </van-cell>
            <van-cell
              v-if="product.contact_info.wechat"
              title="微信"
              :value="product.contact_info.wechat"
              clickable
              @click="copyText(product.contact_info.wechat, '微信号')"
              icon="chat-o"
            />
            <van-cell
              v-if="product.contact_info.email"
              title="邮箱"
              :value="product.contact_info.email"
              clickable
              @click="copyText(product.contact_info.email, '邮箱')"
              icon="envelope-o"
            />
            <van-cell
              v-if="product.contact_info.website"
              title="官网"
              value="点击访问"
              clickable
              @click="openUrl(product.contact_info.website)"
              icon="link-o"
              is-link
            />
          </van-cell-group>
        </div>

        <!-- 来源 -->
        <div class="detail-section" v-if="product.source_url">
          <h3 class="section-title">🔗 信息来源</h3>
          <van-cell
            :title="product.source_name || '来源网址'"
            label="点击查看原始页面"
            is-link
            @click="openUrl(product.source_url)"
          />
        </div>

        <!-- 时间 -->
        <div class="detail-section detail-footer">
          <span>发布于 {{ new Date(product.created_at).toLocaleDateString('zh-CN') }}</span>
          <span v-if="product.updated_at !== product.created_at">
             · 更新于 {{ new Date(product.updated_at).toLocaleDateString('zh-CN') }}
          </span>
        </div>
      </template>
    </van-skeleton>
  </div>
</template>

<style scoped>
.detail-section {
  background: #fff;
  margin: 10px 12px;
  border-radius: 12px;
  overflow: hidden;
}

.product-title {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  padding: 16px 16px 0;
  color: #1a1a1a;
}

.product-meta {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 6px;
}

.view-count {
  margin-left: auto;
  font-size: 12px;
  color: #969799;
}

.product-tags {
  padding: 0 16px 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  padding: 16px 16px 8px;
  color: #1a1a1a;
}

.product-desc {
  padding: 0 16px 16px;
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}

.detail-footer {
  padding: 16px;
  font-size: 12px;
  color: #969799;
  text-align: center;
  background: transparent;
}
</style>
