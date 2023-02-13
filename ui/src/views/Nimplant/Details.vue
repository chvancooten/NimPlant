<template>
  <NimPlantLayout>
    <div class="pt-24 sm:pt-16">
      <div class="">
        <div class="px-6 py-5 sm:px-6">
          <dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                Username
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ nimplant.username }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                hostname
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{nimplant.hostname }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                external ip
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{nimplant.externalIp }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                internal ip
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ nimplant.internalIp }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                pid
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{nimplant.pid }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                crypt key
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ nimplant.cryptKey }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                os
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{nimplant.osBuild }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                task
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ nimplant.task ?? 'none' }}
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                sleep for
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{nimplant.sleep }} seconds
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                kill after
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ nimplant.killAfter }} hours
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                first check-in
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                <time :datetime="nimplant.firstCheckIn">{{ formatCheckIn(nimplant.firstCheckIn) }}</time>
              </dd>
            </div>
            <div class="sm:col-span-1">
              <dt class="text-sm font-light lowercase text-gray-500">
                last check-in
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                <time :datetime="nimplant.lastCheckIn">{{ formatCheckIn(nimplant.lastCheckIn) }}</time>
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-sm font-light lowercase text-gray-500">
                hosting file
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ nimplant.hostingFile ?? 'none' }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </NimPlantLayout>
</template>

<script>
import NimPlantLayout from "../../components/layouts/NimPlantLayout.vue";
import {useStore} from "vuex";
import {useRoute} from "vue-router";
import {computed} from "vue";
import {formatDistance} from "date-fns";

export default {
  components: {
    NimPlantLayout,
  },

  setup() {
    const store = useStore()
    const route = useRoute()

    return {
      nimplant: computed(() => store.getters.nimplant(route.params.guid)),
      formatCheckIn: (date) => formatDistance(
        date, new Date(), { addSuffix: true }
      )
    }
  },

}
</script>