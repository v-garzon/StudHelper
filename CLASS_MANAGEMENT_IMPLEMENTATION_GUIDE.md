# Class Management System - Implementation Guide

## 1. FILE MIGRATION PLAN

### Current Structure → New Structure

```
MOVE THESE FILES:
Vue-Frontend/src/components/features/
├── class-management/
│   ├── modals/CreateClassWizard/index.vue
│   └── panels/ClassInfoPanel.vue
│
└── dashboard/
    ├── Sidebar.vue (MODIFY - add info button)
    ├── ChatInterface.vue (exists)
    ├── UserMenu.vue (exists)
    ├── WelcomeScreen.vue (DELETE - will be replaced)
    └── VerificationBanner.vue (exists)
```

**MIGRATION STEPS:**

```bash
# 1. DELETE old files
rm Vue-Frontend/src/components/features/class-management/modals/CreateClassWizard/index.vue
rm Vue-Frontend/src/components/features/dashboard/WelcomeScreen.vue

# 2. KEEP (but will modify later)
# - Vue-Frontend/src/components/features/class-management/panels/ClassInfoPanel.vue
# - Vue-Frontend/src/components/features/dashboard/Sidebar.vue

# 3. CREATE new structure (see below)
```

---

## 2. NEW FILE STRUCTURE

```
Vue-Frontend/src/components/features/class-management/
├── modals/
│   └── ClassModal.vue                    # NEW: Single modal (create/edit modes)
│
├── panels/
│   └── ClassInfoPanel.vue                # KEEP: Existing slide-out panel
│
├── forms/
│   ├── ClassInfoForm.vue                 # NEW: Name + description inputs
│   └── KnowledgeManager.vue              # NEW: Upload + file table
│
├── components/
│   ├── FileUploadZone.vue                # NEW: Drag-drop + browse
│   ├── FileTable.vue                     # NEW: Color-coded file list
│   ├── YouTubeInput.vue                  # NEW: YouTube URL input
│   └── DeleteClassSection.vue            # NEW: Delete class danger zone
│
└── views/
    ├── ClassWelcome.vue                  # NEW: Welcome when class selected
    └── ClassGrid.vue                     # NEW: Class cards grid

Vue-Frontend/src/components/features/dashboard/
├── Sidebar.vue                           # MODIFY: Info button already exists
├── UserMenu.vue                          # KEEP: No changes
├── ChatInterface.vue                     # KEEP: No changes (Phase 4)
└── VerificationBanner.vue                # KEEP: No changes

Vue-Frontend/src/stores/
└── classes.js                            # MODIFY: Add new actions/state

Vue-Frontend/src/services/
└── classService.js                       # NEW: API calls for classes

Vue-Frontend/src/components/ui/
├── ModalManager.vue                      # MODIFY: Update component registry
└── SlideOutManager.vue                   # KEEP: No changes
```

---

## 3. DATABASE SCHEMA CHANGES

### Migration SQL

```sql
-- ============================================
-- MIGRATION: Add description fields
-- ============================================

-- Add description to classes table
ALTER TABLE classes 
ADD COLUMN description TEXT;

-- Add description to documents table  
ALTER TABLE documents
ADD COLUMN description TEXT;

-- Add url field for YouTube videos
ALTER TABLE documents
ADD COLUMN url TEXT;

-- Add index for faster queries
CREATE INDEX idx_documents_class_id ON documents(class_id);
CREATE INDEX idx_documents_session_id ON documents(session_id);
```

### Updated Schemas

```python
# Backend/app/models/__init__.py

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)                    # ← NEW
    class_code = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ... rest of model

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    description = Column(Text)                    # ← NEW (user-provided)
    url = Column(Text)                            # ← NEW (for YouTube)
    
    scope = Column(Enum(DocumentScope), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    
    # ... rest of model
```

---

## 4. COMPONENT ARCHITECTURE

### Component Hierarchy

```
DashboardView
├── Sidebar (MODIFIED)
│   ├── [+ New Class] button → opens ClassModal (create mode)
│   └── Class Items
│       ├── [ℹ️] button → opens ClassModal (edit mode)
│       └── [+] button → (placeholder) Create chat session
│
└── Content Area
    ├── No class selected
    │   ├── User has 0 classes → ClassWelcome (variant: "no-classes")
    │   └── User has classes → ClassGrid
    │
    └── Class selected (no chat)
        └── ClassWelcome (variant: "class-selected")

ClassModal (create/edit modes)
├── ClassInfoForm
│   ├── Name input
│   └── Description textarea
│
├── KnowledgeManager
│   ├── FileUploadZone
│   │   ├── Drag & drop area
│   │   ├── [Browse Files] button
│   │   └── YouTubeInput
│   │
│   └── FileTable
│       └── Rows (color-coded: green/red/orange)
│
└── DeleteClassSection (edit mode only)
    └── [Delete Class] button
```

