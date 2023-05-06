import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/game/:gameId',
      name: 'gameroom',
      component: () => import('../views/GameRoom.vue')
    },
    {
      path: '/game/:gameId/results',
      name: 'results',
      component: () => import('../views/ResultsView.vue')
    },
    {
      path: '/game/:gameId/join',
      name: 'playerjoin',
      component: () => import('../views/PlayerJoin.vue')
    },
  ]
})

export default router
