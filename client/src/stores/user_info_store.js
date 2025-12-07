import {defineStore} from 'pinia'
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

export const useUserInfoStore = defineStore("userInfoStore", () => {
     
    const username = ref();
    const is_authenticated = ref(false);

    async function fetchUserInfo() {
        const r = await axios.get("/api/users_login/my/");

        username.value = r.data.username;
        is_authenticated.value = r.data.is_authenticated;

        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
    }
    
    onBeforeMount(async ()=>{
        fetchUserInfo();
    })

    return {
        username,
        is_authenticated,

        fetchUserInfo
    }
});