### Component Communication

```
┌─────────────────────────────────────────────────────┐
│                  COMPONENT FLOW                     │
└─────────────────────────────────────────────────────┘

User Action → Component → Store → API → Backend

Example: Create Class
━━━━━━━━━━━━━━━━━━━━
1. User fills ClassModal form
2. User uploads files → FileUploadZone
3. Files added to uploadQueue (Pinia state)
4. User clicks "Create Class"
5. ClassModal → classStore.createClass()
6. classStore → classService.createClass(data)
7. classService → POST /api/v1/classes
8. Backend creates class + documents
9. Backend returns class data
10. classStore updates state
11. ClassModal closes
12. Class auto-selected → ClassWelcome shows
```

---

## 5. USER FLOW DIAGRAMS

### Flow 1: Create Class

```
┌─────────────────────────────────────────────────────┐
│ User clicks [+ New Class] in Sidebar                │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ ClassModal opens (create mode)                      │
│ ┌─────────────────────────────────────────────┐     │
│ │ Class Name: [_______________________]       │     │
│ │ Description: [______________________]       │     │
│ │              [______________________]       │     │
│ │                                              │     │
│ │ Upload Content:                             │     │
│ │ ┌──────────────────────────────────────┐   │     │
│ │ │ [Drag files] or [Browse]             │   │     │
│ │ │ + Add YouTube Video                  │   │     │
│ │ └──────────────────────────────────────┘   │     │
│ │                                              │     │
│ │ Files:                                       │     │
│ │ ┌──────────────────────────────────────┐   │     │
│ │ │ file.pdf  2MB  [description_____]    │   │     │
│ │ │ video.mp4 10MB [description_____]    │   │     │
│ │ └──────────────────────────────────────┘   │     │
│ │                                              │     │
│ │        [Cancel]  [Create Class]             │     │
│ └─────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ API: POST /api/v1/classes                           │
│ Body: { name, description, files[] }                │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ Backend:                                            │
│ 1. Create class record                              │
│ 2. Generate unique class_code                       │
│ 3. Upload files to storage                          │
│ 4. Create document records                          │
│ 5. Return class data                                │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ Frontend:                                           │
│ 1. Add class to store                               │
│ 2. Auto-select new class                            │
│ 3. Close modal                                      │
│ 4. Show ClassWelcome (class-selected variant)      │
└─────────────────────────────────────────────────────┘
```

### Flow 2: Edit Class (Info Button)

```
┌─────────────────────────────────────────────────────┐
│ User clicks [ℹ️] next to class in Sidebar           │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ ClassModal opens (edit mode)                        │
│ - Pre-filled with class data                        │
│ - Shows existing documents                          │
│ - Can add/remove files                              │
│ - Can modify descriptions                           │
│ - Shows Delete Class section                        │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
  [Edit Info]   [Manage Knowledge]  [Delete]
        │               │               │
        ▼               ▼               ▼
  PUT /classes/{id}  POST/DELETE  DELETE /classes/{id}
                     /documents
```

### Flow 3: Welcome Screens

```
┌─────────────────────────────────────────────────────┐
│ User lands on Dashboard                             │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│ Has 0 classes    │          │ Has classes          │
└────────┬─────────┘          └────────┬─────────────┘
         │                              │
         ▼                    ┌─────────┴─────────────┐
┌─────────────────┐           │                       │
│ ClassWelcome    │           ▼                       ▼
│ (no-classes)    │  ┌────────────────┐    ┌──────────────────┐
│                 │  │ No class       │    │ Class selected   │
│ "Welcome!       │  │ selected       │    │ (no chat)        │
│  Create your    │  └────────┬───────┘    └──────────┬───────┘
│  first class"   │           │                       │
│                 │           ▼                       ▼
│ [+ New Class]   │  ┌────────────────┐    ┌──────────────────┐
└─────────────────┘  │ ClassGrid      │    │ ClassWelcome     │
                     │ (2x grid)      │    │ (class-selected) │
                     │                │    │                  │
                     │ [Class Cards]  │    │ "Welcome to      │
                     │  with chat     │    │  [Class Name]!"  │
                     │  counts        │    │                  │
                     └────────────────┘    │ [+ New Session]  │
                                           │  (placeholder)   │
                                           └──────────────────┘
```

---

## 6. API ENDPOINTS

### Class Management

