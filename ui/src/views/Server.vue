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
            <div class="ml-6 bg-gray-100 p-0.5 rounded-lg items-center flex">
              <button type="button"
                      :class="!showAsCode ? 'bg-primary-500 shadow-sm text-primary-100' : 'hover:bg-white hover:shadow-sm text-gray-400'"
                      class="p-1.5 rounded-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                      @click="showAsCode = false"
              >
                <ViewListIcon class="h-5 w-5" aria-hidden="true" />
                <span class="sr-only">Use list view</span>
              </button>
              <button type="button"
                      :class="showAsCode ? 'bg-primary-500 shadow-sm text-primary-100' : 'hover:bg-white hover:shadow-sm text-gray-400'"
                      class="ml-0.5 p-1.5 rounded-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                      @click="showAsCode = true"
              >
                <CodeIcon class="h-5 w-5" aria-hidden="true" />
                <span class="sr-only">Use grid view</span>
              </button>
            </div>
        </div>
      </div>
    </div>

    <div class="flex-1 md:m-6 overflow-y-auto" v-if="showAsCode">
      <div class="bg-gray-900 text-gray-50 md:rounded-lg p-6">
        <pre>{{ prettyJson(server) }}</pre>
      </div>
    </div>

    <div class="flex-1 md:p-6 overflow-y-auto" v-else>
      <h3 class="font-light truncate uppercase p-4 md:p-0">
        Server
      </h3>

      <div class="md:py-6">
        <div class="bg-white shadow overflow-hidden md:rounded-lg p-6">
          <dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                GUID
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.guid }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                ip
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.server.ip }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                port
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.server.port }}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <h3 class="font-light truncate uppercase p-4 md:p-0">
        Listener
      </h3>

      <div class="md:py-6">
        <div class="bg-white shadow overflow-hidden md:rounded-lg p-6">
          <dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                type
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.type }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                hostname
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.hostname != '' ? server.config.listener.hostname : '-'}}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                ip
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.ip }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                port
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.port }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                registerPath
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.registerPath }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                taskPath
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.taskPath }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                resultPath
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.listener.resultPath }}
              </dd>
            </div>
          </dl>

        </div>
      </div>

      <h3 class="font-light truncate uppercase p-4 md:p-0">
        NimPlant
      </h3>

      <div class="md:py-6">
        <div class="bg-white shadow overflow-hidden md:rounded-lg p-6">
          <dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                useragent
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.nimplant.useragent }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                sleep
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.nimplant.sleep }} seconds
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                jitter
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.nimplant.jitter }}%
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                kill after
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ server.config.nimplant.killAfter }} hours
              </dd>
            </div>
          </dl>

        </div>
      </div>

    </div>
  </MainLayout>
</template>

<script>
import {
  Dialog,
  DialogOverlay,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import {
  ChevronRightIcon,
  DotsVerticalIcon,
  DuplicateIcon,
  PencilAltIcon,
  SearchIcon,
  SelectorIcon,
  TrashIcon,
  UserAddIcon,
  ChevronLeftIcon,
  ChipIcon,
  MailIcon,
  CheckCircleIcon,
  ViewListIcon,
  ViewGridIcon,
  CodeIcon,
  ClockIcon,
  ServerIcon,
} from '@heroicons/vue/solid'
import {
  StatusOnlineIcon,
  StatusOfflineIcon,
  FingerPrintIcon,
} from '@heroicons/vue/outline'
import MainLayout from "../components/layouts/MainLayout.vue";
import {useStore} from "vuex";
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import {formatDistance} from "date-fns";

export default {
  components: {
    ServerIcon,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    SelectorIcon,
    MainLayout,
    ChevronLeftIcon,
    ChipIcon,
    CheckCircleIcon,
    ChevronRightIcon,
    ClockIcon,
    ViewListIcon,
    ViewGridIcon,
    CodeIcon,
    StatusOnlineIcon,
    StatusOfflineIcon,
    FingerPrintIcon,
  },

  setup() {
    const store = useStore()

    const showAsCode = ref(false)

    onMounted(() => {
      document.title = 'server – nimplant'
    })

    return {
      showAsCode,
      server: computed(() => store.getters.server),
      formatCheckIn: (date) => formatDistance(
        date, new Date(), { addSuffix: true }
      ),
      prettyJson: (data) => {
        return JSON.stringify(data, null, ' ')
      }
    }
  },

}
</script>