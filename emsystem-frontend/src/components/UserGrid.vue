<script setup>
import { AgGridVue } from "ag-grid-vue3";
import FirstNameHeader from "./FirstNameHeader.vue";
import { ref, watch, nextTick, computed } from "vue";

import {
  ModuleRegistry,
  ClientSideRowModelModule,
  themeQuartz,
} from "ag-grid-community";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const props = defineProps({
  users: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  filters: {
    type: Object,
    required: true,
  },
  onEdit: {
    type: Function,
    required: true,
  },
  onDelete: {
    type: Function,
    required: true,
  },
  onSortFirstName: {
    type: Function,
    required: true,
  },
  onToggleFirstNameSort: {
    type: Function,
    required: true,
  },
  onFilterFirstNameLetter: {
    type: Function,
    required: true,
  },
  canUpdateUsers: {
    type: Boolean,
    default: false,
  },
  canDeleteUsers: {
    type: Boolean,
    default: false,
  },
  canReadUsers: {
    type: Boolean,
    default: false,
  },
  onAssignRole: {
    type: Function,
    default: null,
  },
  canAssignRoles: {
    type: Boolean,
    default: false,
  },
});

const gridTheme = themeQuartz;
const gridApi = ref(null);

const filters = computed(() => props.filters);

const noRowsMessage = computed(() => {
  return props.canReadUsers
    ? "No users found."
    : "You have no permission to access users data.";
});

function isAccountValid(item) {
  if (!item.valid_until) return false;

  const expiry = new Date(item.valid_until);

  if (Number.isNaN(expiry.getTime())) return false;

  // Treat an account as valid through its expiry date.
  expiry.setHours(23, 59, 59, 999);

  return expiry >= new Date();
}

function statusBadgeRenderer(params) {
  const isValid = params.value === "Valid";

  const pill = document.createElement("span");
  pill.className = `status-pill ${isValid ? "status-valid" : "status-invalid"}`;

  const dot = document.createElement("span");
  dot.className = "status-dot";

  pill.appendChild(dot);
  pill.appendChild(document.createTextNode(params.value));

  return pill;
}

function userActionsRenderer(params) {
  const container = document.createElement("div");
  container.className = "row-actions";

  if (props.canUpdateUsers) {
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "edit-button";
    editButton.textContent = "Edit";

    editButton.addEventListener("click", () => {
      props.onEdit(params.data);
    });

    container.appendChild(editButton);
  }

  if (props.canDeleteUsers) {
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.textContent = "Delete";

    deleteButton.addEventListener("click", () => {
      props.onDelete(params.data);
    });

    container.appendChild(deleteButton);
  }

  if (props.canAssignRoles) {
    const assignButton = document.createElement("button");

    assignButton.type = "button";
    assignButton.className = "assign-role-button";
    assignButton.textContent = "Assign Role";

    assignButton.addEventListener("click", () => {
      props.onAssignRole?.(params.data);
    });

    container.appendChild(assignButton);
  }

  return container;
}

const defaultColDef = {
  resizable: true,
  sortable: false,
  filter: false,
};

const columnDefs = [
  {
    field: "first_name",
    headerName: "First name",
    sortable: false,
    headerComponent: FirstNameHeader,
    minWidth: 160,
  },
  {
    field: "last_name",
    headerName: "Last name",
  },
  {
    field: "email",
    headerName: "Email",
    flex: 1,
  },
  {
    headerName:"Role",
    field:"role",
    valueGetter: (params) =>
      params.data?.role?.role_name || "No Role",
    minWidth: 160,
    sortable:false
  },
  {
    headerName: "Password",
    valueGetter: () => "••••••••",
  },
  {
    headerName: "Valid",
    valueGetter: (params) =>
      isAccountValid(params.data) ? "Valid" : "Invalid",
    cellRenderer: statusBadgeRenderer,
    sortable: false,
    width: 120,
  },
  {
    headerName: "Actions",
    cellRenderer: userActionsRenderer,
    sortable: false,
    filter: false,
    minWidth: 260,
  },
];

const gridContext = {
  filters,
  onEdit: props.onEdit,
  onDelete: props.onDelete,
  onSortFirstName: props.onSortFirstName,
  onToggleFirstNameSort: props.onToggleFirstNameSort,
  onFilterFirstNameLetter: props.onFilterFirstNameLetter,
};

function onGridReady(params) {
  gridApi.value = params.api;

  if (props.loading) {
    params.api.showLoadingOverlay();
  } else if (props.users.length === 0) {
    params.api.showNoRowsOverlay();
  }
}

watch(
  [() => props.loading, () => props.users],
  async ([isLoading, currentUsers]) => {
    await nextTick();

    if (!gridApi.value) return;

    if (isLoading) {
      gridApi.value.showLoadingOverlay();
    } else if (currentUsers.length === 0) {
      gridApi.value.showNoRowsOverlay();
    } else {
      gridApi.value.hideOverlay();
    }
  },
);
</script>

<template>
  <div class="ag-grid-wrapper">
    <AgGridVue
      style="width: 100%; height: 500px"
      :theme="gridTheme"
      :rowData="users"
      :columnDefs="columnDefs"
      :defaultColDef="defaultColDef"
      :context="gridContext"
      :suppressCellFocus="true"
      :overlayLoadingTemplate="'<span class=\'ag-overlay-loading-center\'>Loading users...</span>'"
      :overlayNoRowsTemplate="`<span class=\'ag-overlay-no-rows-center\'>${noRowsMessage}</span>`"
      @grid-ready="onGridReady"
    />
  </div>
</template>

<style scoped>
:deep(.row-actions .assign-role-button) {
  border: 1px solid #16a34a;
  background: #f0fdf4;
  color: #15803d;
}

:deep(.row-actions .assign-role-button:hover) {
  background: #dcfce7;
}
</style>
