<script setup>
defineProps({
  product: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const defaultImg = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" fill="#f0f0f0"><rect width="400" height="300"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#c8c9cc" font-size="20">暂无图片</text></svg>'
)
</script>

<template>
  <div class="product-card" @click="$emit('click')">
    <div class="card-image">
      <van-image
        v-if="product.cover_image"
        :src="product.cover_image.url || product.cover_image.local_path"
        fit="cover"
        width="100%"
        height="140"
        lazy-load
      >
        <template #error>
          <div class="img-placeholder">📷</div>
        </template>
      </van-image>
      <div v-else class="img-placeholder">📷</div>

      <div class="card-badges">
        <span v-if="product.video_count > 0" class="badge-video">
          <van-icon name="video-o" size="12" /> {{ product.video_count }}
        </span>
        <span v-if="product.image_count > 1" class="badge-img">
          <van-icon name="photo-o" size="12" /> {{ product.image_count }}
        </span>
      </div>
    </div>

    <div class="card-body">
      <h3 class="card-title">{{ product.title }}</h3>

      <div class="card-meta">
        <van-tag size="small" type="primary" v-if="product.category_name">
          {{ product.category_icon }} {{ product.category_name }}
        </van-tag>
        <van-tag size="small" type="warning" v-if="product.invest_range">
          💰 {{ product.invest_range }}
        </van-tag>
      </div>

      <div class="card-footer">
        <span class="card-location" v-if="product.location?.province">
          📍 {{ product.location.province }}
        </span>
        <span class="card-views">
          <van-icon name="eye-o" size="12" /> {{ product.view_count }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: transform 0.15s;
  cursor: pointer;
}

.product-card:active {
  transform: scale(0.97);
}

.card-image {
  position: relative;
  overflow: hidden;
}

.img-placeholder {
  width: 100%;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  font-size: 36px;
  color: #c8c9cc;
}

.card-badges {
  position: absolute;
  bottom: 6px;
  right: 6px;
  display: flex;
  gap: 4px;
}

.badge-video, .badge-img {
  background: rgba(0,0,0,0.55);
  color: #fff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.card-body {
  padding: 10px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #969799;
}

.card-location {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
