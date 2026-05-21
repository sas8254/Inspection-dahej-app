<script setup>
import { ref, onMounted } from 'vue'
import { plantsApi } from '@/api/dahej'

const items = ref([])
const loading = ref(false)
const error = ref('')

// Inline add
const newName = ref('')
const adding = ref(false)

// Edit dialog
const editDialog = ref(false)
const editing = ref(null)
const editName = ref('')
const editSaving = ref(false)

const headers = [
  { title: 'ID', key: 'id', width: 80 },
  { title: 'Name', key: 'name' },
  { title: 'Actions', key: 'actions', sortable: false, width: 180, align: 'end' },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await plantsApi.list()
  } catch (e) {
    error.value = 'Failed to load plants.'
  } finally {
    loading.value = false
  }
}

async function onAdd() {
  if (!newName.value.trim()) return
  adding.value = true
  try {
    await plantsApi.create({ name: newName.value.trim() })
    newName.value = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.name?.[0] || 'Failed to add plant.'
  } finally {
    adding.value = false
  }
}

function openEdit(item) {
  editing.value = item
  editName.value = item.name
  editDialog.value = true
}

async function onSave() {
  editSaving.value = true
  try {
    await plantsApi.update(editing.value.id, { name: editName.value.trim() })
    editDialog.value = false
    await load()
  } catch (e) {
    error.value = e.response?.data?.name?.[0] || 'Failed to update plant.'
  } finally {
    editSaving.value = false
  }
}

async function onDelete(item) {
  if (!confirm(`Delete "${item.name}"?`)) return
  try {
    await plantsApi.remove(item.id)
    await load()
  } catch (e) {
    error.value = 'Failed to delete (in use by a job/overtime?).'
  }
}

onMounted(load)
</script>

<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      Plants
      <v-spacer />
      <v-btn icon variant="text" @click="load" :loading="loading"><v-icon>mdi-refresh</v-icon></v-btn>
    </v-card-title>

    <v-card-text>
      <v-alert v-if="error" type="error" density="compact" closable class="mb-3" @click:close="error = ''">{{ error }}</v-alert>

      <v-form @submit.prevent="onAdd" class="d-flex ga-2 mb-4">
        <v-text-field v-model="newName" label="New plant name" density="compact" hide-details />
        <v-btn type="submit" color="primary" :loading="adding" :disabled="!newName.trim()">Add</v-btn>
      </v-form>

      <v-data-table :headers="headers" :items="items" :loading="loading" density="comfortable" items-per-page="25">
        <template #item.actions="{ item }">
          <v-btn size="small" variant="text" @click="openEdit(item)">Edit</v-btn>
          <v-btn size="small" variant="text" color="error" @click="onDelete(item)">Delete</v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <v-dialog v-model="editDialog" max-width="500">
    <v-card>
      <v-card-title>Edit plant</v-card-title>
      <v-card-text>
        <v-text-field v-model="editName" label="Name" autofocus />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="editDialog = false">Cancel</v-btn>
        <v-btn color="primary" :loading="editSaving" @click="onSave">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
