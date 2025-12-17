import { createRouter, createWebHistory } from 'vue-router'
import ClientsView from '../views/ClientsView.vue';
import ProjectsView from '../views/ProjectsView.vue';
import EmployeesView from '../views/EmployeesView.vue';
import ReviewsView from '../views/ReviewsView.vue';
import FavoursView from '../views/FavoursView.vue';
import ProjectServicesView from '../views/ProjectServicesView.vue';
import Page0 from '@/pages/Page0.vue';
import Page2 from '@/pages/Page2.vue';
import Page3 from '@/pages/Page3.vue';
import Login from '@/pages/Login.vue';
import { useUserInfoStore } from '@/stores/user_info_store';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
     {
      path: "/",
    },

    {
      path: "/entrance",
      name: "Login",
      component: Login
    },

    {
      path: "/page0",
      component: Page0
    },
    {
      path: "/page2",
      component: Page2
    },
    {
      path: "/page3",
      component: Page3
    },
    {
      path: "/clients",
      name: "ClientsView",
      component: ClientsView
    },

    {
    path: '/projects',
    name: 'ProjectsView',
    component: ProjectsView
    },

    {
    path: '/employees',
    name: 'EmployeesView',
    component: EmployeesView
    },

    {
    path: '/reviews',
    name: 'ReviewsView',
    component: ReviewsView
    },

    {
    path: '/favours',
    name: 'FavoursView',
    component: FavoursView
    },

    {
    path: '/project_services',
    name: 'ProjectServicesView',
    component: ProjectServicesView
    },
  ]
})

router.beforeEach((to, from) =>{

  const userInfoStore = useUserInfoStore();
  if (!userInfoStore.is_authenticated && to.name != "Login") {
    return {name: "Login", query: {next: to.path}}
  }

})

export default router
