<script setup>
import axios from "axios"
import { onMounted, ref, computed } from 'vue';
import Cookies from 'js-cookie';
import { useRouter } from 'vue-router';
import { useUserInfoStore } from "@/stores/user_info_store";
import { storeToRefs } from "pinia";

const userInfoStore = useUserInfoStore()

const clients = ref([]);
const clientToAdd = ref({
  username: '',
  email: '',
  password: '',
  fio: '',
  birthday: '',
  company_name: '',
});
const clientToEdit = ref({});
const clientPictureRef = ref();
const clientAddImageUrl = ref();
const clientEditPictureRef = ref();
const clientEditImageUrl = ref();
const imageModalUrl = ref('');
const router = useRouter();

const wordExportUrl = computed(() => {
  return "/api/user_profiles/export_clients_word";
});

const stats = ref({
  total_clients: 0
});

const {
  is_staff
} = storeToRefs(userInfoStore)


axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

async function fetchClients() {
    const r = await axios.get("/api/user_profiles/")  
    console.log(r.data)
    clients.value = r.data.filter(profile => profile.user_type === 'client');
}

async function fetchStats() {
    const r = await axios.get("/api/user_profiles/stats/");
    stats.value = r.data;
}

async function onClientAdd() {
    const userData = {
      username: clientToAdd.value.username,
      password: clientToAdd.value.password
    };
    const userResponse = await axios.post("/api/users/", userData);
    const userId = userResponse.data.id;
    
    const profilesResponse = await axios.get("/api/user_profiles/");
    let profiles = [];
    profiles = profilesResponse.data;    
  
    const userProfile = profiles.find(profile => profile.user === userId);
    const profileId = userProfile.id;
    
    //Обновляем профиль
    const profileFormData = new FormData();
    profileFormData.append('fio', clientToAdd.value.fio || '');
    profileFormData.append('company_name', clientToAdd.value.company_name || '');
    profileFormData.append('user_type', 'client');
    
    if (clientToAdd.value.birthday) {
      profileFormData.append('birthday', clientToAdd.value.birthday);
    }
    
    if (clientPictureRef.value && clientPictureRef.value.files[0]) {
      profileFormData.append('picture', clientPictureRef.value.files[0]);
    }
    
    await axios.patch(`/api/user_profiles/${profileId}/`, profileFormData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    // Очистка формы
    clientToAdd.value = { username: '', password: '', fio: '', birthday: '', company_name: '' };
    clientAddImageUrl.value = null;
    if (clientPictureRef.value) clientPictureRef.value.value = '';
    
    await fetchClients();
    await fetchStats();
    alert('Клиент успешно добавлен!');
}


function clientAddPictureChange() {
  if (clientPictureRef.value && clientPictureRef.value.files[0]) {
    clientAddImageUrl.value = URL.createObjectURL(clientPictureRef.value.files[0]);
  }
}

function clientEditPictureChange() {
  if (clientEditPictureRef.value && clientEditPictureRef.value.files[0]) {
    clientEditImageUrl.value = URL.createObjectURL(clientEditPictureRef.value.files[0]);
  }
}


async function onRemoveClick(client) {
  if (confirm(`Удалить клиента ${client.fio}?`)) {
    await axios.delete(`/api/users/${client.user}/`);
    await fetchClients();
    await fetchStats();
    alert('Клиент удален!');
  }
}


function onClientEditClick(client) {
  clientToEdit.value = { 
    ...client,
    id: client.id,
    fio: client.fio || '',
    birthday: client.birthday || '',
    company_name: client.company_name || '',
  };
  clientEditImageUrl.value = client.picture || null;
  if (clientEditPictureRef.value) {
    clientEditPictureRef.value.value = '';
  }
}


async function onUpdateClient() { 
   const formData = new FormData();
    

    if (clientEditPictureRef.value && clientEditPictureRef.value.files[0]) {
      formData.append('picture', clientEditPictureRef.value.files[0]);
    }
    

    formData.set('fio', clientToEdit.value.fio || '');
    if (clientToEdit.value.birthday) {
      formData.set('birthday', clientToEdit.value.birthday);
    } else {
      formData.set('birthday', '');
    }
    formData.set('company_name', clientToEdit.value.company_name || '');
    formData.set('user_type', 'client');

    await axios.patch(`/api/user_profiles/${clientToEdit.value.id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    await fetchClients();
    await fetchStats();
    alert('Клиент обновлен!');
}

function openImageModal(imageUrl) {
  imageModalUrl.value = imageUrl;
}

onMounted(async () => {
  await fetchClients();
  await fetchStats();
   //if (!userInfoStore.is_staff) {
   // router.push('/');
  //};
})
</script>

<template>

 <div v-if="!userInfoStore.is_staff" class="p-3">
    <div class="alert alert-danger text-center mt-5">
      <h4>⛔ Доступ запрещен</h4>
      <p>Страница "Клиенты" доступна только администраторам.</p>
      <button @click="$router.push('/')" class="btn btn-primary">
        На главную
      </button>
    </div>
  </div>

  <div v-else class="p-3">
      <h5>Статистика клиентов</h5>
      <div class="d-flex gap-3 p-2">
        <div class="badge bg-primary p-3 px-4">
          Всего клиентов: {{ stats.total_clients || 0 }}
        </div>
    </div>

    <div class="d-flex gap-3 p-2">
      <a :href="wordExportUrl" class="btn btn-success" target="_blank">
        <i class="bi bi-file-earmark-word me-2"></i>Выгрузка инфо в WORD
      </a>
    </div>
  

  <div class="p-3">

    <div class="mb-3">
      <h3>Добавление клиента</h3>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label for="username-input" class="form-label">Имя пользователя *</label>
          <input id="username-input" name="username" v-model="clientToAdd.username" 
                 type="text" class="form-control" placeholder="Введите имя пользователя" required/>
        </div>
        <div class="col-md-6">
          <label for="password-input" class="form-label">Пароль *</label>
          <input id="password-input" name="password" v-model="clientToAdd.password" 
                 type="password" class="form-control" placeholder="Введите пароль" required/>
        </div>
      </div>

      <div class="row mb-2">
        <div class="col-md-4">
          <label for="fio-input" class="form-label">ФИО</label>
          <input id="fio-input" name="fio" v-model="clientToAdd.fio" 
                 type="text" class="form-control" placeholder="Иванов Иван Иванович"/>
        </div>
        <div class="col-md-4">
          <label for="company-input" class="form-label">Название компании</label>
          <input id="company-input" name="company" v-model="clientToAdd.company_name" 
                 type="text" class="form-control" placeholder="ООО 'Ромашка'"/>
        </div>
        <div class="col-md-4">
          <label for="birthday-input" class="form-label">Дата рождения</label>
          <input id="birthday-input" name="birthday" v-model="clientToAdd.birthday" 
                 type="date" class="form-control"/>
        </div>
      </div>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label class="form-label">Фотография</label>
          <input class="form-control" type="file" ref="clientPictureRef" 
                 @change="clientAddPictureChange" accept="image/*">
        </div>
        <div class="col-md-6">
          <div v-if="clientAddImageUrl" class="mt-4">
            <img :src="clientAddImageUrl" style="max-height: 100px; max-width: 100%;" 
                 class="border rounded" alt="Предпросмотр">
          </div>
        </div>
      </div>
      
      <button @click="onClientAdd" class="btn btn-primary">
        Добавить клиента
      </button>
      <small class="form-text text-muted d-block mt-1">* - обязательные поля</small>
    </div>

    <div class="mb-3">
      <button @click="fetchClients" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">Клиентов: {{ clients.length }}</span>
    </div>
    

    <div>
      <h5>Список клиентов</h5>
      <div v-if="clients.length === 0" class="text-muted">
        Клиентов нет
      </div>
      <div v-else>
        <div v-for="item in clients" :key="item.id" class="mb-2 p-2 border d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">

            <div v-if="item.picture" class="me-3">
              <img 
                :src="item.picture" 
                style="max-height: 60px; max-width: 60px; cursor: pointer;" 
                class="border rounded" 
                alt=""
                @click="openImageModal(item.picture)"
                data-bs-toggle="modal" 
                data-bs-target="#imageModal"
              >
            </div>
            <div>
              <strong>ФИО:</strong> {{ item.fio || ' - ' }}
              <span v-if="item.company_name"> | <strong>Компания:</strong> {{ item.company_name }}</span>
              <span v-if="item.birthday"> | <strong>Дата рождения:</strong> {{ item.birthday }}</span>
            </div>
          </div>
          <div>
            <button class="btn btn-success btn-sm me-1" @click="onClientEditClick(item)" data-bs-toggle="modal" data-bs-target="#editClientModal">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-danger btn-sm" @click="onRemoveClick(item)">
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>

    <div class="modal fade" id="editClientModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">
              Редактировать клиента
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
  <div class="row">
    <div class="col-md-6">
      <div class="form-floating mb-3">
        <input
          type="text"
          class="form-control"
          v-model="clientToEdit.fio"
          placeholder="ФИО"
        />
        <label>ФИО</label>
      </div>
    </div>
    <div class="col-md-6">
      <div class="form-floating mb-3">
        <input
          type="text"
          class="form-control"
          v-model="clientToEdit.company_name"
          placeholder="Название компании"
        />
        <label>Название компании</label>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-6">
      <div class="form-floating mb-3">
        <input
          type="date"
          class="form-control"
          v-model="clientToEdit.birthday"
        />
                  <label>Дата рождения</label>
                </div>
              </div>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <label class="form-label">Изменить фотографию</label>
                <input class="form-control" type="file" ref="clientEditPictureRef" @change="clientEditPictureChange" accept="image/*">
              </div>
              <div class="col-md-6">
                <div class="mt-4">
                  <div v-if="clientEditImageUrl">
                    <p class="small text-muted mb-1">Новое изображение:</p>
                    <img :src="clientEditImageUrl" style="max-height: 100px; max-width: 100%;" class="border rounded" alt="Предпросмотр">
                  </div>
                  <div v-else-if="clientToEdit.picture">
                    <p class="small text-muted mb-1">Текущее изображение:</p>
                    <img :src="clientToEdit.picture" style="max-height: 100px; max-width: 100%;" class="border rounded" alt="Текущее изображение">
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Закрыть
            </button>
            <button
              data-bs-dismiss="modal"
              type="button"
              class="btn btn-primary"
              @click="onUpdateClient"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="imageModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Просмотр изображения</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="imageModalUrl" style="max-width: 100%; max-height: 70vh;" class="img-fluid" alt="Увеличенное изображение">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>