<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from "vue";

const props = defineProps({
  params: {
    type: Object,
    required: true,
  },
});

const menuOpen = ref(false);
const menuStyle = ref({});
const menuButton = ref(null);
const showAlphabetDropdown = ref(false);

const filters = computed(() => props.params.context.filters.value);
const sortOrder = computed(() => filters.value.order);

// function openMenu() {
//   if (menuOpen.value) {
//     closeMenu();
//     return;
//   }

//   const rect = menuButton.value.getBoundingClientRect();

//   menuStyle.value = {
//     position: "fixed",
//     top: `${rect.bottom + 6}px`,
//     left: `${Math.max(8, rect.right - 230)}px`,
//   };

//   menuOpen.value = true;
// }

function updateMenuPosition() {
  if (!menuButton.value) return;

  const rect = menuButton.value.getBoundingClientRect();

  menuStyle.value = {
    position: "fixed",
    top: `${rect.bottom + 6}px`,
    left: `${Math.max(8, rect.right - 230)}px`,
  };
}

function openMenu() {
  if (menuOpen.value) {
    closeMenu();
    return;
  }

  updateMenuPosition();
  menuOpen.value = true;
}

function closeMenu() {
  menuOpen.value = false;
  showAlphabetDropdown.value = false;
}

function toggleAlphabetDropdown() {
  showAlphabetDropdown.value = !showAlphabetDropdown.value;
}

function handleOutsideClick(event) {
  if (
    menuOpen.value &&
    !event.target.closest(".first-name-menu") &&
    !event.target.closest(".header-menu-button")
  ) {
    closeMenu();
  }
}

function sortDefault() {
  props.params.context.onSortFirstName("default");
  closeMenu();
}

function sortAscending() {
  props.params.context.onSortFirstName("asc");
  closeMenu();
}

function sortDescending() {
  props.params.context.onSortFirstName("desc");
  closeMenu();
}

function toggleSort() {
  props.params.context.onToggleFirstNameSort();
}

function filterByLetter(letter) {
  props.params.context.onFilterFirstNameLetter(letter);
  closeMenu();
}

onMounted(() => {
  document.addEventListener("click", handleOutsideClick);

  window.addEventListener("scroll", updateMenuPosition, true);
  window.addEventListener("resize", updateMenuPosition);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleOutsideClick);

  window.removeEventListener("scroll", updateMenuPosition, true);
  window.removeEventListener("resize", updateMenuPosition);
});
</script>

<template>
  <div
    class="first-name-header"
    title="Double-click to change sorting"
    @dblclick.stop="toggleSort"
  >
    <span class="header-title"> 
        First name
        <span v-if="filters.letter" class="selected-letter">
            ({{ filters.letter }})
        </span>
    </span>

    <span
      v-if="filters.sort_by === 'first_name'"
      class="sort-indicator"
      :title="sortOrder === 'asc' ? 'Ascending' : 'Descending'"
    >
      {{ sortOrder === "asc" ? "↑" : "↓" }}
    </span>

    <button
      ref="menuButton"
      type="button"
      class="header-menu-button"
      title="Sort and filter"
      aria-label="Open first name sort and filter menu"
      :aria-expanded="menuOpen"
      @click.stop="openMenu"
      @dblclick.stop
    >
      <svg viewBox="0 0 20 20" aria-hidden="true">
        <path d="m5 7 5 5 5-5" />
      </svg>
    </button>
  </div>

  <Teleport to="body">
    <div v-if="menuOpen" class="first-name-menu" :style="menuStyle" @click.stop>
      <!-- Default sorting -->
      <button type="button" class="menu-option" @click="sortDefault">
        <span>Default order</span>
        <strong>Created</strong>
      </button>

      <!-- Ascending sorting -->
      <button type="button" class="menu-option" @click="sortAscending">
        <span>Sort ascending</span>
        <strong>A–Z</strong>
      </button>

      <!-- Descending sorting -->
      <button type="button" class="menu-option" @click="sortDescending">
        <span>Sort descending</span>
        <strong>Z–A</strong>
      </button>

      <div class="menu-divider"></div>

      <!-- Alphabet filter toggle -->
      <button
        type="button"
        class="alphabet-dropdown-toggle"
        :aria-expanded="showAlphabetDropdown"
        @mousedown.stop
        @click.stop.prevent="toggleAlphabetDropdown"
      >
        <span>Filter using alphabet</span>

        <svg
          class="dropdown-arrow"
          :class="{ rotated: showAlphabetDropdown }"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="m5 7 5 5 5-5" />
        </svg>
      </button>

      <!-- Alphabet dropdown content -->
      <div v-show="showAlphabetDropdown" class="alphabet-dropdown">
        <select
          :value="filters.letter"
          class="alphabet-select"
          aria-label="Select first name initial"
          @change="filterByLetter($event.target.value)"
        >
          <option value="">All letters</option>

          <option
            v-for="letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"
            :key="letter"
            :value="letter"
          >
            {{ letter }}
          </option>
        </select>

        <button
          type="button"
          class="clear-filter"
          @click.stop="filterByLetter('')"
        >
          Clear alphabet filter
        </button>
      </div>
    </div>
  </Teleport>
</template>

<style>
.first-name-header {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 100%;
  height: 100%;
}

.header-title {
  font-weight: 600;
  cursor: pointer;
}

.sort-indicator {
  color: #2563eb;
  font-size: 16px;
  font-weight: 800;
}

.header-menu-button {
  display: grid;
  place-items: center;
  margin-left: 20px;
  flex-shrink: 0;
  width: 25px;
  height: 25px;
  padding: 3px;
  border: none;
  border-radius: 5px;
  background: transparent;
  color: #475569;
  cursor: pointer;
}

.header-menu-button:hover {
  background: #e2e8f0;
}

.header-menu-button svg {
  width: 17px;
  height: 17px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.first-name-menu {
  z-index: 99999;
  width: 230px;
  padding: 9px;
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  background: #fff;
  color: #1e293b;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.16);
}

.menu-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #334155;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.menu-option:hover {
  background: #eff6ff;
  color: #2563eb;
}

.menu-divider {
  height: 1px;
  margin: 7px 0;
  background: #e2e8f0;
}

.alphabet-dropdown-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #334155;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.alphabet-dropdown-toggle:hover {
  background: #eff6ff;
  color: #2563eb;
}
.alphabet-dropdown-toggle.rotated {
  transform: rotate(180deg);
}
.dropdown-arrow {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: transform 0.2s ease;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.alphabet-dropdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  background: #f8fafc;
}

.alphabet-select {
  width: 100%;
  padding: 9px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  font-size: 13px;
  cursor: pointer;
}

.alphabet-select:focus {
  outline: 2px solid #2864ed30;
  border-color: #2864ed;
}

.clear-filter {
  width: 100%;
  padding: 9px;
  border: none;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  cursor: pointer;
}

.clear-filter:hover {
  background: #e2e8f0;
}

.selected-letter {
  margin-left: 3px;
  color: #2563eb;
  font-weight: 700;
}
</style>
