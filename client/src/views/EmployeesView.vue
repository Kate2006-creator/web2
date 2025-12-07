<script setup>
import axios from "axios"
import { onMounted, ref } from 'vue';
import Cookies from 'js-cookie';

const employees = ref([]);
const employeeToAdd = ref({
  username: '',
  password: '',
  fio: '',
  birthday: '',
  position: '',  
});
const employeeToEdit = ref({});
const employeePictureRef = ref();
const employeeAddImageUrl = ref();
const employeeEditPictureRef = ref();
const employeeEditImageUrl = ref();
const imageModalUrl = ref('');
const errorMessage = ref('');

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

async function fetchEmployees() {
    const r = await axios.get("/api/user_profiles/")  
    employees.value = r.data.filter(profile => profile.user_type === 'employee');
}

async function onEmployeeAdd() {
  const userData = {
    username: employeeToAdd.value.username,
    password: employeeToAdd.value.password
  };
        
  const userResponse = await axios.post("/api/users/", userData);
  const userId = userResponse.data.id;

  const profilesResponse = await axios.get("/api/user_profiles/");
  const profiles = profilesResponse.data;    
        
  const userProfile = profiles.find(profile => profile.user === userId);

  const profileId = userProfile.id;
  const profileFormData = new FormData();
  profileFormData.append('fio', employeeToAdd.value.fio || '');
  profileFormData.append('position', employeeToAdd.value.position || '');  
  profileFormData.append('user_type', 'employee'); 
        
  if (employeeToAdd.value.birthday) {
      profileFormData.append('birthday', employeeToAdd.value.birthday);
  }
        
  if (employeePictureRef.value && employeePictureRef.value.files[0]) {
      profileFormData.append('picture', employeePictureRef.value.files[0]);
      }
        

  await axios.patch(`/api/user_profiles/${profileId}/`, profileFormData, {
            headers: { 
                'Content-Type': 'multipart/form-data',
                'X-CSRFToken': Cookies.get("csrftoken")
            }
        });

      
  employeeToAdd.value = { 
            username: '', 
            password: '', 
            fio: '', 
            birthday: '', 
            position: '' 
        };
        employeeAddImageUrl.value = null;
        if (employeePictureRef.value) {
            employeePictureRef.value.value = '';
        }
        
        await fetchEmployees();
        
        alert('Сотрудник успешно добавлен!');
}

// Функция для предпросмотра картинки при добавлении
function employeeAddPictureChange() {
  if (employeePictureRef.value && employeePictureRef.value.files[0]) {
    employeeAddImageUrl.value = URL.createObjectURL(employeePictureRef.value.files[0]);
  }
}

// Функция для предпросмотра картинки при редактировании
function employeeEditPictureChange() {
  if (employeeEditPictureRef.value && employeeEditPictureRef.value.files[0]) {
    employeeEditImageUrl.value = URL.createObjectURL(employeeEditPictureRef.value.files[0]);
  }
}

// Удаление сотрудника
async function onRemoveEmployeeClick(employee) {
  if (confirm(`Удалить сотрудника ${employee.fio}?`)) {
      await axios.delete(`/api/users/${employee.user}/`);
      await fetchEmployees();
      alert('Сотрудник удален!');
  }
}

// Редактирование сотрудника - открытие модального окна
function onEmployeeEditClick(employee) {
  employeeToEdit.value = { 
    ...employee,
    id: employee.id,
    fio: employee.fio || '',
    birthday: employee.birthday || '',
    position: employee.position || '',  
  };
  employeeEditImageUrl.value = employee.picture || null;
  if (employeeEditPictureRef.value) {
    employeeEditPictureRef.value.value = '';
  }
}

