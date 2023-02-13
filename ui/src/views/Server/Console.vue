<template>
  <MainLayout>
    <div class="w-full bg-white shadow p-6 relative z-5">
  <div class="flex items-center justify-between space-x-5">
    <div class="flex items-center space-x-4 w-full">
      <div class="flex-shrink-0">
        <div class="relative">
          <div class="h-8 w-8 rounded-full bg-gray-900 flex items-center justify-center">
            <ServerIcon class="h-6 w-6 text-white" />
          </div>
          <span class="absolute inset-0 shadow-inner rounded-full" aria-hidden="true" />
        </div>
      </div>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-900">Server</h1>
      </div>
    </div>
  </div>
</div>

    <div class="flex-1 relative z-0 bg-gray-900">
      <div class="bg-gray-900 text-gray-50">
        <pre class="p-6 h-screen overflow-x-auto">{{ serverConsole ? serverConsole.result : ''}}</pre>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import {useStore} from "vuex";
import {computed, onMounted} from "vue";
import {formatDistance} from "date-fns";
import MainLayout from "../../components/layouts/MainLayout.vue";
import {
  ServerIcon,
} from '@heroicons/vue/solid'
export default {
  components: {
    MainLayout,
    ServerIcon,
  },

  setup() {
    const store = useStore()

    onMounted(() => {
      document.title = 'server console – nimplant'
    })

    return {
      server: computed(() => store.getters.server),
      serverConsole: computed(() => store.getters.serverConsole),
      formatCheckIn: (date) => formatDistance(
        date, new Date(), { addSuffix: true }
      ),
    }
  },

}
</script>