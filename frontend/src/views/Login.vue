<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '../store'

const router = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const loading = ref(false)
const form = ref({
  username: '',
  password: '',
  display_name: '',
  phone: '',
  invite_code: ''
})

async function handleSubmit() {
  if (!form.value.username || !form.value.password) {
    showToast('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    if (isRegister.value) {
      await authStore.register({ ...form.value })
      showToast({ message: '注册成功，请登录', icon: 'success' })
      isRegister.value = false
    } else {
      await authStore.login(form.value.username, form.value.password)
      showToast({ message: '登录成功', icon: 'success' })
      router.replace('/home')
    }
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-header">
      <div class="login-logo">🏔️</div>
      <h1>景区二消产品搜罗平台</h1>
      <p>搜罗好项目，助力投资决策</p>
    </div>

    <div class="login-form">
      <van-form @submit="handleSubmit">
        <van-field
          v-model="form.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true }]"
          left-icon="user-o"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
          left-icon="lock"
        />
        <van-field
          v-if="isRegister"
          v-model="form.display_name"
          name="display_name"
          label="昵称"
          placeholder="请输入昵称（选填）"
          left-icon="smile-o"
        />
        <van-field
          v-if="isRegister"
          v-model="form.phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号（选填）"
          left-icon="phone-o"
        />

        <div style="margin: 16px">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="请稍候..."
          >
            {{ isRegister ? '注 册' : '登 录' }}
          </van-button>
        </div>

        <div style="text-align: center; margin-top: 8px">
          <van-button size="small" type="primary" plain @click="isRegister = !isRegister">
            {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
          </van-button>
        </div>
      </van-form>
    </div>

    <div class="login-footer">
      <p>首批用户自动获得管理员权限</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px 40px;
}

.login-header {
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}

.login-logo {
  font-size: 64px;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  opacity: 0.85;
}

.login-form {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  padding: 16px 0;
}

.login-footer {
  margin-top: 32px;
  color: rgba(255,255,255,0.7);
  font-size: 12px;
}
</style>
