
<script setup>
import { watch, onUnmounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  type: {
    type: String,
    default: 'success',
    validator: value =>
      ['success', 'error', 'warning', 'info'].includes(value),
  },
  message: {
    type: String,
    default: '',
  },
  duration: {
    type: Number,
    default: 4000,
  },
})

const emit = defineEmits(['close'])

let timeoutId = null

function clearToastTimer() {
  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutId = null
  }
}

watch(
  () => [props.show, props.message, props.duration],
  ([isVisible]) => {
    clearToastTimer()

    if (isVisible && props.duration > 0) {
      timeoutId = setTimeout(() => {
        emit('close')
      }, props.duration)
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  clearToastTimer()
})
</script>

<template>
  <Transition name="toast">
    <div
      v-if="show && message"
      class="toast-notification"
      :class="`toast-${type}`"
      :role="type === 'error' ? 'alert' : 'status'"
      aria-live="polite"
    >
      <span class="toast-icon" aria-hidden="true">
        {{
          type === 'success' ? '✓' :
          type === 'error' ? '✕' :
          type === 'warning' ? '⚠' : 'ℹ'
        }}
      </span>

      <p class="toast-message">{{ message }}</p>

      <button
        type="button"
        class="toast-close"
        aria-label="Close notification"
        @click="emit('close')"
      >
        ×
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.toast-notification {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 2000;
  display: flex;
  align-items: center;
  gap: 12px;
  width: min(400px, calc(100vw - 32px));
  padding: 15px 16px;
  border: 1px solid;
  border-radius: 10px;
  background: #ffffff;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
}

.toast-icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  font-weight: 700;
}

.toast-message {
  flex: 1;
  margin: 0;
  color: #263238;
  font-size: 14px;
  line-height: 1.5;
}

.toast-close {
  flex-shrink: 0;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 22px;
  cursor: pointer;
}

.toast-success {
  border-color: #a7f3d0;
  background: #ecfdf5;
}

.toast-success .toast-icon {
  background: #d1fae5;
  color: #047857;
}

.toast-error {
  border-color: #fecaca;
  background: #fef2f2;
}

.toast-error .toast-icon {
  background: #fee2e2;
  color: #b91c1c;
}

.toast-warning {
  border-color: #fde68a;
  background: #fffbeb;
}

.toast-warning .toast-icon {
  background: #fef3c7;
  color: #b45309;
}

.toast-info {
  border-color: #bae6fd;
  background: #f0f9ff;
}

.toast-info .toast-icon {
  background: #e0f2fe;
  color: #0369a1;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@media (max-width: 600px) {
  .toast-notification {
    top: 12px;
    right: 16px;
  }
}
</style>
