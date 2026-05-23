import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'

const iosLight = {
  dark: false,
  colors: {
    background: '#F2F2F7',
    surface: '#FFFFFFCC',
    'surface-bright': '#FFFFFF',
    'surface-variant': '#F2F2F7',
    'on-surface-variant': '#1C1C1E',
    primary: '#0A84FF',
    'primary-darken-1': '#0066CC',
    secondary: '#5E5CE6',
    accent: '#FF2D55',
    error: '#FF3B30',
    info: '#64D2FF',
    success: '#30D158',
    warning: '#FF9F0A',
  },
}

export default createVuetify({
  theme: {
    defaultTheme: 'iosLight',
    themes: { iosLight },
  },
  defaults: {
    VCard: {
      rounded: 'xl',
      elevation: 0,
      class: 'glass-card',
    },
    VBtn: {
      rounded: 'xl',
      style: 'text-transform: none; letter-spacing: 0; font-weight: 600;',
    },
    VTextField: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'comfortable',
    },
    VAutocomplete: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'comfortable',
    },
    VTextarea: {
      variant: 'outlined',
      rounded: 'lg',
    },
    VAlert: {
      rounded: 'lg',
      variant: 'tonal',
    },
    VChip: {
      rounded: 'xl',
    },
    VList: {
      class: 'glass-list',
      rounded: 'lg',
    },
    VDataTable: {
      class: 'glass-table',
    },
    VToolbar: {
      class: 'glass-toolbar',
    },
    VAppBar: {
      class: 'glass-appbar',
    },
    VDialog: {
      contentClass: 'glass-dialog',
    },
  },
})
