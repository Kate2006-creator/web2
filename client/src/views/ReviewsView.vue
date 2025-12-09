<script setup>
import axios from "axios"
import { onMounted, ref, computed } from 'vue';
import Cookies from 'js-cookie';

const reviews = ref([]);
const projects = ref([]); 
const reviewToAdd = ref({
  description: '',
  mark: 5,
  pr: null,
});
const reviewToEdit = ref({});
const reviewPictureRef = ref();
const reviewAddImageUrl = ref();
const reviewEditPictureRef = ref();
const reviewEditImageUrl = ref();
const imageModalUrl = ref('');
const stats = ref({
  total_count: 0,
  avg_mark: 0,
  marks_distribution: {}  
});

const wordExportUrl = computed(() => {
  return "/api/reviews/export_word";
});

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

async function fetchReviews() {
  const r = await axios.get("/api/reviews/");
  reviews.value = r.data;
}

async function fetchProjects() {
  const r = await axios.get("/api/projects/");
  projects.value = r.data;
}

async function fetchStats() {
  const r = await axios.get("/api/reviews/stats/");
  stats.value = r.data;
}

async function onReviewAdd() {
  if (!reviewToAdd.value.description || !reviewToAdd.value.mark) {
    alert('Заполните описание и оценку');
    return;
  }

  const reviewFormData = new FormData();
  reviewFormData.append('description', reviewToAdd.value.description);
  reviewFormData.append('mark', reviewToAdd.value.mark);
  
  if (reviewToAdd.value.pr) {
    reviewFormData.append('pr', reviewToAdd.value.pr);
  }
  
  if (reviewPictureRef.value && reviewPictureRef.value.files[0]) {
    reviewFormData.append('picture', reviewPictureRef.value.files[0]);
  }

  await axios.post("/api/reviews/", reviewFormData, {
    headers: { 
      'Content-Type': 'multipart/form-data',
      'X-CSRFToken': Cookies.get("csrftoken")
    }
  });

  reviewToAdd.value = {
    description: '',
    mark: 5,
    pr: null,
  };
  reviewAddImageUrl.value = null;
  if (reviewPictureRef.value) {
    reviewPictureRef.value.value = '';
  }
  
  await fetchReviews();
  await fetchStats();
  
  alert('Отзыв успешно добавлен!');
}

function reviewAddPictureChange() {
  if (reviewPictureRef.value && reviewPictureRef.value.files[0]) {
    reviewAddImageUrl.value = URL.createObjectURL(reviewPictureRef.value.files[0]);
  }
}

function reviewEditPictureChange() {
  if (reviewEditPictureRef.value && reviewEditPictureRef.value.files[0]) {
    reviewEditImageUrl.value = URL.createObjectURL(reviewEditPictureRef.value.files[0]);
  }
}


async function onRemoveReviewClick(review) {
  if (confirm(`Удалить отзыв с оценкой ${review.mark}?`)) {
    await axios.delete(`/api/reviews/${review.id}/`);
    await fetchReviews();
    await fetchStats();
    alert('Отзыв удален!');
  }
}


function onReviewEditClick(review) {
  reviewToEdit.value = { 
    ...review,
    id: review.id,
    description: review.description || '',
    mark: review.mark || 5,
    pr: review.pr || null,
  };
  reviewEditImageUrl.value = review.picture || null;
  if (reviewEditPictureRef.value) {
    reviewEditPictureRef.value.value = '';
  }
}


