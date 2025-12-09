<script setup>
import axios from "axios"
import { onMounted, ref, computed } from 'vue';
import Cookies from 'js-cookie';

const projectServices = ref([]);
const projects = ref([]); 
const favours = ref([]); 
const employees = ref([]); 
const projectServiceToAdd = ref({
  project: null,
  favour: null,
  employee_user: null,
  notes: '',
});
const projectServiceToEdit = ref({});
const wordExportUrl = computed(() => {
  return "/api/project_services/export_word";
});


axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");


async function fetchProjectServices() {
    const r = await axios.get("/api/project_services/");
    console.log('Услуги в проектах:', r.data);
    projectServices.value = r.data;
}

async function fetchProjects() {
  
    const r = await axios.get("/api/projects/");
    console.log('Проекты:', r.data);
  
    projects.value = r.data;
}


async function fetchFavours() {
    const r = await axios.get("/api/favours/");
    console.log('Услуги:', r.data);
    favours.value = r.data;
}

async function fetchEmployees() {

    const r = await axios.get("/api/user_profiles/");
    console.log('Профили:', r.data);
    
    let profiles = [];
    profiles = r.data;

    const employeeProfiles = profiles.filter(profile => profile.user_type === 'employee');
    
    employees.value = await Promise.all(
      employeeProfiles.map(async (profile) => {
          const userResponse = await axios.get(`/api/users/${profile.user}/`);
          return {
            id: profile.user, // ID пользователя
            profile_id: profile.id,
            fio: profile.fio || 'Без имени',
            position: profile.position || '',
            email: userResponse.data.email || '',
            username: userResponse.data.username,
          };
      })
    );
    
    console.log('Сотрудники для выбора:', employees.value);
}


async function onProjectServiceAdd() {

    if (!projectServiceToAdd.value.project || !projectServiceToAdd.value.favour) {
      alert('Выберите проект и услугу');
      return;
    }

    const projectServiceData = {
      project: projectServiceToAdd.value.project,
      favour: projectServiceToAdd.value.favour,
      employee_user: projectServiceToAdd.value.employee_user || null,
      notes: projectServiceToAdd.value.notes || '',
    };
    
    const response = await axios.post("/api/project_services/", projectServiceData);
    
    projectServiceToAdd.value = {
      project: null,
      favour: null,
      employee_user: null,
      notes: '',
    };
    
    await fetchProjectServices();
    
    alert('Услуга успешно добавлена в проект!');
    
  } 

async function onRemoveProjectService(projectService) {
  if (confirm(`Удалить услугу из проекта?`)) {  
    await axios.delete(`/api/project_services/${projectService.id}/`);
    await fetchProjectServices();
      alert('Услуга удалена из проекта!');
  }
}

function onProjectServiceEditClick(projectService) {
  console.log('Редактируем услугу в проекте:', projectService);
  
  projectServiceToEdit.value = { 
    ...projectService,
    id: projectService.id,
    project: projectService.project || null,
    favour: projectService.favour || null,
    employee_user: projectService.employee_user || null,
    notes: projectService.notes || '',
  };
}


async function onUpdateProjectService() {
     const updateData = {
      project: projectServiceToEdit.value.project,
      favour: projectServiceToEdit.value.favour,
      employee_user: projectServiceToEdit.value.employee_user || null,
      notes: projectServiceToEdit.value.notes || '',
    };
    
    const response = await axios.patch(`/api/project_services/${projectServiceToEdit.value.id}/`, updateData);
    
    await fetchProjectServices();
    alert('Услуга в проекте обновлена!');
}

function getProjectName(projectId) {
  if (!projectId) return 'Не указан';
  
  const project = projects.value.find(p => p.id === projectId);
  return project.name;
}

function getFavourName(favourId) {
  if (!favourId) return 'Не указана';
  
  const favour = favours.value.find(f => f.id === favourId);
  return favour.name;
}


function getEmployeeName(employeeId) {
  if (!employeeId) return 'Не назначен';
  
  const employee = employees.value.find(e => e.id === employeeId);
  return employee.fio;
}


function getEmployeePosition(employeeId) {
  if (!employeeId) return '';
  
  const employee = employees.value.find(e => e.id === employeeId);
  return  employee.position;
}

onMounted(async () => {
  await Promise.all([
    fetchProjectServices(),
    fetchProjects(),
    fetchFavours(),
    fetchEmployees()
  ]);
})
</script>

