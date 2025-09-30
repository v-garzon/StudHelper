export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

export const validatePassword = (password) => {
  const errors = []
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long')
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  }
  
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export const validateUsername = (username) => {
  if (username.length < 3) {
    return { isValid: false, error: 'Username must be at least 3 characters long' }
  }
  
  if (username.length > 20) {
    return { isValid: false, error: 'Username must be less than 20 characters long' }
  }
  
  if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
    return { isValid: false, error: 'Username can only contain letters, numbers, hyphens, and underscores' }
  }
  
  return { isValid: true }
}

export const validateClassName = (name) => {
  if (!name || name.trim().length === 0) {
    return { isValid: false, error: 'Class name is required' }
  }
  
  if (name.length < 3) {
    return { isValid: false, error: 'Class name must be at least 3 characters long' }
  }
  
  if (name.length > 100) {
    return { isValid: false, error: 'Class name must be less than 100 characters long' }
  }
  
  return { isValid: true }
}

export const validateFileUpload = (file) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
  ]
  
  if (file.size > maxSize) {
    return { isValid: false, error: 'File size must be less than 10MB' }
  }
  
  if (!allowedTypes.includes(file.type)) {
    return { isValid: false, error: 'File type not supported. Please upload PDF, Word, PowerPoint, or text files.' }
  }
  
  return { isValid: true }
}

export const validateYouTubeUrl = (url) => {
  const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})$/
  
  if (!youtubeRegex.test(url)) {
    return { isValid: false, error: 'Please enter a valid YouTube URL' }
  }
  
  return { isValid: true }
}

