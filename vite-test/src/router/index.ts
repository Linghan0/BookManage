import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import BooksView from '@/views/BooksView.vue'
import LoginView from '@/views/LoginView.vue'
import UserBooksView from '@/views/UserBooksView.vue'
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
      path: '/userbooks',
      name: 'userbooks',
      component: UserBooksView
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
    }
  ]
})

export default router
