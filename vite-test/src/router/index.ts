import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import BooksView from '@/views/BooksView.vue'
import LoginView from '@/views/LoginView.vue'
import TestView from '@/views/TestView.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/books',
      name: 'books',
      component: BooksView
    },
    {
      path: '/bookshelf',
      name: 'bookshelf',
      component: () => import('@/views/UserBooksView.vue')
    },
    {
      path: '/books/:isbn',
      name: 'book-detail',
      component: () => import('@/views/BookDetailView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/admin/books',
      name: 'admin-books',
      component: () => import('@/views/admin/BooksView.vue')
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/UsersView.vue')
    },
    {
      path: '/admin/register',
      name: 'admin-register',
      component: () => import('@/views/admin/RegisterView.vue')
    },
    {
      path: '/admin/users/edit/:id',
      name: 'admin-edit-user',
      component: () => import('@/views/admin/EditUserView.vue')
    },
    {
      path: '/test',
      name: 'test',
      component: TestView
    }
  ]
})

import { useUserStore } from '@/stores/user'

// 需要认证的路由
const authRoutes = [
  '/books/:isbn',
  '/admin/books',
  '/admin/users',
  '/admin/register',
  '/admin/users/edit/:id'
]

// 防止重复导航
let isNavigating = false

router.beforeEach(async (to, _from, next) => {
  if (isNavigating) {
    return next(false)
  }
  isNavigating = true

  const userStore = useUserStore()
  
  // 检查是否需要认证
  const requiresAuth = authRoutes.some(route => {
    const regex = new RegExp('^' + route.replace(/:\w+/g, '\\w+') + '$')
    return regex.test(to.path)
  })

  if (requiresAuth) {
    // 验证token有效性
    if (!userStore.token) {
      isNavigating = false
      return next('/login')
    }

    try {
      // 验证token是否有效
      await userStore.init()
      if (!userStore.isAuthenticated) {
        isNavigating = false
        return next('/login')
      }
    } catch (error) {
      console.error('认证检查失败:', error)
      isNavigating = false
      return next('/login')
    }
  }

  next()
})

router.afterEach(() => {
  isNavigating = false
})

// 全局错误处理
router.onError((error) => {
  console.error('Router error:', error)
})

export default router
