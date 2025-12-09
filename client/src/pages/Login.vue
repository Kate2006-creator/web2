<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useUserInfoStore } from '@/stores/user_info_store';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const username = ref();
const password = ref();
const userInfoStore = useUserInfoStore();
const {
    is_authenticated 
} = storeToRefs(userInfoStore)
const router = useRouter();

async function onLoginFormSubmit() {
    const r = await axios.post("/api/users_login/entrance/", {
        username: username.value,
        password: password.value,
    });

    username.value = '';
    password.value = '';

    await userInfoStore.fetchUserInfo()

    if (is_authenticated.value){
        router.push("/clients")
    }
}

</script>

<template>

<form @submit.stop.prevent="onLoginFormSubmit" class="form d-flex flex-column p-3" style="gap: 8px">
    <input placeholder="Логин" class="form-control" type="text" v-model="username">
    <input placeholder="Пароль" class="form-control" type="password" v-model="password">
    <button class="btn btn-info">Войти</button>
</form>


</template>
<style scoped>

</style>
