
<script setup>
defineProps({
  params: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <div class="row-actions">
    <button
      type="button"
      class="edit-button"
      @click="params.context.onEdit(params.data)"
    >
      Edit
    </button>

    <button
      type="button"
      class="delete-button"
      @click="params.context.onDelete(params.data)"
    >
      Delete
    </button>
  </div>
</template>

<!-- Deliberately not scoped: test these styles as global CSS. -->
<style>
.row-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 100%;
}

.row-actions button {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.row-actions .edit-button {
  border: 1px solid #2864ed;
  background: #eff6ff;
  color: #2864ed;
}

.row-actions .edit-button:hover {
  background: #dbeafe;
}

.row-actions .delete-button {
  border: 1px solid #ef4444;
  background: #fef2f2;
  color: #dc2626;
}

.row-actions .delete-button:hover {
  background: #fee2e2;
}
</style>
