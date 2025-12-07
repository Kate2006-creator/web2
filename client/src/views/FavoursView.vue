<script setup>
import axios from "axios"
import { onMounted, ref } from 'vue';
import Cookies from 'js-cookie';

const favours = ref([]);
const favourToAdd = ref({
  name: '',
  description: '',
  price: 0,
});
const favourToEdit = ref({});
const errorMessage = ref('');

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");


async function fetchFavours() {
    const r = await axios.get("/api/favours/");
    console.log('Услуги:', r.data);
  
    favours.value = r.data;
}

async function onFavourAdd() {
    if (!favourToAdd.value.name) {
      alert('Заполните название услуги');
      return;
    }

    const favourData = {
      name: favourToAdd.value.name,
      description: favourToAdd.value.description || '',
      price: price,
    };
    
    const response = await axios.post("/api/favours/", favourData);

    favourToAdd.value = {
      name: '',
      description: '',
      price: 0,
    };
  
    await fetchFavours();
    
    alert('Услуга успешно добавлена!');
}

// Удаление услуги
async function onRemoveFavour(favour) {
  if (confirm(`Удалить услугу "${favour.name}"?`)) {
      await axios.delete(`/api/favours/${favour.id}/`);
      await fetchFavours();
      alert('Услуга удалена!');
  }
}

function onFavourEditClick(favour) {
  console.log('Редактируем услугу:', favour);
  
  favourToEdit.value = { 
    ...favour,
    id: favour.id,
    name: favour.name || '',
    description: favour.description || '',
    price: favour.price || 0,
  };
}

async function onUpdateFavour() {
    const updateData = {
      name: favourToEdit.value.name,
      description: favourToEdit.value.description || '',
      price: price,
    };
    const response = await axios.patch(`/api/favours/${favourToEdit.value.id}/`, updateData);

    await fetchFavours();
    alert('Услуга обновлена!');
}

onMounted(async () => {
  await fetchFavours();
})
</script>

<template>
  <div class="p-3">
    <!-- Форма добавления услуги -->
    <div class="mb-3">
      <h5>Добавление услуги</h5>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label for="favour-name" class="form-label">Название услуги *</label>
          <input id="favour-name" v-model="favourToAdd.name" 
                 type="text" class="form-control" placeholder="Введите название услуги" required/>
        </div>
        <div class="col-md-6">
          <label for="favour-price" class="form-label">Цена</label>
          <div class="input-group">
            <input id="favour-price" v-model.number="favourToAdd.price" 
                   type="number" class="form-control" placeholder="0" step="0.01" min="0"/>
            <span class="input-group-text">₽</span>
          </div>
        </div>
      </div>

      <div class="row mb-2">
        <div class="col-md-12">
          <label for="favour-description" class="form-label">Описание</label>
          <textarea id="favour-description" v-model="favourToAdd.description" 
                    class="form-control" rows="3" placeholder="Опишите услугу..."></textarea>
        </div>
      </div>
      
      <button @click="onFavourAdd" class="btn btn-primary">
        Добавить услугу
      </button>
      <small class="form-text text-muted d-block mt-1">* - обязательные поля</small>
    </div>

    <div class="mb-3">
      <button @click="fetchFavours" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">Услуг: {{ favours.length }}</span>
    </div>

    <div>
      <h5>Список услуг</h5>
      <div v-if="favours.length === 0" class="text-muted">
        Услуг нет
      </div>
      <div v-else>
        <div v-for="favour in favours" :key="favour.id" class="mb-2 p-3 border rounded">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">{{ favour.name }}</h6>
              
              <div class="mb-2">
                <span class="badge bg-success">
                  {{ favour.price }}
                </span>
              </div>
              
              <p class="mb-1 text-muted">
                {{ favour.description }}
              </p>
            </div>
            
            <div>
              <button class="btn btn-success btn-sm me-1" 
                      @click="onFavourEditClick(favour)" 
                      data-bs-toggle="modal" 
                      data-bs-target="#editFavourModal">
                <i class="bi bi-pencil-square"></i>
              </button>
              <button class="btn btn-danger btn-sm" @click="onRemoveFavour(favour)">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования услуги -->
    <div class="modal fade" id="editFavourModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать услугу</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название услуги *</label>
              <input type="text" class="form-control" v-model="favourToEdit.name" required/>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Цена</label>
              <div class="input-group">
                <input type="number" class="form-control" v-model.number="favourToEdit.price" 
                       step="0.01" min="0"/>
                <span class="input-group-text">₽</span>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Описание</label>
              <textarea class="form-control" v-model="favourToEdit.description" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button data-bs-dismiss="modal" type="button" class="btn btn-primary" @click="onUpdateFavour">
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
</style>