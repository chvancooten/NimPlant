<template>
  <div class="h-screen bg-gray-50 flex overflow-hidden">
    <!-- Menu -->
    <AppMenu :open="mobileMenuOpen" @close="mobileMenuOpen = false" />

    <!-- Content area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppHeader @open-mobile-menu="mobileMenuOpen = true" />

      <!-- Main content -->
      <div class="flex-1 flex items-stretch overflow-hidden">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import AppMenu from "./components/AppMenu.vue";
import AppHeader from "./components/AppHeader.vue";

export default {
  components: {
    AppHeader,
    AppMenu,
  },

  setup() {
    const mobileMenuOpen = ref(false)

    return {
      mobileMenuOpen,
    }
  },
}
</script>