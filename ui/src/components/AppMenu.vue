<template>
  <!-- Narrow sidebar -->
  <div class="hidden w-28 bg-primary-700 overflow-y-auto md:block">
    <div class="w-full py-6 flex flex-col items-center">
      <div class="flex-shrink-0 flex items-center">
        <Logo class="h-8 w-auto" alt="NimPlant" />
      </div>
      <div class="flex-1 mt-6 w-full px-2 space-y-1">
        <router-link v-for="item in navigation" :key="item.name" :to="item.to" :class="[item.hidden ? 'hidden' : '', item.current ? 'bg-primary-800 text-white' : 'text-primary-100 hover:bg-primary-800 hover:text-white', 'group w-full p-3 rounded-md flex flex-col items-center text-xs font-medium']" :aria-current="item.current ? 'page' : undefined">
          <component :is="item.icon" :class="[item.current ? 'text-white' : 'text-primary-300 group-hover:text-white', 'h-6 w-6']" aria-hidden="true" />
          <span class="mt-2">{{ item.name }}</span>
        </router-link>
      </div>
    </div>
  </div>

  <!-- Mobile menu -->
  <MobileMenu :navigation="navigation" :open="open" @close="$emit('close')" />
</template>

<script>
import Logo from "./Logo.vue";
import MobileMenu from "./MobileMenu.vue";
import {ChipIcon, ServerIcon} from "@heroicons/vue/outline";

export default {
  components: {MobileMenu, Logo},
  props: {
    open: {
      type: Boolean,
      default: false,
    }
  },

  computed: {
    navigation() {
      return [
        {
          name: 'Server',
          to: { name: 'server' },
          icon: ServerIcon,
          hidden: true,
          current: this.$route.name === 'server'
        },
        {
          name: 'NimPlants',
          to: { name: 'nimplants' },
          icon: ChipIcon,
          hidden: false,
          current: this.$route.name === 'nimplants'
        },
      ]
    }
  }
}
</script>