```http
# Create new class
POST /api/v1/classes
Content-Type: multipart/form-data

Body:
  name: string (required)
  description: string (optional)
  files: File[] (optional)
  youtube_urls: string[] (optional)
  file_descriptions: { [filename]: description } (optional)

Response: 201 Created
{
  "id": 1,
  "name": "Physics 101",
  "description": "Intro to physics",
  "class_code": "PHYS101XYZ",
  "owner_id": 1,
  "created_at": "2025-10-10T10:00:00Z",
  "documents": [
    {
      "id": 1,
      "filename": "syllabus.pdf",
      "file_size": 2048576,
      "description": "Course syllabus",
      "uploaded_at": "2025-10-10T10:00:00Z"
    }
  ]
}

# List user's classes
GET /api/v1/classes

Response: 200 OK
{
  "classes": [
    {
      "id": 1,
      "name": "Physics 101",
      "description": "Intro to physics",
      "class_code": "PHYS101XYZ",
      "is_owner": true,
      "chat_session_count": 3,
      "document_count": 5,
      "member_count": 15
    }
  ]
}

# Get class details
GET /api/v1/classes/{id}

Response: 200 OK
{
  "id": 1,
  "name": "Physics 101",
  "description": "Intro to physics",
  "class_code": "PHYS101XYZ",
  "owner_id": 1,
  "is_owner": true,
  "documents": [...],
  "members": [...],
  "chat_sessions": [...]
}

# Update class info
PUT /api/v1/classes/{id}
Content-Type: application/json

Body:
{
  "name": "Physics 101 - Updated",
  "description": "Updated description"
}

Response: 200 OK
{
  "id": 1,
  "name": "Physics 101 - Updated",
  ...
}

# Delete class (owner only)
DELETE /api/v1/classes/{id}

Response: 204 No Content
```

### Document Management

```http
# Upload documents to class
POST /api/v1/documents/classes/{class_id}/upload
Content-Type: multipart/form-data

Body:
  file: File (required)
  description: string (optional)
  # OR
  youtube_url: string (required)
  description: string (optional)

Response: 201 Created
{
  "id": 1,
  "filename": "lecture1.pdf",
  "file_size": 1048576,
  "file_type": "pdf",
  "description": "First lecture notes",
  "scope": "class",
  "class_id": 1,
  "processing_status": "pending"
}

# List class documents
GET /api/v1/documents/classes/{class_id}

Response: 200 OK
{
  "documents": [
    {
      "id": 1,
      "filename": "lecture1.pdf",
      "original_filename": "Lecture 1.pdf",
      "file_size": 1048576,
      "file_type": "pdf",
      "description": "First lecture",
      "uploaded_at": "2025-10-10T10:00:00Z",
      "processing_status": "completed"
    },
    {
      "id": 2,
      "filename": "YouTube: Introduction",
      "url": "https://youtube.com/watch?v=xyz",
      "file_size": 0,
      "file_type": "youtube",
      "description": "Intro video",
      "uploaded_at": "2025-10-10T11:00:00Z",
      "processing_status": "pending"
    }
  ]
}

# Update document description
PUT /api/v1/documents/{id}
Content-Type: application/json

Body:
{
  "description": "Updated description"
}

Response: 200 OK

# Delete document
DELETE /api/v1/documents/{id}

Response: 204 No Content
```

### Chat Sessions (Placeholder)

```http
# Create chat session (PLACEHOLDER - Phase 4)
POST /api/v1/chat/sessions
Content-Type: application/json

Body:
{
  "class_id": 1,
  "title": "Questions about Chapter 1"
}

Response: 201 Created
{
  "id": 1,
  "class_id": 1,
  "title": "Questions about Chapter 1",
  "created_at": "2025-10-10T10:00:00Z"
}

# List chat sessions for class
GET /api/v1/chat/sessions?class_id={id}

Response: 200 OK
{
  "sessions": [...]
}
```

---

## 7. PINIA STORE UPDATES

### classes.js

