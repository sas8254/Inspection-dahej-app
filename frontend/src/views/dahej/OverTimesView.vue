<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { overtimesApi, plantsApi, usersApi } from '@/api/dahej'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const items = ref([])
const plants = ref([])
const users = ref([])
const ranking = ref([])
const loading = ref(false)
const error = ref('')

const filters = ref({
  user: null,
  plant: null,
  date_from: '',
  date_to: '',
})

const formDialog = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const form = ref(emptyForm())

const detailDialog = ref(false)
const detailItem = ref(null)

// v-date-picker works with Date objects; the API/state uses YYYY-MM-DD strings.
// These helpers bridge the two so menus stay in sync with the underlying state.
function toDate(s) {
  if (!s) return null
  const [y, m, d] = s.split('-').map(Number)
  return new Date(y, m - 1, d)
}
function toISO(d) {
  if (!d) return ''
  const dt = Array.isArray(d) ? d[0] : d
  if (!dt) return ''
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const fromMenu = ref(false)
const toMenu = ref(false)
const formDateMenu = ref(false)

const fromDate = computed({
  get: () => toDate(filters.value.date_from),
  set: (v) => { filters.value.date_from = toISO(v); fromMenu.value = false },
})
const toDateModel = computed({
  get: () => toDate(filters.value.date_to),
  set: (v) => { filters.value.date_to = toISO(v); toMenu.value = false },
})
const formDate = computed({
  get: () => toDate(form.value.date),
  set: (v) => { form.value.date = toISO(v); formDateMenu.value = false },
})

function emptyForm() {
  return {
    id: null,
    user: auth.user?.id ?? null,
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
  { title: 'Actions', key: 'actions', sortable: false, width: 240, align: 'end' },
]

const rankingHeaders = [
  { title: 'Rank', key: 'rank', width: 80 },
  { title: 'User', key: 'username' },
  { title: 'Total hours', key: 'total_hours' },
  { title: 'Last overtime', key: 'last_date' },
]

const activeFilterParams = computed(() => {
  const p = {}
  if (filters.value.user) p.user = filters.value.user
  if (filters.value.plant) p.plant = filters.value.plant
  if (filters.value.date_from) p.date_from = filters.value.date_from
  if (filters.value.date_to) p.date_to = filters.value.date_to
  return p
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!auth.user) await auth.fetchMe()
    const params = activeFilterParams.value
    const [ot, p, u, rk] = await Promise.all([
      overtimesApi.list(params),
      plantsApi.list(),
      usersApi.list(),
      overtimesApi.ranking(params),
    ])
    items.value = ot
    plants.value = p
    users.value = u
    ranking.value = rk
  } catch (e) {
    error.value = 'Failed to load overtimes.'
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  filters.value = { user: null, plant: null, date_from: '', date_to: '' }
  load()
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
    user: item.user,
    plants: [...item.plants],
    date: item.date,
    hours: item.hours,
    remarks: item.remarks,
    updation_remarks: '',
  }
  formDialog.value = true
}

function openDetail(item) {
  detailItem.value = item
  detailDialog.value = true
}

async function onSave() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      user: form.value.user,
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

// Color-grade ranks: green at the top, red at the bottom, yellow/orange in
// between. Interpolates over HSL hue from 120 (green) to 0 (red).
function rankColor(rank) {
  const n = ranking.value.length
  if (!n || !rank) return 'grey'
  if (n === 1) return 'hsl(120, 60%, 45%)'
  const t = (rank - 1) / (n - 1)            // 0 = best, 1 = worst
  const hue = Math.round(120 * (1 - t))     // 120 -> 0
  return `hsl(${hue}, 65%, 42%)`
}

const topRanked = computed(() => ranking.value[0] || null)
const bottomRanked = computed(() =>
  ranking.value.length > 1 ? ranking.value[ranking.value.length - 1] : null,
)

watch(filters, load, { deep: true })

onMounted(load)
</script>

<template>
  <div class="d-flex align-center mb-4">
    <div class="text-h5">Overtime</div>
    <v-spacer />
    <v-btn icon variant="text" @click="load" :loading="loading" class="mr-2"><v-icon>mdi-refresh</v-icon></v-btn>
    <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Log overtime</v-btn>
  </div>

  <v-card class="mb-4">
    <v-card-title>Filters</v-card-title>
    <v-card-text>
      <v-row dense>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.user"
            :items="users" item-title="username" item-value="id"
            label="User" clearable density="compact" hide-details
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.plant"
            :items="plants" item-title="name" item-value="id"
            label="Plant" clearable density="compact" hide-details
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-menu v-model="fromMenu" :close-on-content-click="false" location="bottom">
            <template #activator="{ props }">
              <v-text-field
                v-bind="props" :model-value="filters.date_from"
                label="From" prepend-inner-icon="mdi-calendar"
                readonly clearable density="compact" hide-details
                @click:clear="filters.date_from = ''"
              />
            </template>
            <v-date-picker v-model="fromDate" hide-header />
          </v-menu>
        </v-col>
        <v-col cols="12" md="2">
          <v-menu v-model="toMenu" :close-on-content-click="false" location="bottom">
            <template #activator="{ props }">
              <v-text-field
                v-bind="props" :model-value="filters.date_to"
                label="To" prepend-inner-icon="mdi-calendar"
                readonly clearable density="compact" hide-details
                @click:clear="filters.date_to = ''"
              />
            </template>
            <v-date-picker v-model="toDateModel" hide-header />
          </v-menu>
        </v-col>
        <v-col cols="12" md="2" class="d-flex align-center">
          <v-btn variant="text" @click="clearFilters">Clear</v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>

  <v-card class="mb-4">
    <v-card-title>Overtime ranking</v-card-title>
    <v-card-text>
      <v-row v-if="ranking.length" dense class="mb-2">
        <v-col cols="12" md="6" v-if="topRanked">
          <v-alert type="success" variant="tonal" density="compact">
            Highest: <strong>{{ topRanked.username }}</strong> &mdash; {{ topRanked.total_hours }} hrs
          </v-alert>
        </v-col>
        <v-col cols="12" md="6" v-if="bottomRanked">
          <v-alert type="info" variant="tonal" density="compact">
            Lowest: <strong>{{ bottomRanked.username }}</strong> &mdash; {{ bottomRanked.total_hours }} hrs
          </v-alert>
        </v-col>
      </v-row>
      <v-data-table
        :headers="rankingHeaders" :items="ranking" :loading="loading"
        density="compact" :items-per-page="-1" hide-default-footer
      >
        <template #item.rank="{ item }">
          <v-chip :color="rankColor(item.rank)" size="small" variant="flat" class="text-white">
            {{ item.rank }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>

  <v-card>
    <v-card-title>Overtime</v-card-title>

    <v-card-text>
      <v-alert v-if="error" type="error" density="compact" closable class="mb-3" @click:close="error = ''">{{ error }}</v-alert>

      <v-data-table :headers="headers" :items="items" :loading="loading" density="comfortable" items-per-page="25">
        <template #item.plant_names="{ item }">
          <v-chip v-for="name in item.plant_names" :key="name" size="x-small" class="mr-1">{{ name }}</v-chip>
        </template>
        <template #item.actions="{ item }">
          <v-btn size="small" variant="text" @click="openDetail(item)">View</v-btn>
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
        <v-select
          v-model="form.user"
          :items="users" item-title="username" item-value="id"
          label="User" required
        />
        <v-menu v-model="formDateMenu" :close-on-content-click="false" location="bottom">
          <template #activator="{ props }">
            <v-text-field
              v-bind="props" :model-value="form.date"
              label="Date" prepend-inner-icon="mdi-calendar"
              readonly required
            />
          </template>
          <v-date-picker v-model="formDate" hide-header />
        </v-menu>
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

  <v-dialog v-model="detailDialog" max-width="640">
    <v-card v-if="detailItem">
      <v-card-title>Overtime #{{ detailItem.id }}</v-card-title>
      <v-card-text>
        <v-list density="compact">
          <v-list-item title="ID" :subtitle="String(detailItem.id)" />
          <v-list-item title="User" :subtitle="detailItem.user_username" />
          <v-list-item title="Date" :subtitle="detailItem.date" />
          <v-list-item title="Hours" :subtitle="String(detailItem.hours)" />
          <v-list-item title="Plants" :subtitle="(detailItem.plant_names || []).join(', ') || '—'" />
          <v-list-item title="Remarks" :subtitle="detailItem.remarks || '—'" />
          <v-list-item title="Created by" :subtitle="detailItem.created_by_username" />
          <v-list-item title="Created at" :subtitle="formatDate(detailItem.created_at)" />
          <v-list-item title="Updated by" :subtitle="detailItem.updated_by_username || '—'" />
          <v-list-item title="Updated at" :subtitle="formatDate(detailItem.updated_at)" />
          <v-list-item title="Update remarks" :subtitle="detailItem.updation_remarks || '—'" />
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="detailDialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
