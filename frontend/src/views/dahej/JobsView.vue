<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { jobsApi, jobTypesApi, plantsApi, usersApi } from '@/api/dahej'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const items = ref([])
const jobTypes = ref([])
const plants = ref([])
const users = ref([])
const ranking = ref([])
const loading = ref(false)
const error = ref('')

const filters = ref({
  performer: null,
  job_type: null,
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

// v-date-picker works with Date objects; filters use YYYY-MM-DD strings.
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
  get: () => toDate(form.value.job_date),
  set: (v) => { form.value.job_date = toISO(v); formDateMenu.value = false },
})

function emptyForm() {
  return {
    id: null,
    performer: auth.user?.id ?? null,
    job_type: null,
    plant: null,
    job_date: new Date().toISOString().slice(0, 10),
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
  { title: 'Job date', key: 'job_date' },
  { title: 'Count', key: 'count', width: 90 },
  { title: 'Done', key: 'done', width: 90 },
  { title: 'Created by', key: 'created_by_username' },
  { title: 'Created at', key: 'created_at' },
  { title: 'Actions', key: 'actions', sortable: false, width: 240, align: 'end' },
]

const rankingHeaders = [
  { title: 'Rank', key: 'rank', width: 80 },
  { title: 'User', key: 'username' },
  { title: 'Total count', key: 'total_count' },
  { title: 'Last job', key: 'last_at' },
]

const activeFilterParams = computed(() => {
  const p = {}
  if (filters.value.performer) p.performer = filters.value.performer
  if (filters.value.job_type) p.job_type = filters.value.job_type
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
    const [j, jt, p, u, rk] = await Promise.all([
      jobsApi.list(params),
      jobTypesApi.list(),
      plantsApi.list(),
      usersApi.list(),
      jobsApi.ranking(params),
    ])
    items.value = j
    jobTypes.value = jt
    plants.value = p
    users.value = u
    ranking.value = rk
  } catch (e) {
    error.value = 'Failed to load jobs.'
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  filters.value = { performer: null, job_type: null, plant: null, date_from: '', date_to: '' }
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
    performer: item.performer,
    job_type: item.job_type,
    plant: item.plant,
    job_date: item.job_date,
    count: item.count,
    done: item.done,
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
      performer: form.value.performer,
      job_type: form.value.job_type,
      plant: form.value.plant,
      job_date: form.value.job_date,
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

// Color-grade ranks: green at the top, red at the bottom, interpolated over
// HSL hue from 120 (green) to 0 (red).
function rankColor(rank) {
  const n = ranking.value.length
  if (!n || !rank) return 'grey'
  if (n === 1) return 'hsl(120, 60%, 45%)'
  const t = (rank - 1) / (n - 1)
  const hue = Math.round(120 * (1 - t))
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
  <v-card class="mb-4">
    <v-card-title>Filters</v-card-title>
    <v-card-text>
      <v-row dense>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.performer"
            :items="users" item-title="username" item-value="id"
            label="Performer" clearable density="compact" hide-details
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-select
            v-model="filters.job_type"
            :items="jobTypes" item-title="name" item-value="id"
            label="Job type" clearable density="compact" hide-details
          />
        </v-col>
        <v-col cols="12" md="2">
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
        <v-col cols="12" md="1" class="d-flex align-center">
          <v-btn variant="text" @click="clearFilters">Clear</v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>

  <v-card class="mb-4">
    <v-card-title>Job ranking</v-card-title>
    <v-card-text>
      <v-row v-if="ranking.length" dense class="mb-2">
        <v-col cols="12" md="6" v-if="topRanked">
          <v-alert type="success" variant="tonal" density="compact">
            Highest: <strong>{{ topRanked.username }}</strong> &mdash; {{ topRanked.total_count }}
          </v-alert>
        </v-col>
        <v-col cols="12" md="6" v-if="bottomRanked">
          <v-alert type="info" variant="tonal" density="compact">
            Lowest: <strong>{{ bottomRanked.username }}</strong> &mdash; {{ bottomRanked.total_count }}
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
        <template #item.last_at="{ item }">{{ formatDate(item.last_at) }}</template>
      </v-data-table>
    </v-card-text>
  </v-card>

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
          <v-btn size="small" variant="text" @click="openDetail(item)">View</v-btn>
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
        <v-menu v-model="formDateMenu" :close-on-content-click="false" location="bottom">
          <template #activator="{ props }">
            <v-text-field
              v-bind="props" :model-value="form.job_date"
              label="Job date" prepend-inner-icon="mdi-calendar"
              readonly required
            />
          </template>
          <v-date-picker v-model="formDate" hide-header />
        </v-menu>
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

  <v-dialog v-model="detailDialog" max-width="640">
    <v-card v-if="detailItem">
      <v-card-title>Job #{{ detailItem.id }}</v-card-title>
      <v-card-text>
        <v-list density="compact">
          <v-list-item title="ID" :subtitle="String(detailItem.id)" />
          <v-list-item title="Job type" :subtitle="detailItem.job_type_name" />
          <v-list-item title="Plant" :subtitle="detailItem.plant_name" />
          <v-list-item title="Performed by" :subtitle="detailItem.performer_username" />
          <v-list-item title="Job date" :subtitle="detailItem.job_date" />
          <v-list-item title="Count" :subtitle="String(detailItem.count)" />
          <v-list-item title="Done" :subtitle="detailItem.done ? 'Yes' : 'No'" />
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