<template>
  <div class="p-3">
     <div class="d-flex gap-3 mb-2">
      <a :href="wordExportUrl" class="btn btn-success" target="_blank">
        <i class="bi bi-file-earmark-word me-2"></i>Выгрузка инфо в WORD
      </a>
    </div>

    <!-- Форма добавления услуги в проект -->
    <div class="mb-3">
      <h5>Добавление услуги в проект</h5>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label for="project-select" class="form-label">Проект *</label>
          <select id="project-select" v-model="projectServiceToAdd.project" class="form-select" required>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
        </div>
        
        <div class="col-md-6">
          <label for="favour-select" class="form-label">Услуга *</label>
          <select id="favour-select" v-model="projectServiceToAdd.favour" class="form-select" required>
            <option v-for="favour in favours" :key="favour.id" :value="favour.id">
              {{ favour.name }} - {{ favour.price}}
            </option>
          </select>
        </div>
      </div>

      <div class="row mb-2">
        <div class="col-md-6">
          <label for="employee-select" class="form-label">Сотрудник</label>
          <select id="employee-select" v-model="projectServiceToAdd.employee_user" class="form-select">
            <option v-for="employee in employees" :key="employee.id" :value="employee.id">
              {{ employee.fio }} {{ `(${employee.position})`}}
            </option>
          </select>
        </div>
        
        <div class="col-md-6">
          <label for="project-service-notes" class="form-label">Примечания</label>
          <textarea id="project-service-notes" v-model="projectServiceToAdd.notes" 
                    class="form-control" rows="2" placeholder="Дополнительные примечания..."></textarea>
        </div>
      </div>
      
      <button @click="onProjectServiceAdd" class="btn btn-primary">
        Добавить услугу в проект
      </button>
      <small class="form-text text-muted d-block mt-1">* - обязательные поля</small>
    </div>

    <div class="mb-3">
      <button @click="fetchProjectServices" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">Услуг в проектах: {{ projectServices.length }}</span>
    </div>
    
    <!-- Список услуг в проектах -->
    <div>
      <h5>Услуги в проектах</h5>
      <div v-if="projectServices.length === 0" class="text-muted">
        Услуг в проектах нет
      </div>
      <div v-else>
        <div v-for="projectService in projectServices" :key="projectService.id" class="mb-3 p-3 border rounded">
          <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
              <div class="row">
                <div class="col-md-4">
                  <h6 class="mb-1">Проект:</h6>
                  <p class="mb-2"><strong>{{ getProjectName(projectService.project) }}</strong></p>
                </div>
                
                <div class="col-md-4">
                  <h6 class="mb-1">Услуга:</h6>
                  <p class="mb-2"><strong>{{ getFavourName(projectService.favour) }}</strong></p>
                </div>
                
                <div class="col-md-4">
                  <h6 class="mb-1">Сотрудник:</h6>
                  <p class="mb-2">
                    <strong>{{ getEmployeeName(projectService.employee_user) }}</strong>
                    <span v-if="getEmployeePosition(projectService.employee_user)" class="text-muted small d-block">
                      {{ getEmployeePosition(projectService.employee_user) }}
                    </span>
                  </p>
                </div>
              </div>
              
              <div v-if="projectService.notes" class="mt-2">
                <h6 class="mb-1">Примечания:</h6>
                <p class="mb-0 text-muted">{{ projectService.notes }}</p>
              </div>
              
              <div v-else class="text-muted small mt-2">
                <em>Примечания отсутствуют</em>
              </div>
            </div>
            
            <div class="ms-3">
              <button class="btn btn-success btn-sm me-1" 
                      @click="onProjectServiceEditClick(projectService)" 
                      data-bs-toggle="modal" 
                      data-bs-target="#editProjectServiceModal">
                <i class="bi bi-pencil-square"></i>
              </button>
              <button class="btn btn-danger btn-sm" @click="onRemoveProjectService(projectService)">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования услуги в проекте -->
    <div class="modal fade" id="editProjectServiceModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать услугу в проекте</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Проект *</label>
                  <select class="form-select" v-model="projectServiceToEdit.project" required>
                    <option v-for="project in projects" :key="project.id" :value="project.id">
                      {{ project.name }}
                    </option>
                  </select>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Услуга *</label>
                  <select class="form-select" v-model="projectServiceToEdit.favour" required>
                    <option v-for="favour in favours" :key="favour.id" :value="favour.id">
                      {{ favour.name }} - {{ favour.price }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Сотрудник</label>
                  <select class="form-select" v-model="projectServiceToEdit.employee_user">
                    <option v-for="employee in employees" :key="employee.id" :value="employee.id">
                      {{ employee.fio }} {{ `(${employee.position})`}}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Примечания</label>
              <textarea class="form-control" v-model="projectServiceToEdit.notes" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button data-bs-dismiss="modal" type="button" class="btn btn-primary" @click="onUpdateProjectService">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge {
  font-size: 0.85em;
  padding: 0.35em 0.65em;
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.border {
  border-color: #e9ecef !important;
}
</style>