<script setup>
import { ref, onMounted } from 'vue'
import { overtimesApi, plantsApi } from '@/api/dahej'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const items = ref([])
const plants = ref([])
const loading = ref(false)
const error = ref('')

const formDialog = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const form = ref(emptyForm())

function emptyForm() {
  return {
    id: null,
    plants: [],
    date: new Date().toISOString().slice(0, 10),
    hours: 0,
    remarks: '',
    updation_remarks: '',
  }
}

const headers = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'User', key: 'user_username' },
  { title: 'Date', key: 'date' },
  { title: 'Hours', key: 'hours' },
  { title: 'Plants', key: 'plant_names' },
  { title: 'Remarks', key: 'remarks' },
  { title: 'Actions', key: 'actions', sortable: false, width: 180, align: 'end' },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!auth.user) await auth.fetchMe()
    const [ot, p] = await Promise.all([overtimesApi.list(), plantsApi.list()])
    items.value = ot
    plants.value = p
  } catch (e) {
    error.value = 'Failed to load overtimes.'
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
    plants: [...item.plants],
    date: item.date,
    hours: item.hours,
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
      user: auth.user.id,           // always log OT for the current user
      plants: form.value.plants,
      date: form.value.date,
      hours: form.value.hours,
      remarks: form.value.remarks,
      updation_remarks: form.value.updation_remarks,
    }
    if (isEdit.value) {
      await overtimesApi.update(form.value.id, payload)
    } else {
      await overtimesApi.create(payload)
    }
    formDialog.value = false
    await load()
  } catch (e) {
    error.value = formatError(e) || 'Failed to save overtime.'
  } finally {
    saving.value = false
  }
}

async function onDelete(item) {
  if (!confirm(`Delete overtime #${item.id}?`)) return
  try {
    await overtimesApi.remove(item.id)
    await load()
  } catch (e) {
    error.value = 'Failed to delete.'
  }
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
      Overtime
      <v-spacer />
      <v-btn icon variant="text" @click="load" :loading="loading"><v-icon>mdi-refresh</v-icon></v-btn>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Log overtime</v-btn>
    </v-card-title>

    <v-card-text>
      <v-alert v-if="error" type="error" density="compact" closable class="mb-3" @click:close="error = ''">{{ error }}</v-alert>

      <v-data-table :headers="headers" :items="items" :loading="loading" density="comfortable" items-per-page="25">
        <template #item.plant_names="{ item }">
          <v-chip v-for="name in item.plant_names" :key="name" size="x-small" class="mr-1">{{ name }}</v-chip>
        </template>
        <template #item.actions="{ item }">
          <v-btn size="small" variant="text" @click="openEdit(item)">Edit</v-btn>
          <v-btn size="small" variant="text" color="error" @click="onDelete(item)">Delete</v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <v-dialog v-model="formDialog" max-width="600" persistent>
    <v-card>
      <v-card-title>{{ isEdit ? 'Edit overtime' : 'Log overtime' }}</v-card-title>
      <v-card-text>
        <v-text-field v-model="form.date" label="Date" type="date" required />
        <v-text-field v-model.number="form.hours" label="Hours" type="number" step="0.25" min="0" required />
        <v-select
          v-model="form.plants"
          :items="plants" item-title="name" item-value="id"
          label="Plants" multiple chips
        />
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
