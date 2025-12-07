<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useUserInfoStore } from '@/stores/user_info_store';
import { storeToRefs } from 'pinia';


const userInfoStore = useUserInfoStore();
const  {
  username
} = storeToRefs(userInfoStore)



</script>

<template>
 СТРАНИЦА 2

 Привет, {{ username }} !!!
</template>
<style scoped>

</style>
