<template>
  <MainLayout>
    <div class="w-full bg-white shadow p-6 relative z-10">
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

    <div class="flex-1 relative z-0 flex sm:mt-16 items-baseline justify-center">
      <div class="bg-white shadow sm:rounded-lg max-w-4xl" v-if="! exited">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Exit server
          </h3>
          <div class="mt-2 sm:flex sm:items-start sm:justify-between">
            <div class="max-w-xl text-sm text-gray-500">
              <p>
                Are you sure you want to exit the server and stop all running nimplants?
              </p>
            </div>
            <div class="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0 sm:flex sm:items-center">
              <button @click.prevent="exitServer" type="button" class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm">
                Exit Server
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="bg-white shadow sm:rounded-lg max-w-4xl" v-else>
        <div class="px-4 py-5 sm:p-6">
          Exiting the server. Check your console for details.
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from "../../components/layouts/MainLayout.vue";

import {
  ServerIcon,
} from '@heroicons/vue/solid'
import api from "../../api/nimplant";

export default {
  components: {
    MainLayout,
    ServerIcon,
  },

  data: () => ({
    exited: false
  }),

  methods: {
    async exitServer() {
      try {
        await api.postServerExit()
        this.exited = true
      } catch (error) {
        console.error(error);
        this.exited = false
      }
    }
  },

  mounted() {
      document.title = 'exit server – nimplant'
  },

}
</script>