async function onUpdateReview() { 
  const formData = new FormData();
  

  if (reviewEditPictureRef.value && reviewEditPictureRef.value.files[0]) {
    formData.append('picture', reviewEditPictureRef.value.files[0]);
  }
  
  formData.append('description', reviewToEdit.value.description || '');
  formData.append('mark', reviewToEdit.value.mark || 5);
  if (reviewToEdit.value.pr) {
    formData.append('pr', reviewToEdit.value.pr);
  } else {
    formData.append('pr', '');
  }

  await axios.patch(`/api/reviews/${reviewToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  
  await fetchReviews();
   await fetchStats();
  alert('Отзыв обновлен!');
}


function openImageModal(imageUrl) {
  imageModalUrl.value = imageUrl;
}


function getProjectName(projectId) {
  if (!projectId) return 'Не указан';
  
  const project = projects.value.find(p => p.id === projectId);
  return project.name ;
}

function getStarRating(mark) {
  return '★'.repeat(mark) + '☆'.repeat(5 - mark);
}

onMounted(async () => {
  await fetchReviews();
  await fetchProjects();
  await fetchStats();
})
</script>

<template>
<div class="p-3">
    <div class="mb-3">
      <h5>Статистика отзывов</h5>
      
      <div class="d-flex flex-wrap gap-2">
        <div class="badge bg-success p-2 px-3">
          Всего отзывов: {{ stats.total_count}}
        </div>
        <div class="badge bg-success p-2 px-3">
          Средняя оценка: {{ stats.avg_mark }}
        </div>
      </div>
      
     
      <div v-if="stats.marks_distribution && Object.keys(stats.marks_distribution).length > 0">
        <h5 class="mt-3">Распределение по оценкам:</h5>
        <div class="d-flex flex-wrap gap-2">
          <div v-for="(count, mark) in stats.marks_distribution" 
     :key="mark" 
     class="badge bg-warning p-2 px-3">
  {{ mark }}★: {{ count }}
</div>
        </div>
      </div>
    </div>

     <div class="d-flex flex-wrap gap-2">
      <a :href="wordExportUrl" class="btn btn-success" target="_blank">
        <i class="bi bi-file-earmark-word me-2"></i>Выгрузка инфо в WORD
      </a>
    </div>

    </div>



  <div class="p-3">
    <!-- Форма добавления отзыва -->
    <div class="mb-3">
      <h5>Добавление отзыва</h5>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <label for="description-input" class="form-label">Описание *</label>
          <textarea id="description-input" name="description" v-model="reviewToAdd.description" 
                 class="form-control" rows="3" placeholder="Опишите ваши впечатления..." required></textarea>
        </div>
        <div class="col-md-6">
          <label for="mark-input" class="form-label">Оценка *</label>
          <select id="mark-input" name="mark" v-model="reviewToAdd.mark" class="form-select" required>
            <option value="1">★☆☆☆☆ - 1</option>
            <option value="2">★★☆☆☆ - 2</option>
            <option value="3">★★★☆☆ - 3</option>
            <option value="4">★★★★☆ - 4</option>
            <option value="5">★★★★★ - 5</option>
          </select>
          <div class="mt-2 text-warning" style="font-size: 1.2rem;">
            {{ getStarRating(reviewToAdd.mark) }}
          </div>
        </div>
      </div>

      <div class="row mb-2">
        <div class="col-md-6">
          <label for="project-select" class="form-label">Проект</label>
          <select id="project-select" name="pr" v-model="reviewToAdd.pr" class="form-select">
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">Изображение</label>
          <input class="form-control" type="file" ref="reviewPictureRef" 
                 @change="reviewAddPictureChange" accept="image/*">
        </div>
      </div>
      
      <div class="row mb-2">
        <div class="col-md-6">
          <div v-if="reviewAddImageUrl" class="mt-4">
            <img :src="reviewAddImageUrl" style="max-height: 100px; max-width: 100%;" 
                 class="border rounded" alt="Предпросмотр">
          </div>
        </div>
      </div>
      
      <button @click="onReviewAdd" class="btn btn-primary">
        Добавить отзыв
      </button>
      <small class="form-text text-muted d-block mt-1">* - обязательные поля</small>
    </div>

    <div class="mb-3">
      <button @click="fetchReviews" class="btn btn-primary">Обновить список</button>
      <span class="ms-2">Отзывов: {{ reviews.length }}</span>
    </div>
    
    <!-- Список отзывов -->
    <div>
      <h5>Список отзывов</h5>
      <div v-if="reviews.length === 0" class="text-muted">
        Отзывов нет
      </div>
      <div v-else>
        <div v-for="item in reviews" :key="item.id" class="mb-2 p-2 border d-flex justify-content-between align-items-center">
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
              <div class="mb-1">
                <strong>Оценка:</strong> 
                <span class="text-warning ms-1">{{ getStarRating(item.mark) }}</span>
                <span class="badge bg-secondary ms-2">{{ item.mark }}/5</span>
              </div>
              <div class="mb-1">
                <strong>Описание:</strong> {{ item.description || ' - ' }}
              </div>
              <div>
                <strong>Проект:</strong> {{ getProjectName(item.pr) }}
              </div>
            </div>
          </div>
          <div>
            <button class="btn btn-success btn-sm me-1" @click="onReviewEditClick(item)" data-bs-toggle="modal" data-bs-target="#editReviewModal">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-danger btn-sm" @click="onRemoveReviewClick(item)">
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования отзыва -->
    <div class="modal fade" id="editReviewModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">
              Редактировать отзыв
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
              <div class="col-md-12">
                <div class="form-floating mb-3">
                  <textarea
                    class="form-control"
                    v-model="reviewToEdit.description"
                    placeholder="Описание"
                    style="height: 100px;"
                  ></textarea>
                  <label>Описание</label>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <select
                    class="form-select"
                    v-model="reviewToEdit.mark"
                  >
                    <option value="1">★☆☆☆☆ - 1</option>
                    <option value="2">★★☆☆☆ - 2</option>
                    <option value="3">★★★☆☆ - 3</option>
                    <option value="4">★★★★☆ - 4</option>
                    <option value="5">★★★★★ - 5</option>
                  </select>
                  <label>Оценка</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <select
                    class="form-select"
                    v-model="reviewToEdit.pr"
                  >
                    <option v-for="project in projects" :key="project.id" :value="project.id">
                      {{ project.name }}
                    </option>
                  </select>
                  <label>Проект</label>
                </div>
              </div>
            </div>
            
            <!-- Поле для изменения картинки -->
            <div class="row">
              <div class="col-md-6">
                <label class="form-label">Изменить изображение</label>
                <input class="form-control" type="file" ref="reviewEditPictureRef" @change="reviewEditPictureChange" accept="image/*">
              </div>
              <div class="col-md-6">
                <div class="mt-4">
                  <div v-if="reviewEditImageUrl">
                    <p class="small text-muted mb-1">Новое изображение:</p>
                    <img :src="reviewEditImageUrl" style="max-height: 100px; max-width: 100%;" class="border rounded" alt="Предпросмотр">
                  </div>
                  <div v-else-if="reviewToEdit.picture">
                    <p class="small text-muted mb-1">Текущее изображение:</p>
                    <img :src="reviewToEdit.picture" style="max-height: 100px; max-width: 100%;" class="border rounded" alt="Текущее изображение">
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
              @click="onUpdateReview"
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