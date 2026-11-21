
<script setup>
const props = defineProps({
  roleName: {
    type: String,
    default: "Unassigned",
  },
  roleId: {
    type: [Number, String],
    default: null,
  },
})

// Assign a consistent color to each role.
// New roles automatically receive a color.
const colors = [
  "blue",
  "purple",
  "green",
  "orange",
  "pink",
  "cyan",
  "indigo",
  "teal",
]

function getColor() {
  if (!props.roleId) return "gray"

  const index = Math.abs(Number(props.roleId)) % colors.length
  return colors[index]
}
</script>

<template>
  <span class="role-badge" :class="`badge-${getColor()}`">
    {{ roleName }}
  </span>
</template>

<style scoped>
/* .role-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 11px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
} */
.role-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  min-height: 25px;
  padding: 4px 10px;
  border-radius: 999px;

  font-size: 11px;
  font-weight: 650;
  line-height: 1.2;
  white-space: nowrap;

  box-sizing: border-box;
}

.badge-blue {
  color: #1d4ed8;
  background: #dbeafe;
}

.badge-purple {
  color: #7e22ce;
  background: #f3e8ff;
}

.badge-green {
  color: #15803d;
  background: #dcfce7;
}

.badge-orange {
  color: #c2410c;
  background: #ffedd5;
}

.badge-pink {
  color: #be185d;
  background: #fce7f3;
}

.badge-cyan {
  color: #0e7490;
  background: #cffafe;
}

.badge-indigo {
  color: #4338ca;
  background: #e0e7ff;
}

.badge-teal {
  color: #0f766e;
  background: #ccfbf1;
}

.badge-gray {
  color: #475569;
  background: #f1f5f9;
}
</style>
