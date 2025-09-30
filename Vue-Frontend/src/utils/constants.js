export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    PROFILE: '/auth/profile'
  },
  CLASSES: {
    LIST: '/classes',
    CREATE: '/classes',
    DETAIL: '/classes/{id}',
    JOIN: '/classes/join',
    MEMBERS: '/classes/{id}/members'
  },
  CHAT: {
    SESSIONS: '/chat/sessions',
    MESSAGES: '/chat/sessions/{id}/messages'
  },
  DOCUMENTS: {
    CLASS_UPLOAD: '/documents/classes/{id}/upload',
    CHAT_UPLOAD: '/documents/sessions/{id}/upload',
    CLASS_LIST: '/documents/classes/{id}',
    CHAT_LIST: '/documents/sessions/{id}',
    DELETE: '/documents/{id}'
  },
  USAGE: {
    MY_USAGE: '/usage/my-usage',
    CLASS_USAGE: '/usage/classes/{id}/members',
    LIMITS: '/usage/classes/{id}/limits'
  }
}

export const FILE_TYPES = {
  ACCEPTED: ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt'],
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  MIME_TYPES: {
    'application/pdf': 'PDF',
    'application/msword': 'Word',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
    'application/vnd.ms-powerpoint': 'PowerPoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
    'text/plain': 'Text'
  }
}

export const USER_ROLES = {
  READER: 'reader',
  CONTRIBUTOR: 'contributor',
  MANAGER: 'manager',
  OWNER: 'owner'
}

export const MODAL_NAMES = {
  CREATE_CLASS: 'CreateClassModal',
  CLASS_SETTINGS: 'ClassSettingsModal',
  DOCUMENT_UPLOAD: 'DocumentUploadModal'
}

export const SLIDEOUT_NAMES = {
  CLASS_INFO: 'ClassInfoPanel',
  USER_SETTINGS: 'UserSettingsPanel',
  QUICK_USAGE: 'QuickUsagePanel'
}

export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
}

