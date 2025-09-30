# StudHelper Frontend

A Vue.js frontend for StudHelper - your personal AI study assistant that allows you to upload documents and chat with an AI tutor about your specific study materials.

## Features

- **Class Management**: Create and organize study classes
- **Document Upload**: Upload PDFs, Word docs, PowerPoint, and YouTube videos
- **AI Chat**: Chat with an AI tutor that understands your materials
- **User Management**: Authentication and profile management
- **Usage Tracking**: Monitor AI usage and limits

## Tech Stack

- **Vue 3** with Composition API
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Pinia** for state management
- **Vue Router** for navigation
- **Axios** for HTTP requests

## Setup Instructions

1. **Clone and Install**
   ```bash
   npm install
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

3. **Development Server**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── views/              # Main pages
├── components/
│   ├── features/       # Feature-specific components
│   ├── ui/            # Reusable UI components
│   └── shared/        # Shared components
├── stores/            # Pinia state management
├── services/          # API service layer
├── composables/       # Vue composition functions
├── utils/             # Helper utilities
└── assets/           # Static assets
```

## Backend Integration

This frontend is designed to work with the StudHelper FastAPI backend. Make sure to:

1. Set the correct API URL in `.env`
2. Ensure CORS is configured in your backend
3. The backend should be running on the specified port

## Development

- Uses Vue 3 Composition API
- Tailwind CSS for styling
- Component-based architecture
- Modular service layer for API calls
- Centralized state management with Pinia

