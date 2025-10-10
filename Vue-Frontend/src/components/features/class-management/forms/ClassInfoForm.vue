<template>
  <div class="class-info-form space-y-4">
    <div>
      <label for="className" class="block text-sm font-medium text-gray-700 mb-1">
        Class Name <span class="text-red-500">*</span>
      </label>
      <input
        id="className"
        type="text"
        :value="name"
        @input="$emit('update:name', $event.target.value)"
        placeholder="e.g., Physics 101"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        :class="{ 'border-red-500': errors.name }"
      />
      <p v-if="errors.name" class="mt-1 text-sm text-red-600">
        {{ errors.name }}
      </p>
    </div>

    <div>
      <label for="classDescription" class="block text-sm font-medium text-gray-700 mb-1">
        Description
      </label>
      <textarea
        id="classDescription"
        :value="description"
        @input="$emit('update:description', $event.target.value)"
        placeholder="What is this class about?"
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['update:name', 'update:description'])
</script>