```javascript
// stores/classes.js

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import classService from '@/services/classService'

export const useClassStore = defineStore('classes', () => {
  // ==========================================
  // STATE
  // ==========================================
  
  const classes = ref([])
  const selectedClass = ref(null)
  const currentChat = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Upload management
  const uploadQueue = ref([])
  const uploadProgress = ref({})
  
  // ==========================================
  // GETTERS
  // ==========================================
  
  const hasClasses = computed(() => classes.value.length > 0)
  
  const selectedClassId = computed(() => {
    return selectedClass.value?.id || localStorage.getItem('selectedClassId')
  })
  
  // ==========================================
  // ACTIONS
  // ==========================================
  
  /**
   * Fetch all classes for current user
   */
  async function fetchClasses() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await classService.getClasses()
      classes.value = response.classes
      
      // Auto-select from localStorage
      const savedId = localStorage.getItem('selectedClassId')
      if (savedId) {
        const savedClass = classes.value.find(c => c.id === parseInt(savedId))
        if (savedClass) {
          selectedClass.value = savedClass
        }
      }
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch classes:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Create new class with files
   */
  async function createClass(classData) {
    isLoading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('name', classData.name)
      formData.append('description', classData.description || '')
      
      // Add files with descriptions
      classData.files.forEach((fileObj, index) => {
        formData.append('files', fileObj.file)
        if (fileObj.description) {
          formData.append(`file_descriptions[${fileObj.file.name}]`, fileObj.description)
        }
      })
      
      // Add YouTube URLs with descriptions
      if (classData.youtubeVideos?.length) {
        classData.youtubeVideos.forEach((video, index) => {
          formData.append(`youtube_urls[${index}]`, video.url)
          if (video.description) {
            formData.append(`youtube_descriptions[${index}]`, video.description)
          }
        })
      }
      
      const newClass = await classService.createClass(formData)
      
      // Add to classes list
      classes.value.push(newClass)
      
      // Auto-select new class
      selectClass(newClass)
      
      return newClass
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Update class info
   */
  async function updateClass(classId, updates) {
    isLoading.value = true
    error.value = null
    
    try {
      const updatedClass = await classService.updateClass(classId, updates)
      
      // Update in list
      const index = classes.value.findIndex(c => c.id === classId)
      if (index !== -1) {
        classes.value[index] = { ...classes.value[index], ...updatedClass }
      }
      
      // Update selected if it's the current class
      if (selectedClass.value?.id === classId) {
        selectedClass.value = { ...selectedClass.value, ...updatedClass }
      }
      
      return updatedClass
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Delete class
   */
  async function deleteClass(classId) {
    isLoading.value = true
    error.value = null
    
    try {
      await classService.deleteClass(classId)
      
      // Remove from list
      classes.value = classes.value.filter(c => c.id !== classId)
      
      // Clear selection if deleted class was selected
      if (selectedClass.value?.id === classId) {
        selectedClass.value = null
        localStorage.removeItem('selectedClassId')
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Select a class
   */
  function selectClass(classItem) {
    selectedClass.value = classItem
    currentChat.value = null // Clear chat when switching classes
    localStorage.setItem('selectedClassId', classItem.id.toString())
  }
  
  /**
   * Clear class selection
   */
  function clearClassSelection() {
    selectedClass.value = null
    currentChat.value = null
    localStorage.removeItem('selectedClassId')
  }
  
  /**
   * Select a chat (placeholder for Phase 4)
   */
  function selectChat(chat) {
    currentChat.value = chat
  }
  
  /**
   * Add file to upload queue
   */
  function addToUploadQueue(file, description = '') {
    const fileObj = {
      id: Date.now() + Math.random(),
      file,
      description,
      status: 'new', // 'new' | 'uploading' | 'completed' | 'error'
      progress: 0
    }
    uploadQueue.value.push(fileObj)
    return fileObj
  }
  
  /**
   * Remove file from upload queue
   */
  function removeFromUploadQueue(fileId) {
    uploadQueue.value = uploadQueue.value.filter(f => f.id !== fileId)
  }
  
  /**
   * Update file description in queue
   */
  function updateFileDescription(fileId, description) {
    const file = uploadQueue.value.find(f => f.id === fileId)
    if (file) {
      file.description = description
      file.status = 'modified'
    }
  }
  
  /**
   * Clear upload queue
   */
  function clearUploadQueue() {
    uploadQueue.value = []
    uploadProgress.value = {}
  }
  
  return {
    // State
    classes,
    selectedClass,
    currentChat,
    isLoading,
    error,
    uploadQueue,
    uploadProgress,
    
    // Getters
    hasClasses,
    selectedClassId,
    
    // Actions
    fetchClasses,
    createClass,
    updateClass,
    deleteClass,
    selectClass,
    clearClassSelection,
    selectChat,
    addToUploadQueue,
    removeFromUploadQueue,
    updateFileDescription,
    clearUploadQueue
  }
})
```

---

## 8. COMPONENT PSEUDOCODE

### ClassModal.vue

