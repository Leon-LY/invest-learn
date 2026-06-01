import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const theme = ref<'light' | 'dark' | 'system'>(
    (localStorage.getItem('app-theme') as 'light' | 'dark' | 'system') || 'system'
  )
  const sidebarCollapsed = ref(false)
  const colorScheme = ref<'red_up_green_down' | 'green_up_red_down'>(
    (localStorage.getItem('color-scheme') as any) || 'red_up_green_down'
  )
  const learningMode = ref(
    localStorage.getItem('learning-mode') !== 'false'
  )

  const isDark = computed(() => {
    if (theme.value === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return theme.value === 'dark'
  })

  function setTheme(t: 'light' | 'dark' | 'system') {
    theme.value = t
    localStorage.setItem('app-theme', t)
    applyTheme()
  }

  function toggleTheme() {
    const next: Record<string, 'light' | 'dark' | 'system'> = {
      light: 'dark', dark: 'system', system: 'light',
    }
    setTheme(next[theme.value])
  }

  function applyTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function toggleLearningMode() {
    learningMode.value = !learningMode.value
    localStorage.setItem('learning-mode', String(learningMode.value))
  }

  function setColorScheme(scheme: 'red_up_green_down' | 'green_up_red_down') {
    colorScheme.value = scheme
    localStorage.setItem('color-scheme', scheme)
  }

  function getColor(change: number | null): string {
    if (!change) return 'market-flat'
    const isUp = change > 0
    if (colorScheme.value === 'red_up_green_down') {
      return isUp ? 'market-up' : 'market-down'
    }
    return isUp ? 'market-down' : 'market-up'
  }

  // Initialize theme on load
  applyTheme()

  return {
    theme, sidebarCollapsed, colorScheme, learningMode, isDark,
    setTheme, toggleTheme, applyTheme, toggleSidebar, toggleLearningMode,
    setColorScheme, getColor,
  }
})
