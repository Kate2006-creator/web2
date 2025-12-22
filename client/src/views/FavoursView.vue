<script setup>
import axios from "axios"
import { onMounted, ref, computed } from 'vue';
import Cookies from 'js-cookie';
import { useUserInfoStore } from "@/stores/user_info_store";
import { useRouter } from 'vue-router';
import { storeToRefs } from "pinia";

const favours = ref([]);
const filteredFavours = ref([]); 
const favourToAdd = ref({
  name: '',
  description: '',
  price: 0,
});
const favourToEdit = ref({});

const userInfoStore = useUserInfoStore()

const stats = ref({
  total_count: 0,
  min_price: 0,
  max_price: 0,
  avg_price: 0
});

const priceFilter = ref('none'); // none, asc, desc
const alphabetFilter = ref('none'); // none, asc

const wordExportUrl = computed(() => {
  return "/api/favours/export_word";
});

const {
  is_staff
} = storeToRefs(userInfoStore)

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

async function fetchFavours() {

  const params = {};
  
  if (priceFilter.value !== 'none') {
    params.price_sort = priceFilter.value; // 'asc' или 'desc'
  }
  
  if (alphabetFilter.value !== 'none') {
    params.alphabet_sort = 'asc'; 
  }
  
  const r = await axios.get("/api/favours/", { params });
  
  favours.value = r.data;
  filteredFavours.value = r.data; 
}

async function fetchStats() {
    const r = await axios.get("/api/favours/stats/");
    stats.value = r.data;
}

function applyFilters() {
  fetchFavours(); 
}

// Сброс фильтров
function clearFilters() {
  priceFilter.value = 'none';
  alphabetFilter.value = 'none';
  fetchFavours(); 
}

async function onFavourAdd() {
    if (!favourToAdd.value.name) {
      alert('Заполните название услуги');
      return;
    }

    const favourData = {
      name: favourToAdd.value.name,
      description: favourToAdd.value.description || '',
      price: favourToAdd.value.price,
    };
    
    const response = await axios.post("/api/favours/", favourData);

    favourToAdd.value = {
      name: '',
      description: '',
      price: 0,
    };
  
    await fetchFavours(); 
    await fetchStats();
    
    alert('Услуга успешно добавлена!');
}

async function onRemoveFavour(favour) {
  if (confirm(`Удалить услугу "${favour.name}"?`)) {
      await axios.delete(`/api/favours/${favour.id}/`);
      await fetchFavours();
      await fetchStats();
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
      price: favourToEdit.value.price, 
    };
    
    const response = await axios.patch(`/api/favours/${favourToEdit.value.id}/`, updateData);

    await fetchFavours(); 
    await fetchStats();
    alert('Услуга обновлена!');
}

onMounted(async () => {
  await fetchFavours();
  await fetchStats();
})
</script>

<template>
  <div class="p-3">
  <div class="mb-3" v-if="userInfoStore.is_staff">
  <h5>Статистика услуг</h5>
  <div class="d-flex gap-3 mb-4">
    <div class="badge bg-success p-2">
      Всего услуг: {{ stats.total_count || 0 }}
    </div>
    <div class="badge bg-success p-2">
      Средняя цена: {{ Math.round(stats.avg_price) }} ₽
    </div>
    <div class="badge bg-success p-2">
      Самая высокая цена: {{ Math.round(stats.max_price) }} ₽
    </div>
    <div class="badge bg-success p-2">
      Самая низкая цена: {{ Math.round(stats.min_price) }} ₽
    </div>
  </div>
</div>

     <div class="d-flex gap-3 mb-4">
      <a :href="wordExportUrl" class="btn btn-success" target="_blank">
        <i class="bi bi-file-earmark-word me-2"></i>Выгрузка инфо в WORD
      </a>
    </div>

</div>

  <div class="p-3">

    <div class="mb-3" v-if="userInfoStore.is_staff">
      <h3>Добавление услуги</h3>
      
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
    
    <div class="card mb-3">
      <div class="card-header bg-light">
        <h6 class="mb-0">Фильтры услуг</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-4 mb-2">
            <label class="form-label">Сортировка по цене</label>
            <select v-model="priceFilter" class="form-select" @change="applyFilters">
              <option value="none">Без сортировки</option>
              <option value="asc">По возрастанию цены</option>
              <option value="desc">По убыванию цены</option>
            </select>
          </div>
          <div class="col-md-4 mb-2">
            <label class="form-label">Сортировка по алфавиту</label>
            <select v-model="alphabetFilter" class="form-select" @change="applyFilters">
              <option value="none">Без сортировки</option>
              <option value="asc">По алфавиту (А-Я)</option>
            </select>
          </div>
          <div class="col-md-4 d-flex align-items-end">
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
      <button @click="fetchFavours" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">Услуг: {{ filteredFavours.length }}</span>
    </div>

    <div>
      <h5>Список услуг</h5>
      <div v-if="filteredFavours.length == 0" class="text-muted">
        Услуг нет
      </div>
      <div v-else>
        <div v-for="favour in filteredFavours" :key="favour.id" class="mb-2 p-3 border rounded">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">{{ favour.name }}</h6>
              
              <div class="mb-2">
                <span class="badge bg-success">
                  {{ favour.price }} ₽
                </span>
              </div>
              
              <p class="mb-1 text-muted">
                {{ favour.description }}
              </p>
            </div>
            
            <div v-if="userInfoStore.is_staff">
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
</style>