```vue
<template>
  <ModalWrapper @close="handleClose">
    <div class="modal-content">
      <h2>{{ isEditMode ? 'Edit Class' : 'Create New Class' }}</h2>
      
      <!-- Class Info Form -->
      <ClassInfoForm 
        v-model:name="classData.name"
        v-model:description="classData.description"
        :errors="validationErrors"
      />
      
      <!-- Knowledge Manager -->
      <KnowledgeManager 
        v-model:files="classData.files"
        v-model:youtubeVideos="classData.youtubeVideos"
        :existing-documents="existingDocuments"
        :mode="isEditMode ? 'edit' : 'create'"
        @file-deleted="handleFileDeleted"
      />
      
      <!-- Delete Section (edit mode only) -->
      <DeleteClassSection 
        v-if="isEditMode"
        :class-name="classData.name"
        @delete="handleDelete"
      />
      
      <!-- Actions -->
      <div class="modal-actions">
        <button @click="handleClose">Cancel</button>
        <button @click="handleSubmit" :disabled="!isValid">
          {{ isEditMode ? 'Save Changes' : 'Create Class' }}
        </button>
      </div>
    </div>
  </ModalWrapper>
</template>

<script setup>
// PSEUDOCODE

props: {
  mode: 'create' | 'edit',
  classId: number (if edit mode)
}

data: {
  classData: {
    name: '',
    description: '',
    files: [], // Array of { id, file, description, status }
    youtubeVideos: [] // Array of { id, url, description, status }
  },
  existingDocuments: [], // Only for edit mode
  validationErrors: {},
  isLoading: false
}

computed: {
  isEditMode: mode === 'edit',
  isValid: name.length > 0
}

methods: {
  async handleSubmit() {
    if (isEditMode) {
      // 1. Update class info
      await classStore.updateClass(classId, {
        name: classData.name,
        description: classData.description
      })
      
      // 2. Handle file operations
      for (file in classData.files) {
        if (file.status === 'new') {
          // Upload new file
          await uploadDocument(file)
        } else if (file.status === 'modified') {
          // Update description
          await updateDocumentDescription(file.id, file.description)
        } else if (file.status === 'deleted') {
          // Delete file
          await deleteDocument(file.id)
        }
      }
    } else {
      // Create new class
      await classStore.createClass(classData)
    }
    
    emit('close')
  },
  
  handleFileDeleted(fileId) {
    // Mark file as deleted (red background)
    const file = classData.files.find(f => f.id === fileId)
    if (file) {
      file.status = 'deleted'
    }
  },
  
  handleDelete() {
    if (confirm('Are you sure you want to delete this class?')) {
      await classStore.deleteClass(classId)
      emit('close')
    }
  }
}

lifecycle: {
  onMounted() {
    if (isEditMode) {
      // Fetch class details
      loadClassData(classId)
    }
  }
}
</script>
```

### FileUploadZone.vue

```vue
<template>
  <div class="upload-zone">
    <!-- Drag & Drop Area -->
    <div 
      class="drop-zone"
      :class="{ 'drag-over': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div class="drop-content">
        <svg>📁</svg>
        <p>Drag files here or</p>
        <button @click="triggerFileInput">Browse Files</button>
      </div>
      <input 
        ref="fileInput"
        type="file"
        multiple
        accept=".pdf,.docx,.xlsx,.pptx,.txt"
        @change="handleFileSelect"
        hidden
      />
    </div>
    
    <!-- YouTube Input -->
    <YouTubeInput @video-added="handleYouTubeVideo" />
  </div>
</template>

<script setup>
// PSEUDOCODE

data: {
  isDragging: false
}

methods: {
  handleDrop(event) {
    isDragging = false
    const files = Array.from(event.dataTransfer.files)
    processFiles(files)
  },
  
  handleFileSelect(event) {
    const files = Array.from(event.target.files)
    processFiles(files)
  },
  
  processFiles(files) {
    // Validate each file
    for (file of files) {
      if (validateFile(file)) {
        emit('file-added', {
          id: generateId(),
          file: file,
          description: '',
          status: 'new'
        })
      } else {
        showError(`Invalid file: ${file.name}`)
      }
    }
  },
  
  validateFile(file) {
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      return false
    }
    
    // Check file type
    const allowedTypes = ['pdf', 'docx', 'xlsx', 'pptx', 'txt']
    const ext = file.name.split('.').pop().toLowerCase()
    return allowedTypes.includes(ext)
  },
  
  handleYouTubeVideo(videoData) {
    emit('youtube-added', videoData)
  }
}
</script>
```

### FileTable.vue

