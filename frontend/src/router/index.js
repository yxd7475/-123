import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true, roles: ['admin', 'operator', 'viewer'] },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页概览', icon: 'HomeFilled' }
      },
      {
        path: 'items',
        name: 'Items',
        component: () => import('@/views/Items.vue'),
        meta: { title: '物品管理', icon: 'Box' }
      },
      {
        path: 'inbound',
        name: 'Inbound',
        component: () => import('@/views/Inbound.vue'),
        meta: { title: '入库管理', icon: 'Download' }
      },
      {
        path: 'outbound',
        name: 'Outbound',
        component: () => import('@/views/Outbound.vue'),
        meta: { title: '出库管理', icon: 'Upload' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/Inventory.vue'),
        meta: { title: '库存查询', icon: 'Search' }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/Alerts.vue'),
        meta: { title: '库存预警', icon: 'Bell' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/Statistics.vue'),
        meta: { title: '统计报表', icon: 'DataLine' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/Logs.vue'),
        meta: { title: '操作日志', icon: 'Document', roles: ['admin'] }
      },
      {
        path: 'backup',
        name: 'Backup',
        component: () => import('@/views/Backup.vue'),
        meta: { title: '数据备份', icon: 'FolderOpened', roles: ['admin'] }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      }
    ]
  },
  {
    path: '/public',
    component: () => import('@/layout/PublicLayout.vue'),
    redirect: '/public/items',
    meta: { requiresAuth: false, isPublic: true },
    children: [
      {
        path: 'items',
        name: 'PublicItems',
        component: () => import('@/views/public/Items.vue'),
        meta: { title: '物品列表', isPublic: true }
      },
      {
        path: 'records',
        name: 'PublicRecords',
        component: () => import('@/views/public/Records.vue'),
        meta: { title: '领取记录', isPublic: true }
      }
    ]
  },
  {
    path: '/receiver',
    component: () => import('@/layout/ReceiverLayout.vue'),
    redirect: '/receiver/items',
    meta: { requiresAuth: true, roles: ['receiver'] },
    children: [
      {
        path: 'items',
        name: 'ReceiverItems',
        component: () => import('@/views/receiver/Items.vue'),
        meta: { title: '可领物品' }
      },
      {
        path: 'records',
        name: 'ReceiverRecords',
        component: () => import('@/views/receiver/Records.vue'),
        meta: { title: '我的领取记录' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.isPublic) {
    next()
    return
  }
  
  if (to.meta.requiresAuth !== false && !authStore.token) {
    next('/login')
    return
  }
  
  if (to.path === '/login' && authStore.token) {
    const userRole = authStore.user?.role
    if (userRole === 'receiver') {
      next('/receiver')
    } else {
      next('/dashboard')
    }
    return
  }
  
  if (to.meta.roles && authStore.user) {
    const userRole = authStore.user.role
    if (!to.meta.roles.includes(userRole)) {
      if (userRole === 'receiver') {
        next('/receiver')
      } else {
        next('/dashboard')
      }
      return
    }
  }
  
  next()
})

export default router
