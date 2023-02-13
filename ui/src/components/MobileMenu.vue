<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" static class="fixed inset-0 z-40 flex md:hidden" @close="$emit('close')" :open="open">
      <TransitionChild as="template" enter="transition-opacity ease-linear duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="transition-opacity ease-linear duration-300" leave-from="opacity-100" leave-to="opacity-0">
        <DialogOverlay class="fixed inset-0 bg-gray-600 bg-opacity-75" />
      </TransitionChild>
      <TransitionChild as="template" enter="transition ease-in-out duration-300 transform" enter-from="-translate-x-full" enter-to="translate-x-0" leave="transition ease-in-out duration-300 transform" leave-from="translate-x-0" leave-to="-translate-x-full">
        <div class="relative max-w-xs w-full bg-primary-700 pt-5 pb-4 flex-1 flex flex-col">
          <TransitionChild as="template" enter="ease-in-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-300" leave-from="opacity-100" leave-to="opacity-0">
            <div class="absolute top-1 right-0 -mr-14 p-1">
              <button type="button" class="h-12 w-12 rounded-full flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-white" @click="$emit('close')">
                <XIcon class="h-6 w-6 text-white" aria-hidden="true" />
                <span class="sr-only">Close sidebar</span>
              </button>
            </div>
          </TransitionChild>
          <div class="flex-shrink-0 px-4 flex items-center">
            <Logomark class="h-8 w-auto" alt="NimPlant"/>
          </div>
          <div class="mt-5 flex-1 h-0 px-2 overflow-y-auto">
            <nav class="h-full flex flex-col">
              <div class="space-y-1">
                <router-link @click="$emit('close')" v-for="item in navigation" :key="item.name" :to="item.to" :class="[item.hidden ? 'hidden' : '', item.current ? 'bg-primary-800 text-white' : 'text-primary-100 hover:bg-primary-800 hover:text-white', 'group py-2 px-3 rounded-md flex items-center text-sm font-medium']" :aria-current="item.current ? 'page' : undefined">
                  <component :is="item.icon" :class="[item.current ? 'text-white' : 'text-primary-300 group-hover:text-white', 'mr-3 h-6 w-6']" aria-hidden="true" />
                  <span>{{ item.name }}</span>
                </router-link>
              </div>
            </nav>
          </div>
        </div>
      </TransitionChild>
      <div class="flex-shrink-0 w-14" aria-hidden="true">
        <!-- Dummy element to force sidebar to shrink to fit close icon -->
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script>
import {
  Dialog,
  DialogOverlay,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'

import Logomark from "./Logomark.vue";
import { XIcon } from "@heroicons/vue/outline";

export default {
  components: {
    Logomark,
    Dialog,
    DialogOverlay,
    TransitionChild,
    TransitionRoot,
    XIcon
  },
  props: {
    open: {
      type: Boolean,
      default: false,
    },
    navigation: {
      type: Object,
    }
  }
}
</script>