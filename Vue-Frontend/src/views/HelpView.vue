<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <router-link to="/" class="text-2xl font-bold text-primary-600">
            StudHelper
          </router-link>
          <router-link 
            to="/dashboard" 
            class="btn-primary"
          >
            Back to Dashboard
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="bg-white rounded-lg shadow-sm p-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Help & Documentation</h1>

        <!-- Getting Started -->
        <section class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">Getting Started</h2>
          <div class="space-y-4 text-gray-700">
            <p>Welcome to StudHelper! This guide will help you get started with your AI study assistant.</p>
            
            <div class="bg-gray-50 p-6 rounded-lg">
              <h3 class="font-semibold text-gray-900 mb-3">Quick Start Steps:</h3>
              <ol class="list-decimal list-inside space-y-2">
                <li>Create your first study class</li>
                <li>Upload your study materials (PDFs, documents, videos)</li>
                <li>Start chatting with your AI tutor about the content</li>
                <li>Organize your learning into focused sessions</li>
              </ol>
            </div>
          </div>
        </section>

        <!-- Features -->
        <section class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">Features</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div class="bg-gray-50 p-6 rounded-lg">
              <h3 class="font-semibold text-gray-900 mb-3">Class Management</h3>
              <p class="text-gray-700">
                Create and organize study classes for different subjects or topics. Each class can contain multiple documents and chat sessions.
              </p>
            </div>

            <div class="bg-gray-50 p-6 rounded-lg">
              <h3 class="font-semibold text-gray-900 mb-3">Document Upload</h3>
              <p class="text-gray-700">
                Upload PDFs, Word documents, PowerPoint presentations, and YouTube videos. The AI will analyze and understand your content.
              </p>
            </div>

            <div class="bg-gray-50 p-6 rounded-lg">
              <h3 class="font-semibold text-gray-900 mb-3">AI Chat</h3>
              <p class="text-gray-700">
                Chat with an AI tutor that has knowledge of your specific study materials. Ask questions, request explanations, and get help.
              </p>
            </div>

            <div class="bg-gray-50 p-6 rounded-lg">
              <h3 class="font-semibold text-gray-900 mb-3">Usage Tracking</h3>
              <p class="text-gray-700">
                Monitor your AI usage and stay within your limits. Track tokens used per class and optimize your study sessions.
              </p>
            </div>
          </div>
        </section>

        <!-- FAQ -->
        <section class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">Frequently Asked Questions</h2>
          <div class="space-y-6">
            
            <div class="border-l-4 border-primary-500 pl-4">
              <h3 class="font-semibold text-gray-900 mb-2">What file types can I upload?</h3>
              <p class="text-gray-700">
                You can upload PDF files, Word documents (.docx), PowerPoint presentations (.pptx), text files, and YouTube video links.
              </p>
            </div>

            <div class="border-l-4 border-primary-500 pl-4">
              <h3 class="font-semibold text-gray-900 mb-2">How does the AI understand my documents?</h3>
              <p class="text-gray-700">
                The AI processes your documents by extracting text, creating embeddings, and building a knowledge base specific to your content.
              </p>
            </div>

            <div class="border-l-4 border-primary-500 pl-4">
              <h3 class="font-semibold text-gray-900 mb-2">Can I share classes with others?</h3>
              <p class="text-gray-700">
                Yes! You can invite others to join your classes with different permission levels, from read-only access to full management rights.
              </p>
            </div>
          </div>
        </section>

        <!-- Contact -->
        <section>
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">Need More Help?</h2>
          <div class="bg-primary-50 p-6 rounded-lg">
            <p class="text-gray-700 mb-4">
              Can't find what you're looking for? We're here to help!
            </p>
            <div class="flex flex-col sm:flex-row gap-4">
              <a href="mailto:support@studhelper.com" class="btn-primary inline-block text-center">
                Email Support
              </a>
              <a href="#" class="btn-secondary inline-block text-center">
                Community Forum
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
// No specific logic needed for static help page
</script>