```vue
<template>
  <div class="file-table-container">
    <table class="file-table">
      <thead>
        <tr>
          <th>Filename</th>
          <th>Size</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="file in files" 
          :key="file.id"
          :class="getRowClass(file)"
        >
          <td>
            <div class="filename">
              <svg>{{ getFileIcon(file) }}</svg>
              <span>{{ file.filename || file.file.name }}</span>
            </div>
          </td>
          <td>{{ formatFileSize(file) }}</td>
          <td>
            <input 
              v-model="file.description"
              type="text"
              placeholder="Add description..."
              @input="handleDescriptionChange(file)"
            />
          </td>
          <td>
            <button @click="handleDelete(file)" class="delete-btn">
              <svg>🗑️</svg>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
// PSEUDOCODE

props: {
  files: Array, // Array of file objects
  mode: 'create' | 'edit'
}

methods: {
  getRowClass(file) {
    // Color-coded rows based on status
    if (file.status === 'new') return 'bg-green-50'
    if (file.status === 'deleted') return 'bg-red-50'
    if (file.status === 'modified') return 'bg-orange-50'
    return ''
  },
  
  getFileIcon(file) {
    const type = file.file_type || file.file.name.split('.').pop()
    return FILE_TYPE_ICONS[type] || '📄'
  },
  
  formatFileSize(file) {
    if (file.file_type === 'youtube') {
      return 'duration' // Placeholder - will get from YouTube API
    }
    
    const bytes = file.file_size || file.file.size
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  },
  
  handleDescriptionChange(file) {
    // Mark as modified if in edit mode
    if (mode === 'edit' && file.status !== 'new') {
      file.status = 'modified'
    }
    emit('description-changed', file)
  },
  
  handleDelete(file) {
    if (mode === 'create') {
      // Remove from queue immediately
      emit('file-removed', file.id)
    } else {
      // Mark as deleted (will show with red background)
      file.status = 'deleted'
      emit('file-deleted', file.id)
    }
  }
}
</script>
```

### ClassWelcome.vue

```vue
<template>
  <div class="welcome-container">
    <!-- No Classes Variant -->
    <div v-if="variant === 'no-classes'" class="welcome-no-classes">
      <div class="welcome-icon">🎓</div>
      <h1>Welcome to StudHelper!</h1>
      <p>Create your first class to get started with AI-powered learning.</p>
      <button @click="openCreateClassModal" class="primary-button">
        + Create Your First Class
      </button>
    </div>
    
    <!-- Class Selected Variant -->
    <div v-else-if="variant === 'class-selected'" class="welcome-class-selected">
      <div class="class-header">
        <div class="class-icon">📚</div>
        <div class="class-info">
          <h1>{{ className }}</h1>
          <p class="class-description">{{ classDescription }}</p>
        </div>
      </div>
      
      <div class="welcome-message">
        <h2>Ready to learn?</h2>
        <p>Create a new chat session to start asking questions about your materials.</p>
      </div>
      
      <button @click="createChatSession" class="primary-button" disabled>
        + New Chat Session
        <span class="placeholder-badge">Phase 4</span>
      </button>
      
      <div class="class-stats">
        <div class="stat">
          <span class="stat-value">{{ documentCount }}</span>
          <span class="stat-label">Documents</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ sessionCount }}</span>
          <span class="stat-label">Chat Sessions</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// PSEUDOCODE

props: {
  variant: 'no-classes' | 'class-selected',
  className: string,
  classDescription: string,
  documentCount: number,
  sessionCount: number
}

methods: {
  openCreateClassModal() {
    uiStore.openModal('ClassModal', { mode: 'create' })
  },
  
  createChatSession() {
    // PLACEHOLDER - Phase 4
    console.log('Chat session creation coming in Phase 4')
  }
}
</script>
```

### ClassGrid.vue

```vue
<template>
  <div class="class-grid-container">
    <div class="grid-header">
      <h2>Your Classes</h2>
      <button @click="openCreateClassModal" class="secondary-button">
        + New Class
      </button>
    </div>
    
    <div class="class-grid">
      <div 
        v-for="classItem in classes" 
        :key="classItem.id"
        class="class-card"
        @click="selectClass(classItem)"
      >
        <div class="card-icon">📚</div>
        <h3 class="card-title">{{ classItem.name }}</h3>
        <p class="card-description">{{ classItem.description || 'No description' }}</p>
        <div class="card-footer">
          <span class="chat-count">
            <svg>💬</svg>
            {{ classItem.chat_session_count || 0 }} chat sessions
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// PSEUDOCODE

props: {
  classes: Array
}

methods: {
  selectClass(classItem) {
    classStore.selectClass(classItem)
  },
  
  openCreateClassModal() {
    uiStore.openModal('ClassModal', { mode: 'create' })
  }
}

computed: {
  // Classes displayed in 2-column grid
  // CSS: grid-template-columns: repeat(2, 1fr)
}
</script>

<style>
.class-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.class-card {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.class-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
</style>
```

---

## 9. BACKEND SERVICE STRUCTURE

### Class Service

