<script setup>
import { ref } from 'vue'

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
})

const showPlayer = ref(false)

const platformLabels = {
  bilibili: 'B站',
  youtube: 'YouTube',
  douyin: '抖音',
  kuaishou: '快手',
  other: '视频'
}

function getPlatformLabel(platform) {
  return platformLabels[platform] || '视频'
}

function getPlatformIcon(platform) {
  const icons = { bilibili: '📺', youtube: '▶️', douyin: '🎵', kuaishou: '📱', other: '🎬' }
  return icons[platform] || '🎬'
}

function openVideo() {
  if (props.video.url) {
    window.open(props.video.url)
  }
}
</script>

<template>
  <div class="video-card" @click="openVideo">
    <div class="video-thumb">
      <div class="play-btn">▶</div>
      <img v-if="video.thumbnail_url" :src="video.thumbnail_url" class="thumb-img" />
      <div v-else class="thumb-placeholder">
        <span>{{ getPlatformIcon(video.platform) }}</span>
      </div>
    </div>
    <div class="video-info">
      <span class="video-platform">{{ getPlatformLabel(video.platform) }}</span>
      <span class="video-title">{{ video.title || '查看视频' }}</span>
      <van-icon name="arrow" size="14" color="#c8c9cc" />
    </div>
  </div>
</template>

<style scoped>
.video-card {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 10px;
  margin: 8px 16px 0;
  cursor: pointer;
}

.video-thumb {
  width: 100px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.play-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  width: 32px;
  height: 32px;
  background: rgba(0,0,0,0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e5e5;
  font-size: 24px;
}

.video-info {
  flex: 1;
  margin-left: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.video-platform {
  font-size: 11px;
  background: #1989fa;
  color: #fff;
  padding: 1px 6px;
  border-radius: 4px;
}

.video-title {
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
</style>
