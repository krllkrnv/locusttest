import { createRouter, createWebHistory } from 'vue-router'
import TermsList from '../components/TermsList.vue'
import TermForm from '../components/TermForm.vue'
import MindMap from '../components/MindMap.vue'

const routes = [
  {
    path: '/',
    redirect: '/terms'
  },
  {
    path: '/terms',
    name: 'TermsList',
    component: TermsList
  },
  {
    path: '/terms/create',
    name: 'TermCreate',
    component: TermForm
  },
  {
    path: '/terms/:id/edit',
    name: 'TermEdit',
    component: TermForm,
    props: true
  },
  {
    path: '/graph',
    name: 'MindMap',
    component: MindMap
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
