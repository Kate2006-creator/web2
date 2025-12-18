<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useUserInfoStore } from '@/stores/user_info_store';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const router = useRouter();

const userInfoStore = useUserInfoStore();
const  {
  is_authenticated,
  is_staff,
} = storeToRefs(userInfoStore)


async function onLogout() {
  const r = await axios.post("/api/users_login/logout/")
  userInfoStore.fetchUserInfo();
  router.go();
}

</script>

<template>

  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">Студия</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">


        <ul class="navbar-nav">
          <li class="nav-item">
            <router-link class="nav-link" v-if="userInfoStore.is_staff" to="/clients">Клиенты</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/favours">Услуги</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/projects">Проекты</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/reviews">Отзывы</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/project_services">Добавить услугу</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/employees" v-if = "userInfoStore.hasPermission('general.can_see_EmployeesView')">Сотрудники</router-link>
          </li>
        
        </ul>

        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button"
              data-bs-toggle="dropdown" aria-expanded="false">
              <i class="bi bi-person-circle me-2"></i>
              <span>Аккаунт</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <a class="dropdown-item" href="/admin" target="_blank">
                  <i class="bi bi-speedometer2 me-2"></i>
                  Админ
                </a>
              </li>
            </ul>
          </li>
        </ul>

        <button @click="onLogout" v-if="is_authenticated">Выйти</button>

      </div>
    </div>
  </nav>
  
  
<div v-if="userInfoStore.is_authenticated" class="fw-bold fs-4 mb-3 p-3">
  Привет, {{ userInfoStore.username }} !
</div>
  <router-view></router-view>

</template>
<style scoped>

</style>
