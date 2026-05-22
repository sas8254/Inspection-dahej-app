<script setup>
import { ref, onMounted } from 'vue'
import { jobsApi, jobTypesApi, plantsApi, usersApi } from '@/api/dahej'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const items = ref([])
const jobTypes = ref([])
const plants = ref([])
const users = ref([])
const loading = ref(false)
const error = ref('')

const formDialog = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const form = ref(emptyForm())

function emptyForm() {
  return {
    id: null,
    performer: auth.user?.id ?? null,
    job_type: null,
    plant: null,
    count: 1,
    done: false,
    remarks: '',
    updation_remarks: '',
  }
}

const headers = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'Job type', key: 'job_type_name' },
  { title: 'Plant', key: 'plant_name' },
  { title: 'Performed by', key: 'performer_username' },
  { title: 'Count', key: 'count', width: 90 },
  { title: 'Done', key: 'done', width: 90 },
  { title: 'Created by', key: 'created_by_username' },
  { title: 'Created at', key: 'created_at' },
  { title: 'Actions', key: 'actions', sortable: false, width: 180, align: 'end' },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!auth.user) await auth.fetchMe()
    const [j, jt, p, u] = await Promise.all([
      jobsApi.list(),
      jobTypesApi.list(),
      plantsApi.list(),
      usersApi.list(),
    ])
    items.value = j
    jobTypes.value = jt
    plants.value = p
    users.value = u
  } catch (e) {
    error.value = 'Failed to load jobs.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  form.value = emptyForm()
  formDialog.value = true
}

function openEdit(item) {
  isEdit.value = true
  form.value = {
    id: item.id,
    performer: item.performer,
    job_type: item.job_type,
    plant: item.plant,
    count: item.count,
    done: item.done,
    remarks: item.remarks,
    updation_remarks: '',
  }
  formDialog.value = true
}

async function onSave() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      performer: form.value.performer,
      job_type: form.value.job_type,
      plant: form.value.plant,
      count: form.value.count,
      done: form.value.done,
      remarks: form.value.remarks,
      updation_remarks: form.value.updation_remarks,
    }
    if (isEdit.value) {
      await jobsApi.update(form.value.id, payload)
    } else {
      await jobsApi.create(payload)
    }
    formDialog.value = false
    await load()
  } catch (e) {
    error.value = formatError(e) || 'Failed to save job.'
  } finally {
    saving.value = false
  }
}

async function onDelete(item) {
  if (!confirm(`Delete job #${item.id}?`)) return
  try {
    await jobsApi.remove(item.id)
    await load()
  } catch (e) {
    error.value = 'Failed to delete.'
  }
}

function formatDate(s) {
  if (!s) return ''
  return new Date(s).toLocaleString()
}

function formatError(e) {
  const d = e.response?.data
  if (d && typeof d === 'object') {
    const [field, msgs] = Object.entries(d)[0]
    return `${field}: ${Array.isArray(msgs) ? msgs[0] : msgs}`
  }
  return null
}

onMounted(load)
</script>

<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      Jobs
      <v-spacer />
      <v-btn icon variant="text" @click="load" :loading="loading"><v-icon>mdi-refresh</v-icon></v-btn>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">New job</v-btn>
    </v-card-title>

    <v-card-text>
      <v-alert v-if="error" type="error" density="compact" closable class="mb-3" @click:close="error = ''">{{ error }}</v-alert>

      <v-data-table :headers="headers" :items="items" :loading="loading" density="comfortable" items-per-page="25">
        <template #item.done="{ item }">
          <v-chip :color="item.done ? 'success' : 'default'" size="small">{{ item.done ? 'Yes' : 'No' }}</v-chip>
        </template>
        <template #item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
        <template #item.actions="{ item }">
          <v-btn size="small" variant="text" @click="openEdit(item)">Edit</v-btn>
          <v-btn size="small" variant="text" color="error" @click="onDelete(item)">Delete</v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <v-dialog v-model="formDialog" max-width="600" persistent>
    <v-card>
      <v-card-title>{{ isEdit ? 'Edit job' : 'New job' }}</v-card-title>
      <v-card-text>
        <v-select
          v-model="form.performer"
          :items="users" item-title="username" item-value="id"
          label="Performed by" required
        />
        <v-select
          v-model="form.job_type"
          :items="jobTypes" item-title="name" item-value="id"
          label="Job type" required
        />
        <v-select
          v-model="form.plant"
          :items="plants" item-title="name" item-value="id"
          label="Plant" required
        />
        <v-text-field v-model.number="form.count" label="Count" type="number" min="1" />
        <v-switch v-model="form.done" label="Done" color="primary" hide-details />
        <v-textarea v-model="form.remarks" label="Remarks" rows="2" auto-grow />
        <v-textarea v-if="isEdit" v-model="form.updation_remarks" label="Update remarks" rows="2" auto-grow />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="formDialog = false">Cancel</v-btn>
        <v-btn color="primary" :loading="saving" @click="onSave">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
