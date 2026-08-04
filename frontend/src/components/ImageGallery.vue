<script setup>
import { ref } from 'vue'
import { Swipe, SwipeItem, Image as VanImage } from 'vant'

const props = defineProps({
  images: {
    type: Array,
    required: true,
    default: () => []
  }
})

defineEmits(['click'])

const currentIndex = ref(0)

function getImageUrl(img) {
  if (!img) return ''
  if (img.url && img.url.startsWith('http')) return img.url
  if (img.url) return `/static/${img.url}`
  if (img.local_path) return `/${img.local_path}`
  return ''
}
</script>

<template>
  <div class="image-gallery">
    <van-swipe
      v-if="images.length > 0"
      :autoplay="3000"
      indicator-color="#1989fa"
      @change="currentIndex = $event"
      lazy-render
    >
      <van-swipe-item v-for="(img, idx) in images" :key="img.id || idx">
        <div class="gallery-slide" @click="$emit('click')">
          <van-image
            :src="getImageUrl(img)"
            fit="cover"
            width="100%"
            height="280"
            :alt="img.alt_text || ''"
          >
            <template #loading>
              <div class="img-loading">
                <van-loading type="spinner" size="24" />
              </div>
            </template>
            <template #error>
              <div class="img-error">📷 图片加载失败</div>
            </template>
          </van-image>
        </div>
      </van-swipe-item>
    </van-swipe>
    <div v-else class="no-image">
      <span>📷</span>
      <p>暂无图片</p>
    </div>
    <div v-if="images.length > 1" class="gallery-indicator">
      {{ currentIndex + 1 }} / {{ images.length }}
    </div>
  </div>
</template>

<style scoped>
.image-gallery {
  position: relative;
  background: #000;
}

.gallery-slide {
  width: 100%;
  height: 280px;
  cursor: pointer;
}

.img-loading, .img-error {
  width: 100%;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
}

.img-error {
  color: #969799;
  font-size: 16px;
  flex-direction: column;
  gap: 8px;
}

.no-image {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #c8c9cc;
  font-size: 48px;
}

.no-image p {
  font-size: 14px;
  margin-top: 8px;
}

.gallery-indicator {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0,0,0,0.55);
  color: #fff;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
}
</style>
