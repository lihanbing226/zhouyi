<template>
  <div class="auth-view">
    <div class="auth-card">
      <h2 class="auth-title">{{ isLogin ? '登录' : '注册' }}</h2>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="form.username"
            class="form-input"
            type="text"
            placeholder="请输入用户名"
            :class="{ invalid: errors.username }"
            @input="clearError('username')"
          />
          <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
        </div>

        <div class="form-group" v-if="!isLogin">
          <label class="form-label">邮箱</label>
          <input
            v-model="form.email"
            class="form-input"
            type="email"
            placeholder="请输入邮箱"
            :class="{ invalid: errors.email }"
            @input="clearError('email')"
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            class="form-input"
            type="password"
            placeholder="请输入密码（至少6位）"
            :class="{ invalid: errors.password }"
            @input="clearError('password')"
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <p v-if="serverError" class="error-msg">{{ serverError }}</p>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '请稍候...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <p class="switch-text">
        {{ isLogin ? '还没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="switchMode">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const serverError = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
})

async function loadCurrentUser() {
  const response = await apiClient.get('/auth/me')
  authStore.setUser(response.data)
}

function clearError(field: keyof typeof errors) {
  errors[field] = ''
  serverError.value = ''
}

function validate(): boolean {
  let valid = true

  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    valid = false
  } else if (isLogin.value && form.username.trim().length < 3) {
    errors.username = '用户名至少3个字符'
    valid = false
  } else if (!isLogin.value && form.username.trim().length < 3) {
    errors.username = '用户名至少3个字符'
    valid = false
  }

  if (!isLogin.value) {
    if (!form.email.trim()) {
      errors.email = '请输入邮箱'
      valid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errors.email = '请输入有效的邮箱地址'
      valid = false
    }
  }

  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  } else if (form.password.length < 6) {
    errors.password = '密码至少6位'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (!validate()) return

  serverError.value = ''
  loading.value = true

  try {
    if (isLogin.value) {
      const response = await apiClient.post('/auth/login', {
        username: form.username.trim(),
        password: form.password,
      })
      authStore.setToken(response.data.access_token)
      await loadCurrentUser()
    } else {
      await apiClient.post('/auth/register', {
        username: form.username.trim(),
        email: form.email,
        password: form.password,
      })

      const loginResponse = await apiClient.post('/auth/login', {
        username: form.username.trim(),
        password: form.password,
      })
      authStore.setToken(loginResponse.data.access_token)
      await loadCurrentUser()
    }

    // 重定向到之前的页面或首页
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (err: any) {
    if (err.code === 'ERR_NETWORK') {
      serverError.value = '无法连接到服务器'
    } else {
      serverError.value = err.response?.data?.detail || '操作失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

function switchMode() {
  isLogin.value = !isLogin.value
  serverError.value = ''
  errors.username = ''
  errors.email = ''
  errors.password = ''
  form.password = ''
}
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0f;
  padding: 24px;
}

.auth-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 16px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
}

.auth-title {
  font-size: 28px;
  color: #c9a84c;
  text-align: center;
  margin-bottom: 32px;
  letter-spacing: 4px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  color: #a09070;
}

.form-input {
  background: #0a0a0f;
  border: 1px solid #2a2a35;
  border-radius: 8px;
  padding: 12px 16px;
  color: #e8dcc8;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s ease;
  font-family: inherit;
}

.form-input:focus {
  border-color: #c9a84c;
}

.form-input.invalid {
  border-color: #c0392b;
}

.form-input::placeholder {
  color: #665e50;
}

.field-error {
  color: #c0392b;
  font-size: 12px;
}

.error-msg {
  color: #c0392b;
  font-size: 14px;
  text-align: center;
}

.submit-btn {
  background: linear-gradient(135deg, #c9a84c, #a0863d);
  color: #0a0a0f;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(201, 168, 76, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-text {
  text-align: center;
  color: #a09070;
  font-size: 14px;
  margin-top: 24px;
}

.switch-text a {
  color: #c9a84c;
}

.switch-text a:hover {
  color: #e8c56a;
}
</style>