```python
# Backend/app/services/class_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models import Class, ClassMembership, Document, DocumentScope
from app.schemas import ClassCreate, ClassResponse
import random
import string

class ClassService:
    
    @staticmethod
    def generate_class_code() -> str:
        """Generate unique 8-character class code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    @staticmethod
    async def create_class(
        db: Session, 
        name: str, 
        description: str,
        owner_id: int,
        files: list[UploadFile] = None,
        file_descriptions: dict = None,
        youtube_urls: list[str] = None,
        youtube_descriptions: list[str] = None
    ) -> ClassResponse:
        """Create new class with optional documents"""
        
        # 1. Generate unique class code
        while True:
            class_code = ClassService.generate_class_code()
            existing = db.query(Class).filter(Class.class_code == class_code).first()
            if not existing:
                break
        
        # 2. Create class
        new_class = Class(
            name=name,
            description=description,
            class_code=class_code,
            owner_id=owner_id
        )
        db.add(new_class)
        db.flush()
        
        # 3. Create owner membership
        owner_membership = ClassMembership(
            user_id=owner_id,
            class_id=new_class.id,
            is_manager=True,
            can_chat=True,
            daily_token_limit=100000,
            is_sponsored=True
        )
        db.add(owner_membership)
        
        # 4. Process file uploads (if any)
        if files:
            for file in files:
                description = file_descriptions.get(file.filename, '') if file_descriptions else ''
                # PLACEHOLDER: Full implementation in Phase 3
                document = Document(
                    filename=file.filename,
                    original_filename=file.filename,
                    file_path=f"uploads/{new_class.id}/{file.filename}",
                    file_type=file.filename.split('.')[-1],
                    file_size=0,  # TODO: Get actual size
                    description=description,
                    scope=DocumentScope.CLASS,
                    class_id=new_class.id,
                    uploaded_by=owner_id
                )
                db.add(document)
        
        # 5. Process YouTube videos (if any)
        if youtube_urls:
            for i, url in enumerate(youtube_urls):
                description = youtube_descriptions[i] if youtube_descriptions and i < len(youtube_descriptions) else ''
                video_id = extract_youtube_id(url)
                document = Document(
                    filename=f"YouTube: {video_id}",
                    original_filename=url,
                    file_path="",
                    file_type="youtube",
                    file_size=0,
                    description=description,
                    url=url,
                    scope=DocumentScope.CLASS,
                    class_id=new_class.id,
                    uploaded_by=owner_id
                )
                db.add(document)
        
        db.commit()
        db.refresh(new_class)
        
        return new_class
    
    @staticmethod
    def get_user_classes(db: Session, user_id: int) -> list[ClassResponse]:
        """Get all classes user is member of"""
        
        # Get classes where user is member
        memberships = db.query(ClassMembership).filter(
            ClassMembership.user_id == user_id
        ).all()
        
        classes = []
        for membership in memberships:
            class_obj = db.query(Class).filter(Class.id == membership.class_id).first()
            if class_obj:
                # Add extra data
                class_obj.is_owner = class_obj.owner_id == user_id
                class_obj.chat_session_count = len(class_obj.chat_sessions)
                class_obj.document_count = len(class_obj.documents)
                classes.append(class_obj)
        
        return classes
    
    @staticmethod
    def get_class_details(db: Session, class_id: int, user_id: int) -> ClassResponse:
        """Get detailed class information"""
        
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check if user is member
        membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.user_id == user_id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this class")
        
        class_obj.is_owner = class_obj.owner_id == user_id
        return class_obj
    
    @staticmethod
    def update_class(db: Session, class_id: int, user_id: int, name: str = None, description: str = None):
        """Update class information (owner only)"""
        
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        if class_obj.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only owner can update class")
        
        if name:
            class_obj.name = name
        if description is not None:
            class_obj.description = description
        
        db.commit()
        db.refresh(class_obj)
        return class_obj
    
    @staticmethod
    def delete_class(db: Session, class_id: int, user_id: int):
        """Delete class (owner only)"""
        
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        if class_obj.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only owner can delete class")
        
        # Delete all related records (CASCADE should handle this)
        db.delete(class_obj)
        db.commit()


def extract_youtube_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    # Simple implementation - can be improved
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'watch?v=' in url:
        return url.split('watch?v=')[1].split('&')[0]
    return url
```

---

## 10. IMPLEMENTATION CHECKLIST

### Phase 2A: File Structure & Database

- [ ] **File Migration**
  - [ ] Delete `CreateClassWizard/index.vue`
  - [ ] Delete `dashboard/WelcomeScreen.vue`
  - [ ] Create new folder structure
  - [ ] Update component imports in `ModalManager.vue`

- [ ] **Database Migration**
  - [ ] Create Alembic migration file
  - [ ] Add `description` to `classes` table
  - [ ] Add `description` to `documents` table
  - [ ] Add `url` to `documents` table
  - [ ] Run migration: `alembic upgrade head`

### Phase 2B: Backend (3-4 hours)

