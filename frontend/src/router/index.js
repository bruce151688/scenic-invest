import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/category',
    name: 'Category',
    component: () => import('../views/Category.vue'),
    meta: { title: '分类' }
  },
  {
    path: '/category/:id',
    name: 'CategoryProducts',
    component: () => import('../views/CategoryProducts.vue'),
    meta: { title: '分类产品' }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
    meta: { title: '搜索' }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/ProductDetail.vue'),
    meta: { title: '产品详情' }
  },
  {
    path: '/sources',
    name: 'Sources',
    component: () => import('../views/Sources.vue'),
    meta: { title: '抓取源', needAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '我的' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 景区二消产品搜罗` : '景区二消产品搜罗平台'

  const authStore = useAuthStore()
  if (to.meta.needAuth && !authStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
