<template>
  <header class="w-full">
    <div class="relative z-20 flex-shrink-0 h-16 bg-white border-b border-gray-200 shadow-sm flex">
      <button type="button" class="border-r border-gray-200 px-4 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 md:hidden" @click="$emit('openMobileMenu')">
        <span class="sr-only">Open sidebar</span>
        <MenuAlt2Icon class="h-6 w-6" aria-hidden="true" />
      </button>
      <div class="flex-1 flex justify-between pr-4 sm:pr-6">
        <div class="flex-1 flex">
          <router-link :to="{name: 'server'}" class="relative w-full text-gray-400 hover:text-gray-600 focus-within:text-gray-600 flex items-center focus:ring-2 focus:ring-inset focus:ring-primary-500 pl-4 sm:pl-6">
            <div class="pointer-events-none flex items-center">
              <ServerIcon class="flex-shrink-0 h-5 w-5" aria-hidden="true" />
            </div>
            <div class="flex-1 px-4 text-sm hidden sm:block">
              {{ server.guid }} is listening on {{ server.config.listener.hostname != '' ? server.config.listener.hostname : server.config.listener.ip + ':' + server.config.listener.port }}
            </div>
            <div class="flex-1 px-4 text-sm block sm:hidden">
              {{ server.config.listener.hostname != '' ? server.config.listener.hostname : server.config.listener.ip + ':' + server.config.listener.port }}
            </div>
          </router-link>
        </div>
        <div class="ml-2 flex items-center space-x-4 sm:ml-6 sm:space-x-3">
          <router-link as="button" :to="{ name: 'server.console' }" type="button" class="flex text-primary-600 p-1 rounded-full items-center justify-center hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <TerminalIcon class="h-6 w-6" aria-hidden="true" />
            <span class="sr-only">Show Server Console</span>
          </router-link>
          <router-link as="button" :to="{ name: 'server.exit' }" type="button" class="flex text-primary-600 p-1 rounded-full items-center justify-center hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <StopIcon class="h-6 w-6" aria-hidden="true" />
            <span class="sr-only">Stop Server</span>
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import {
  MenuAlt2Icon,
  TerminalIcon,
  ServerIcon,
  StopIcon,
} from '@heroicons/vue/outline'

import {useStore} from "vuex";
import {computed} from "vue";

export default {
  components: {
    ServerIcon,
    MenuAlt2Icon,
    TerminalIcon,
    StopIcon,
  },

  setup() {
    const store = useStore()

    return {
      server: computed(() => store.getters.server)
    }
  }

}
</script>