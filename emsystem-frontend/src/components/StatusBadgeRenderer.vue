
<script setup>
defineProps({
  params: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <span
    class="status-pill"
    :class="params.value === 'Valid' ? 'status-valid' : 'status-invalid'"
  >
    <span class="status-dot"></span>
    {{ params.value }}
  </span>
</template>

<style>
.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 76px;
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
}

.status-valid {
  color: #15803d;
  background: #dcfce7;
}

.status-invalid {
  color: #b91c1c;
  background: #fee2e2;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
</style>
