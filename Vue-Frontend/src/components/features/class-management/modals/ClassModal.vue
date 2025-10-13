<template>
  <ModalWrapper @close="handleClose">
    <div class="modal-content max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="modal-header px-6 py-4 border-b border-gray-200">
        <h2 class="text-2xl font-semibold text-gray-900">
          {{ isEditMode ? 'Edit Class' : 'Create New Class' }}
        </h2>
      </div>

      <!-- Content -->
      <div class="modal-body px-6 py-4 space-y-6">
        <!-- Class Info Form -->
        <ClassInfoForm 
          v-model:name="classData.name"
          v-model:description="classData.description"
          :errors="validationErrors"
        />

        <!-- Knowledge Manager -->
        <KnowledgeManager 
          :files="uploadQueue"
          :mode="mode"
          @file-added="handleFileAdded"
          @file-removed="handleFileRemoved"
          @description-changed="handleDescriptionChanged"
          @youtube-added="handleYouTubeAdded"
        />

        <!-- Delete Section (edit mode only) -->
        <DeleteClassSection 
          v-if="isEditMode"
          :class-name="classData.name"
          :is-deleting="isDeleting"
          @delete="handleDelete"
        />
      </div>

      <!-- Footer -->
      <div class="modal-footer px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
        <button 
          @click="handleClose"
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          :disabled="isSubmitting || isDeleting"
        >
          Cancel
        </button>
        <button 
          @click="handleSubmit"
          :disabled="!isValid || isSubmitting"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="isSubmitting">
            {{ isEditMode ? 'Saving...' : 'Creating...' }}
          </span>
          <span v-else>
            {{ isEditMode ? 'Save Changes' : 'Create Class' }}
          </span>
        </button>
      </div>
    </div>
  </ModalWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useClassStore } from '@/stores/classes'
import { useUIStore } from '@/stores/ui'
import ModalWrapper from '@/components/ui/ModalWrapper.vue'
import ClassInfoForm from '../forms/ClassInfoForm.vue'
import KnowledgeManager from '../forms/KnowledgeManager.vue'
import DeleteClassSection from '../components/DeleteClassSection.vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'edit'].includes(value)
  },
  classId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['close'])

const classStore = useClassStore()
const uiStore = useUIStore()

const classData = ref({
  name: '',
  description: ''
})

const validationErrors = ref({})
const isSubmitting = ref(false)
const isDeleting = ref(false)

const isEditMode = computed(() => props.mode === 'edit')
const uploadQueue = computed(() => classStore.uploadQueue)

const isValid = computed(() => {
  return classData.value.name.trim().length > 0
})

onMounted(async () => {
  // Clear upload queue
  classStore.clearUploadQueue()
  
  if (isEditMode.value && props.classId) {
    // Fetch class details
    try {
      const classDetails = await classStore.fetchClassDetails(props.classId)
      classData.value.name = classDetails.name
      classData.value.description = classDetails.description || ''
      
      // Add existing documents to queue
      classDetails.documents.forEach(doc => {
        classStore.addExistingToQueue(doc)
      })
    } catch (error) {
      console.error('Failed to fetch class details:', error)
    }
  }
})

async function handleSubmit() {
  if (!isValid.value || isSubmitting.value) return
  
  isSubmitting.value = true
  validationErrors.value = {}
  
  try {
    if (isEditMode.value) {
      // Update class info
      await classStore.updateClass(props.classId, {
        name: classData.value.name,
        description: classData.value.description
      })
      
      // Handle file operations
      const filesToProcess = uploadQueue.value.filter(f => 
        f.status === 'new' || f.status === 'modified' || f.status === 'deleted'
      )
      
      for (const fileObj of filesToProcess) {
        if (fileObj.status === 'new') {
          // Upload new file
          if (fileObj.isYouTube) {
            await classStore.uploadYouTubeVideo(
              props.classId,
              fileObj.url,
              fileObj.description
            )
          } else {
            await classStore.uploadDocument(
              props.classId,
              fileObj.file,
              fileObj.description
            )
          }
        } else if (fileObj.status === 'modified') {
          // Update description
          await classStore.updateDocumentDescription(
            fileObj.id,
            fileObj.description
          )
        } else if (fileObj.status === 'deleted') {
          // Delete file
          await classStore.deleteDocument(fileObj.id)
        }
      }
      
      // Refresh class details
      await classStore.fetchClassDetails(props.classId)
    } else {
      // Create new class
      const newFiles = uploadQueue.value.filter(f => !f.isYouTube)
      const youtubeVideos = uploadQueue.value.filter(f => f.isYouTube)
      
      await classStore.createClass({
        name: classData.value.name,
        description: classData.value.description,
        files: newFiles,
        youtubeVideos: youtubeVideos
      })
    }
    
    handleClose()
  } catch (error) {
    console.error('Failed to save class:', error)
    validationErrors.value.submit = error.message || 'Failed to save class'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete() {
  if (!props.classId) return
  
  const confirmed = confirm(
    `Are you sure you want to delete "${classData.value.name}"? This action cannot be undone.`
  )
  
  if (!confirmed) return
  
  isDeleting.value = true
  
  try {
    await classStore.deleteClass(props.classId)
    handleClose()
  } catch (error) {
    console.error('Failed to delete class:', error)
    alert('Failed to delete class. Please try again.')
  } finally {
    isDeleting.value = false
  }
}

function handleFileAdded(fileObj) {
  classStore.addToUploadQueue(fileObj.file, fileObj.description)
}

function handleFileRemoved(fileId) {
  classStore.removeFromUploadQueue(fileId)
}

function handleDescriptionChanged({ fileId, description }) {
  classStore.updateFileDescription(fileId, description)
}

function handleYouTubeAdded(videoData) {
  const videoObj = {
    id: Date.now() + Math.random(),
    url: videoData.url,
    description: videoData.description || '',
    status: 'new',
    isYouTube: true,
    isExisting: false
  }
  classStore.uploadQueue.push(videoObj)
}

function handleClose() {
  classStore.clearUploadQueue()
  emit('close')
}
</script>


