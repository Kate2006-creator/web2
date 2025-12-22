<script setup>
import axios from "axios"
import { onMounted, ref, computed } from 'vue';
import Cookies from 'js-cookie';
import { useUserInfoStore } from "@/stores/user_info_store";
import { storeToRefs } from "pinia";

const userInfoStore = useUserInfoStore()
const projects = ref([]);
const filteredProjects = ref([]);
const clients = ref([]); 
const projectToAdd = ref({
  name: '',
  description: '',
  status: 'планирование',
  client_user: null,
});
const projectToEdit = ref({});
const stats = ref({
  total_count: 0,
  by_status: {}
});
const filters = ref({
  client_id: '',
  status: ''
});
const wordExportUrl = computed(() => { //реактивная функция, вычисляетя динамически при каждом обращении
  return "/api/projects/export_word";
});

const {
  is_staff
} = storeToRefs(userInfoStore)

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

async function fetchProjects() {
  const params = {};

  if (userInfoStore.is_staff && filters.value.client_id) {
    params.client_id = filters.value.client_id;
  }
  
  if (filters.value.status) {
    params.status = filters.value.status;
  }
  
  const r = await axios.get("/api/projects/", { params });
  projects.value = r.data;
  filteredProjects.value = r.data; 
}

async function fetchStats() {
  const r = await axios.get("/api/projects/stats/");
  stats.value = r.data;
}

async function fetchClients() {
   if (!userInfoStore.is_staff) {
        clients.value = [];
        return;
    }
    const r = await axios.get("/api/user_profiles/");
    const clientProfiles = r.data.filter(profile => profile.user_type == 'client');
        
    clients.value = await Promise.all( 
        clientProfiles.map(async (profile) => { //для каждого профиля в  clientProfiles запускаем асинхронную функцию
        const userResponse = await axios.get(`/api/users/${profile.user}/`);
                    return {
                        id: profile.user, // ID пользователя
                        profile_id: profile.id,
                        fio: profile.fio || 'Без имени',
                        company_name: profile.company_name || '',
                        email: userResponse.data.email || '',
                        username: userResponse.data.username,
                    };
            })
        );
}

function applyFilters() {
  fetchProjects(); 
}


function clearFilters() {
  filters.value = {
    client_id: '',
    status: ''
  };
  fetchProjects(); 
}

async function onProjectAdd() {
        // Проверяем обязательные поля
        if (!projectToAdd.value.name || !projectToAdd.value.status) {
            alert('Заполните название и статус проекта');
            return;
        }

        const projectData = {
            name: projectToAdd.value.name,
            description: projectToAdd.value.description || '',
            status: projectToAdd.value.status,
            client_user: projectToAdd.value.client_user || null,
        };
        const response = await axios.post("/api/projects/", projectData);
        projectToAdd.value = {
            name: '',
            description: '',
            status: 'планирование',
            client_user: null,
        };
        
        await fetchProjects();
        await fetchStats();
        
        alert('Проект успешно добавлен!');   
}

async function onRemoveProject(project) {
    if (confirm(`Удалить проект "${project.name}"?`)) {
            await axios.delete(`/api/projects/${project.id}/`);
            await fetchProjects(); 
            await fetchStats();
            alert('Проект удален!');
    }
}

function onProjectEditClick(project) {
    projectToEdit.value = { 
        ...project,
        id: project.id,
        name: project.name || '',
        description: project.description || '',
        status: project.status || '',
        client_user: project.client_user || null,
    };
}

async function onUpdateProject() {
        const updateData = {
            name: projectToEdit.value.name,
            description: projectToEdit.value.description || '',
            status: projectToEdit.value.status,
            client_user: projectToEdit.value.client_user || null,
        };

        await axios.patch(`/api/projects/${projectToEdit.value.id}/`, updateData);
        
        await fetchProjects();
        await fetchStats();
        alert('Проект обновлен!');
}

const projectStatuses = [
    { value: 'планирование', label: 'Планирование' },
    { value: 'в работе', label: 'В работе' },
    { value: 'приостановлен', label: 'Приостановлен' },
    { value: 'завершен', label: 'Завершен' },
    { value: 'отменен', label: 'Отменен' },
];

onMounted(async () => {
    await fetchProjects();
    await fetchClients();
    await fetchStats();
})
</script>

<template>


<div class="p-3">
  <div v-if="userInfoStore.is_staff">
    <h5>Статистика проектов</h5>
    <div class="d-flex gap-3 mb-2">
      <div class="badge bg-secondary p-3 px-5">
        Всего: {{ stats.total_count || 0 }}
      </div>
      <div v-for="(count, status) in stats.by_status" :key="status" 
           class="badge bg-secondary p-3 px-4">
        {{ status }}: {{ count }}
      </div>
    </div>
  </div>

  <div class="d-flex gap-3 mb-2">
    <a :href="wordExportUrl" class="btn btn-success" target="_blank">
      <i class="bi bi-file-earmark-word me-2"></i>
      <div v-if="userInfoStore.is_staff">
        Выгрузить все проекты 
      </div>
      <div v-else>
        Выгрузить мои проекты
      </div>
    </a>
  </div>
