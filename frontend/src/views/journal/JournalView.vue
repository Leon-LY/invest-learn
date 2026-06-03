<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import EmptyState from '@/components/common/EmptyState.vue'

interface Note {
  id: number
  title: string
  content: string
  tags: string[]
  created_at: string
}

const notes = ref<Note[]>(JSON.parse(localStorage.getItem('invest-notes') || '[]'))
const showEditor = ref(false)
const editNote = ref<Note | null>(null)
const formTitle = ref('')
const formContent = ref('')
const formTags = ref('')

function openEditor(note?: Note) {
  if (note) {
    editNote.value = note
    formTitle.value = note.title
    formContent.value = note.content
    formTags.value = note.tags.join(', ')
  } else {
    editNote.value = null
    formTitle.value = ''
    formContent.value = ''
    formTags.value = ''
  }
  showEditor.value = true
}

function saveNote() {
  if (!formTitle.value.trim()) return

  const tags = formTags.value.split(',').map(t => t.trim()).filter(Boolean)

  if (editNote.value) {
    const idx = notes.value.findIndex(n => n.id === editNote.value!.id)
    if (idx >= 0) {
      notes.value[idx] = {
        ...notes.value[idx],
        title: formTitle.value,
        content: formContent.value,
        tags,
      }
    }
  } else {
    notes.value.unshift({
      id: Date.now(),
      title: formTitle.value,
      content: formContent.value,
      tags,
      created_at: new Date().toISOString(),
    })
  }

  localStorage.setItem('invest-notes', JSON.stringify(notes.value))
  showEditor.value = false
}

function deleteNote(id: number) {
  if (!confirm('确定删除这条笔记？')) return
  notes.value = notes.value.filter(n => n.id !== id)
  localStorage.setItem('invest-notes', JSON.stringify(notes.value))
}
</script>

<template>
  <AppShell>
    <div class="max-w-3xl mx-auto px-4 py-4 space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold dark:text-white">投资笔记</h1>
          <p class="text-sm text-gray-400 mt-1">记录投资心得、反思与学习笔记</p>
        </div>
        <button @click="openEditor()" class="px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors flex items-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          写笔记
        </button>
      </div>

      <!-- Editor Modal -->
      <div v-if="showEditor" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="showEditor = false">
        <div class="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
          <h2 class="text-lg font-bold dark:text-white">{{ editNote ? '编辑笔记' : '新建笔记' }}</h2>
          <input
            v-model="formTitle"
            placeholder="标题..."
            class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <textarea
            v-model="formContent"
            placeholder="写下你的投资思考、学习心得..."
            rows="6"
            class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <input
            v-model="formTags"
            placeholder="标签（用逗号分隔，如：价值投资, 茅台）"
            class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <div class="flex gap-2 justify-end">
            <button @click="showEditor = false" class="px-4 py-2 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">取消</button>
            <button @click="saveNote" class="px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors">保存</button>
          </div>
        </div>
      </div>

      <!-- Notes list -->
      <EmptyState v-if="!notes.length" message="还没有笔记，记录你的投资心得与反思" />
      <div v-else class="space-y-3">
        <div
          v-for="note in notes" :key="note.id"
          class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800 hover:shadow-sm transition-shadow"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 cursor-pointer" @click="openEditor(note)">
              <h3 class="font-medium text-sm dark:text-white">{{ note.title }}</h3>
              <p class="text-xs text-gray-400 mt-1 line-clamp-3">{{ note.content }}</p>
              <div v-if="note.tags.length" class="flex gap-1 mt-2">
                <span v-for="t in note.tags" :key="t" class="px-1.5 py-0.5 text-xs bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80 rounded">{{ t }}</span>
              </div>
              <div class="text-xs text-gray-400 mt-2">{{ note.created_at.slice(0, 10) }}</div>
            </div>
            <button @click="deleteNote(note.id)" class="p-1 text-gray-300 hover:text-red-500 transition-colors shrink-0">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
