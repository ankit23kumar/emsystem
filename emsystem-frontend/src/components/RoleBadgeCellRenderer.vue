
<script setup>
import { computed } from "vue";
import RoleBadge from "./RoleBadge.vue";

const props = defineProps({
  params: {
    type: Object,
    required: true,
  },
});

const role = computed(() => props.params.data?.role ?? null);
</script>
<template>
  <RoleBadge
    v-if="role"
    :role-name="role.role_name"
    :role-id="role.role_id"
  />

  <RoleBadge
    v-else
    role-name="No Role"
  />
</template>
                                           