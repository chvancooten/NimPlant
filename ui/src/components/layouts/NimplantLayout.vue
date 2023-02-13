<template>
  <MainLayout>
    <div class="w-full bg-white shadow p-6 relative z-10">
      <div class="md:flex md:items-center md:justify-between md:space-x-5">
        <div class="flex items-center space-x-5">
          <div class="flex-shrink-0">
            <div class="relative">
              <StatusOnlineIcon class="h-8 w-8 text-green-400" v-if="nimplant.active" />
              <StatusOfflineIcon class="h-8 w-8 text-gray-400" v-else />
            </div>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ nimplant.id }}  – {{ nimplant.guid }}</h1>
            <p class="text-sm font-medium text-gray-500">Last checked in <time :datetime="nimplant.lastCheckIn">{{ formatCheckIn(nimplant.lastCheckIn) }}</time></p>
          </div>
        </div>
        <div>
        </div>
      </div>
    </div>

    <div class="flex-1 relative z-0 overflow-y-auto" :class="bg">
      <div class="fixed w-full">
        <div class="sm:hidden bg-white p-6 shadow">
          <label for="tabs" class="sr-only">Select a tab</label>
          <select id="tabs" name="tabs" class="block w-full focus:ring-primary-500 focus:border-primary-500 border-gray-300 rounded-md uppercase font-light" v-model="selectedTab">
            <option v-for="tab in tabs" :key="tab.name" :value="tab.to">{{ tab.name }}</option>
          </select>
        </div>
        <div class="hidden sm:block ">
          <nav class="relative z-0 shadow flex divide-x divide-gray-200" aria-label="Tabs">
            <router-link v-for="(tab, tabIdx) in tabs" :key="tab.name" :to="tab.to" :class="[tab.current ? 'text-gray-900' : 'text-gray-500 hover:text-gray-700', 'group relative min-w-0 flex-1 overflow-hidden bg-white py-4 px-4 text-sm uppercase font-light text-center hover:bg-gray-50 focus:z-10']" :aria-current="tab.current ? 'page' : undefined">
              <span>{{ tab.name }}</span>
              <span aria-hidden="true" :class="[tab.current ? 'bg-primary-500' : 'bg-transparent', 'absolute inset-x-0 bottom-0 h-0.5']" />
            </router-link>
          </nav>
        </div>
      </div>

      <slot></slot>
    </div>
  </MainLayout>
</template>

<script>
import {
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from '@headlessui/vue'
import {
  SelectorIcon,
  ChevronLeftIcon,
} from '@heroicons/vue/solid'
import {
  StatusOnlineIcon,
  StatusOfflineIcon,
  FingerPrintIcon,
} from '@heroicons/vue/outline'
import MainLayout from "./MainLayout.vue";
import {useStore} from "vuex";
import {useRoute, useRouter} from "vue-router";
import {computed, ref, watch, toRef} from "vue";
import {formatDistance} from "date-fns";

export default {
  props: {
    bg: {
      type: String,
      default: 'bg-white'
    }
  },

  components: {
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    SelectorIcon,
    MainLayout,
    ChevronLeftIcon,
    StatusOnlineIcon,
    StatusOfflineIcon,
    FingerPrintIcon,
  },

  setup(props) {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()

    const tabs = computed(() => [
      { name: 'Console', to: { name: 'nimplant.console', params: { guid: route.params.guid }}, current: route.name == "nimplant.console" },
      { name: 'Details', to: { name: 'nimplant.details', params: { guid: route.params.guid }}, current: route.name == "nimplant.details" },
    ])

    const selectedTab = ref(tabs.value.filter(t => t.current)[0].to)
    watch(selectedTab, (newValue, oldValue) => {
      router.push(newValue)
    })

    const bg = toRef(props, 'bg')

    return {
      bg,
      tabs,
      selectedTab,
      nimplants: computed(() => store.getters.nimplants),
      nimplant: computed(() => store.getters.nimplant(route.params.guid)),
      formatCheckIn: (date) => formatDistance(
        date, new Date(), { addSuffix: true }
      ),
    }
  },

}
</script>