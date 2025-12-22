import {defineStore} from 'pinia'
import { ref, onBeforeMount } from 'vue';
import { useRouter } from 'vue-router'
import axios from 'axios';
import Cookies from 'js-cookie';

export const useUserInfoStore = defineStore("userInfoStore", () => {
     
    const username = ref();
    const is_authenticated = ref(false);
    const is_staff = ref(false);
    const permissions = ref([]);
    const router = useRouter();

    async function fetchUserInfo() {
        const r = await axios.get("/api/users_login/my/");

        username.value = r.data.username;
        is_authenticated.value = r.data.is_authenticated;
        is_staff.value = r.data.is_staff;
        permissions.value = r.data.permissions;

        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

        if (is_authenticated.value){
            router.push(router.currentRoute.value.query.next || '/reviews')
        }
    }
    
    function hasPermission(name){
        return  permissions.value.includes(name);
    }


    onBeforeMount(async ()=>{
        fetchUserInfo();
    })

    return {
        username,
        is_authenticated,
        is_staff,

        fetchUserInfo,
        hasPermission,
    }
});