- [ ] **Class Routes** (`Backend/app/routes/classes.py`)
  - [ ] `POST /api/v1/classes` - Create class
  - [ ] `GET /api/v1/classes` - List classes
  - [ ] `GET /api/v1/classes/{id}` - Get class details
  - [ ] `PUT /api/v1/classes/{id}` - Update class
  - [ ] `DELETE /api/v1/classes/{id}` - Delete class

- [ ] **Document Routes** (`Backend/app/routes/documents.py`)
  - [ ] `POST /api/v1/documents/classes/{id}/upload` - Upload file
  - [ ] `GET /api/v1/documents/classes/{id}` - List documents
  - [ ] `PUT /api/v1/documents/{id}` - Update description
  - [ ] `DELETE /api/v1/documents/{id}` - Delete document

- [ ] **Services**
  - [ ] `class_service.py` - Business logic
  - [ ] Update `document_service.py` - Add description support

- [ ] **Schemas** (`Backend/app/schemas/`)
  - [ ] `ClassCreate`, `ClassUpdate`, `ClassResponse`
  - [ ] Update `DocumentResponse` with description/url

### Phase 2C: Frontend Core (4-5 hours)

- [ ] **API Service** (`services/classService.js`)
  - [ ] `createClass(formData)`
  - [ ] `getClasses()`
  - [ ] `getClassDetails(id)`
  - [ ] `updateClass(id, data)`
  - [ ] `deleteClass(id)`

- [ ] **Pinia Store** (`stores/classes.js`)
  - [ ] Implement all actions from pseudocode
  - [ ] Add upload queue management
  - [ ] Add localStorage persistence

### Phase 2D: UI Components (6-8 hours)

- [ ] **Modal Components**
  - [ ] `ClassModal.vue` (create/edit modes)
  - [ ] Update `ModalManager.vue` registry

- [ ] **Form Components**
  - [ ] `ClassInfoForm.vue`
  - [ ] `KnowledgeManager.vue`

- [ ] **Upload Components**
  - [ ] `FileUploadZone.vue`
  - [ ] `FileTable.vue`
  - [ ] `YouTubeInput.vue`
  - [ ] `DeleteClassSection.vue`

- [ ] **View Components**
  - [ ] `ClassWelcome.vue` (2 variants)
  - [ ] `ClassGrid.vue`

- [ ] **Sidebar Update**
  - [ ] Info button already exists
  - [ ] Update `openClassInfo()` to open `ClassModal` in edit mode

### Phase 2E: Integration & Testing (2-3 hours)

- [ ] **User Flow Testing**
  - [ ] Test create class flow
  - [ ] Test edit class flow
  - [ ] Test delete class flow
  - [ ] Test class selection
  - [ ] Test welcome screen variants

- [ ] **Error Handling**
  - [ ] API error messages
  - [ ] Validation errors
  - [ ] File upload errors

- [ ] **UI Polish**
  - [ ] Loading states
  - [ ] Empty states
  - [ ] Color-coded file rows
  - [ ] Hover effects
  - [ ] Responsive design

---

## 11. MAJOR CHANGES SUMMARY

### Database
- Added `description` field to `classes` and `documents` tables
- Added `url` field to `documents` table (for YouTube)

### Backend
- New class management routes and service
- Document upload support (placeholder - full in Phase 3)
- Class code generation

### Frontend
- Complete file structure reorganization
- New modal system (create/edit in one component)
- Upload queue management in Pinia
- Color-coded file status (green/red/orange)
- Welcome screen variants based on state
- Class grid view (2x2 cards)
- localStorage persistence for selected class

### User Experience
- Single-step class creation (simplified from 3-step wizard)
- Inline file upload with descriptions
- YouTube video support
- Visual feedback for file status
- Auto-select newly created class

---

## 12. MINOR CHANGES & NOTES

- **Sidebar**: Info button already exists, just needs to open `ClassModal` in edit mode
- **Chat Sessions**: Count shown but creation is placeholder (Phase 4)
- **Document Processing**: Files uploaded but not processed yet (Phase 3)
- **File Size**: Stored but not enforced yet (Phase 3)
- **Permissions**: Not implemented yet (later in Phase 2)

---

## NEXT STEPS AFTER COMPLETION

After implementing this class management system, you'll be ready for:

1. **Phase 3**: Document processing (text extraction, embeddings, vector storage)
2. **Phase 4**: Chat interface (AI conversations with RAG)
3. **Permissions**: Member management, token limits, sponsorship

---

**Total Estimated Time: 15-20 hours**
- Backend: 3-4 hours
- Frontend: 10-13 hours  
- Testing: 2-3 hours

Ready to start coding! 🚀
