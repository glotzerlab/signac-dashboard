import { createRouter, createWebHistory } from 'vue-router'
import SchemaDisplay from '../components/SchemaDisplay.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'schema',
      component: SchemaDisplay
    }
  ],
})

export default router
