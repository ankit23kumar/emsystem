<script setup>
import ToastNotification from './components/ToastNotification.vue'
import { useToast } from './composables/useToast'

const { toast, hideToast } = useToast()
</script>

<template>
  <ToastNotification
    :show="toast.show"
    :type="toast.type"
    :message="toast.message"
    :duration="0"
    @close="hideToast"
  />
  <RouterView />
</template>