// Сохранение изменений сотрудника
async function onUpdateEmployee() { 
        const formData = new FormData();
        
        // Добавляем файл если выбран новый
        if (employeeEditPictureRef.value && employeeEditPictureRef.value.files[0]) {
            formData.append('picture', employeeEditPictureRef.value.files[0]);
        }
        
        // Обновляем поля профиля СОТРУДНИКА
        formData.append('fio', employeeToEdit.value.fio || '');
        formData.append('position', employeeToEdit.value.position || ''); 
        formData.append('user_type', 'employee');  
        if (employeeToEdit.value.birthday) {
            formData.append('birthday', employeeToEdit.value.birthday);
        } else {
            formData.append('birthday', '');
        }

        await axios.patch(`/api/user_profiles/${employeeToEdit.value.id}/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        await fetchEmployees();
        alert('Сотрудник обновлен!');
}

// Открытие модального окна с картинкой
function openImageModal(imageUrl) {
  imageModalUrl.value = imageUrl;
}

onMounted(async () => {
  await fetchEmployees();
})
</script>

<template>
  <div class="p-3">
    <!-- Форма добавления сотрудника -->
    <div class="mb-3">
      <h5>Добавление сотрудника</h5>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label for="username-input" class="form-label">Имя пользователя *</label>
          <input id="username-input" name="username" v-model="employeeToAdd.username" 
                 type="text" class="form-control" placeholder="Введите имя пользователя" required/>
        </div>
        <div class="col-md-6">
          <label for="password-input" class="form-label">Пароль *</label>
          <input id="password-input" name="password" v-model="employeeToAdd.password" 
                 type="password" class="form-control" placeholder="Введите пароль" required/>
        </div>
      </div>

      <div class="row mb-2">
        <div class="col-md-4">
          <label for="fio-input" class="form-label">ФИО</label>
          <input id="fio-input" name="fio" v-model="employeeToAdd.fio" 
                 type="text" class="form-control" placeholder="Иванов Иван Иванович"/>
        </div>
        <div class="col-md-4">
          <label for="position-input" class="form-label">Должность</label>
          <input id="position-input" name="position" v-model="employeeToAdd.position" 
                 type="text" class="form-control" placeholder="Менеджер, Разработчик и т.д."/>
        </div>
        <div class="col-md-4">
          <label for="birthday-input" class="form-label">Дата рождения</label>
          <input id="birthday-input" name="birthday" v-model="employeeToAdd.birthday" 
                 type="date" class="form-control"/>
        </div>
      </div>
      
      <!-- Поле для загрузки картинки -->
      <div class="row mb-2">
        <div class="col-md-6">
          <label class="form-label">Фотография</label>
          <input class="form-control" type="file" ref="employeePictureRef" 
                 @change="employeeAddPictureChange" accept="image/*">
        </div>
        <div class="col-md-6">
          <div v-if="employeeAddImageUrl" class="mt-4">
            <img :src="employeeAddImageUrl" style="max-height: 100px; max-width: 100%;" 
                 class="border rounded" alt="Предпросмотр">
          </div>
        </div>
      </div>
      
      <button @click="onEmployeeAdd" class="btn btn-primary">
        Добавить сотрудника
      </button>
      <small class="form-text text-muted d-block mt-1">* - обязательные поля</small>
    </div>

    <div class="mb-3">
      <button @click="fetchEmployees" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">Сотрудников: {{ employees.length }}</span>
    </div>
    
    <!-- Список сотрудников -->
    <div>
      <h5>Список сотрудников</h5>
      <div v-if="employees.length === 0" class="text-muted">
        Сотрудников нет
      </div>
      <div v-else>
        <div v-for="item in employees" :key="item.id" class="mb-2 p-2 border d-flex justify-content-between align-items-center">
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
              <span v-if="item.position"> | <strong>Должность:</strong> {{ item.position }}</span>
              <span v-if="item.birthday"> | <strong>Дата рождения:</strong> {{ item.birthday }}</span>
            </div>
          </div>
          <div>
            <button class="btn btn-success btn-sm me-1" @click="onEmployeeEditClick(item)" data-bs-toggle="modal" data-bs-target="#editEmployeeModal">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-danger btn-sm" @click="onRemoveEmployeeClick(item)">
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования сотрудника -->
    <div class="modal fade" id="editEmployeeModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">
              Редактировать сотрудника
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
                    v-model="employeeToEdit.fio"
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
                    v-model="employeeToEdit.position"
                    placeholder="Должность"
                  />
                  <label>Должность</label>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <input
                    type="date"
                    class="form-control"
                    v-model="employeeToEdit.birthday"
                  />
                  <label>Дата рождения</label>
                </div>
              </div>
            </div>
            
            <!-- Поле для изменения картинки -->
            <div class="row">
              <div class="col-md-6">
                <label class="form-label">Изменить фотографию</label>
                <input class="form-control" type="file" ref="employeeEditPictureRef" @change="employeeEditPictureChange" accept="image/*">
              </div>
              <div class="col-md-6">
                <div class="mt-4">
                  <div v-if="employeeEditImageUrl">
                    <p class="small text-muted mb-1">Новое изображение:</p>
                    <img :src="employeeEditImageUrl" style="max-height: 100px; max-width: 100%;" class="border rounded" alt="Предпросмотр">
                  </div>
                  <div v-else-if="employeeToEdit.picture">
                    <p class="small text-muted mb-1">Текущее изображение:</p>
                    <img :src="employeeToEdit.picture" style="max-height: 100px; max-width: 100%;" class="border rounded" alt="Текущее изображение">
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
              @click="onUpdateEmployee"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно для просмотра картинки (можно оставить общим) -->
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