<template>
  <MainLayout>
    <div class="w-full bg-white shadow p-6 relative z-5">
      <div class="flex items-center justify-between space-x-5">
        <div class="flex items-center space-x-4 w-full">
          <div class="flex-shrink-0">
            <div class="relative">
              <div class="h-8 w-8 rounded-full bg-gray-900 flex items-center justify-center">
                <ChipIcon class="h-6 w-6 text-white" />
              </div>
              <span class="absolute inset-0 shadow-inner rounded-full" aria-hidden="true" />
            </div>
          </div>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">NimPlants</h1>
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
        <pre>{{ prettyJson(nimplants) }}</pre>
      </div>
    </div>

    <div class="flex-1 md:p-6 overflow-y-auto" v-else>
      <!-- table header -->
      <div class="overflow-hidden hidden md:block">
        <div class="divide-y divide-gray-200">
          <div class="block">
            <div class="flex items-center px-4 pb-4 sm:px-6">
              <div class="min-w-0 flex-1 flex items-center">
                <div class="flex-shrink-0">
                  <StatusOfflineIcon class="h-8 w-8 text-white opacity-0" aria-hidden="true" />
                </div>
                <div class="min-w-0 flex-1 px-4 md:grid md:grid-cols-2 md:gap-3 lg:grid-cols-3 lg:gap-4 uppercase">
                  <div class="-ml-12">
                    <p class="font-light truncate">NimPlant</p>
                  </div>
                  <div class="hidden md:block">
                    <div>
                      <p class="font-light truncate">System</p>
                    </div>
                  </div>
                  <div class="hidden lg:block">
                    <div>
                      <p class="font-light truncate">Network</p>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                  <ChevronRightIcon class="h-5 w-5 text-white opacity-0" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white shadow overflow-hidden md:rounded-lg">
        <ul class="divide-y divide-gray-200">
          <li v-for="nimplant in nimplants" :key="nimplant.guid" class="">
            <router-link :to="{ name: 'nimplant', params: { guid: nimplant.guid } }" class="block hover:bg-gray-50">
              <div class="flex items-center px-4 py-4 sm:px-6">
                <div class="min-w-0 flex-1 flex items-center">
                  <div class="flex-shrink-0">
                    <StatusOnlineIcon class="h-8 w-8 text-green-400" v-if="nimplant.active" />
                    <StatusOfflineIcon class="h-8 w-8 text-gray-400" v-else />
                  </div>
                  <div class="min-w-0 flex-1 px-4 md:grid md:grid-cols-2 md:gap-3 lg:grid-cols-3 lg:gap-4">
                    <div>
                      <p class="text-sm font-medium text-primary-600 truncate">{{ nimplant.id }}  – {{ nimplant.guid }}</p>
                      <p class="mt-2 flex items-center text-sm text-gray-700 md:hidden">
                        <span class="truncate">{{ nimplant.username }}@{{ nimplant.hostname }}</span>
                      </p>
                      <p class="mt-2 flex items-center text-sm text-gray-500">
                        <span class="truncate">Last checked in {{ formatCheckIn(nimplant.lastCheckIn) }}</span>
                      </p>
                    </div>
                    <div class="hidden md:block">
                      <div>
                        <p class="text-sm text-gray-900">
                          {{ nimplant.username }}@{{ nimplant.hostname }}
                        </p>
                        <p class="mt-2 flex items-center text-sm text-gray-500">
                          <FingerPrintIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
                          {{ nimplant.pid }}
                        </p>
                      </div>
                    </div>
                    <div class="hidden lg:block">
                      <div>
                        <p class="text-sm text-gray-900">
                          {{ nimplant.externalIp }}
                        </p>
                        <p class="mt-2 flex items-center text-sm text-gray-500">
                          {{ nimplant.internalIp }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <ChevronRightIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
              </div>
            </router-link>
          </li>
        </ul>
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

const application = [
  {
    applicant: {
      name: 'Ricardo Cooper',
      email: 'ricardo.cooper@example.com',
      imageUrl:
        'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    },
    date: '2020-01-07',
    dateFull: 'January 7, 2020',
    stage: 'Completed phone screening',
    href: '#',
  },
]

export default {
  components: {
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
    FingerPrintIcon
  },

  setup() {
    const store = useStore()

    const showAsCode = ref(false)

    onMounted(() => {
      document.title = 'nimplants – nimplant'
    })

    return {
      showAsCode,
      application,
      nimplants: computed(() => store.getters.nimplants),
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