</div>


  <div class="p-3">
    <div class="mb-3">
      <h5>Добавление проекта</h5>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label for="project-name" class="form-label">Название проекта *</label>
          <input id="project-name" v-model="projectToAdd.name" 
                 type="text" class="form-control" placeholder="Введите название проекта" required/>
        </div>
        <div class="col-md-6">
          <label for="project-status" class="form-label">Статус *</label>
          <select id="project-status" v-model="projectToAdd.status" class="form-select" required>
            <option v-for="status in projectStatuses" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="row mb-2">
        <div class="col-md-6">
          <label for="project-description" class="form-label">Описание</label>
          <textarea id="project-description" v-model="projectToAdd.description" 
                    class="form-control" rows="3" placeholder="Опишите проект..."></textarea>
        </div>
        <div class="col-md-6" v-if="is_staff">
          <label for="project-client" class="form-label">Клиент</label>
          <select id="project-client" v-model="projectToAdd.client_user" class="form-select">
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.fio }}
            </option>
          </select>
        </div>
      </div>
      
      <button @click="onProjectAdd" class="btn btn-primary">
        Добавить проект
      </button>
      <small class="form-text text-muted d-block mt-1">* - обязательные поля</small>
    </div>

    <div class="card mb-3">
      <div class="card-header bg-light">
        <h6 class="mb-0">Фильтры проектов</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div v-if="userInfoStore.is_staff" class="col-md-4 mb-2">
            <label class="form-label">Клиент</label>
            <select v-model="filters.client_id" class="form-select" @change="applyFilters">
              <option value="">Все клиенты</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                ({{ client.fio }})
              </option>
            </select>
          </div>
          
          <div :class="userInfoStore.is_staff ? 'col-md-4' : 'col-md-8'">
            <label class="form-label">Статус</label>
            <select v-model="filters.status" class="form-select" @change="applyFilters">
              <option value="">Все статусы</option>
              <option value="планирование">Планирование</option>
              <option value="в работе">В работе</option>
              <option value="приостановлен">Приостановлен</option>
              <option value="завершен">Завершен</option>
              <option value="отменен">Отменен</option>
            </select>
          </div>
          
          <div :class="userInfoStore.is_staff ? 'col-md-4' : 'col-md-4'" class="d-flex align-items-end">
            <div>
              <button @click="clearFilters" class="btn btn-secondary btn-sm">
                Сбросить фильтры
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mb-3">
      <button @click="fetchProjects" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">
        {{ userInfoStore.is_staff ? 'Всего проектов:' : 'Мои проекты:' }} 
        {{ filteredProjects.length }}
      </span>
    </div>


    <div>
      <h5>{{ userInfoStore.is_staff ? 'Список проектов' : 'Мои проекты' }}</h5>
      <div v-if="filteredProjects.length == 0" class="text-muted">
        <span v-if="userInfoStore.is_staff">Проектов нет в системе</span>
        <span v-else>У вас пока нет проектов</span>
      </div>
      <div v-else>
        <div v-for="project in filteredProjects" :key="project.id" class="mb-2 p-3 border rounded">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">{{ project.name }}</h6>
              <div class="mb-2">
                <span class="badge" :class="{
                  'bg-secondary': project.status == 'планирование',
                  'bg-primary': project.status == 'в работе',
                  'bg-warning': project.status == 'приостановлен',
                  'bg-success': project.status == 'завершен',
                  'bg-danger': project.status == 'отменен',
                }">
                  {{ project.status }}
                </span>
              </div>
              
              <p class="mb-1 text-muted" v-if="project.description">
                {{ project.description }}
              </p>
              
              <div v-if="userInfoStore.is_staff" class="text-muted small mt-2">
                <strong>Клиент:</strong> 
                {{ project.client_fio }}
              </div>
            </div>
            
            <div>
              <button class="btn btn-success btn-sm me-1" 
                      @click="onProjectEditClick(project)" 
                      data-bs-toggle="modal" 
                      data-bs-target="#editProjectModal">
                <i class="bi bi-pencil-square"></i>
              </button>
              <button class="btn btn-danger btn-sm" @click="onRemoveProject(project)">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editProjectModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать проект</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название проекта *</label>
              <input type="text" class="form-control" v-model="projectToEdit.name" required/>
            </div>
            

            <div v-if="userInfoStore.is_staff" class="mb-3">
              <label class="form-label">Статус</label>
              <select class="form-select" v-model="projectToEdit.status" required>
                <option v-for="status in projectStatuses" :key="status.value" :value="status.value">
                  {{ status.label }}
                </option>
              </select>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Описание</label>
              <textarea class="form-control" v-model="projectToEdit.description" rows="3"></textarea>
            </div>
            
            <div v-if="userInfoStore.is_staff" class="mb-3">
          <label class="form-label">Клиент</label>
          <select class="form-select" v-model="projectToEdit.client_user">
            <option :value="null">Не выбран</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.fio}}
            </option>
          </select>
        </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button data-bs-dismiss="modal" type="button" class="btn btn-primary" @click="onUpdateProject">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>