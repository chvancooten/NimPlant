<template>
  <NimPlantLayout bg="bg-gray-900">
    <div class="bg-gray-900 text-gray-50">
      <pre class="px-6 pt-28 sm:pt-20 pb-20 overflow-x-auto">{{ nimplantConsole ? nimplantConsole.result : ''}}<code ref="consoleContainer"></code></pre>

      <ConsoleInput :nimplant="nimplant" @ranCommand="updateConsolePosition" />
    </div>
  </NimPlantLayout>
</template>

<script>
import NimPlantLayout from "../../components/layouts/NimPlantLayout.vue";
import {useStore} from "vuex";
import {useRoute} from "vue-router";
import {computed, onBeforeUnmount, onMounted, onUpdated, ref} from "vue";
import {formatDistance} from "date-fns";
import ConsoleInput from "../../components/ConsoleInput.vue";

export default {
  components: {
    ConsoleInput,
    NimPlantLayout,
  },

  data: () => ({
    pollingConsole: null
  }),

  computed: {
    nimplant() {
      return this.$store.getters.nimplant(this.$route.params.guid)
    },
    nimplantConsole() {
      return this.$store.getters.nimplantConsole(this.$route.params.guid)
    }
  },

  methods: {
    updateConsolePosition() {
      this.$refs.consoleContainer.scrollIntoView({ behavior: "smooth" })
    },
    pollConsoleForUpdates() {
      let sleepFor = this.nimplant.sleep * 1000
      this.pollingConsole = setInterval(() => {
        this.$store.dispatch('fetchNimPlantConsole', this.nimplant.guid)
        // this.updateConsolePosition()
      }, sleepFor ?? 5000)
    },
    formatCheckIn(date) {
      return formatDistance(
        date, new Date(), { addSuffix: true }
      )
    }
  },

  mounted() {
    this.updateConsolePosition()
  },

  beforeUnmount() {
    if (this.pollingConsole) {
      clearInterval(this.pollingConsole)
    }
  },

  beforeRouteEnter(to, from, next) {
    next(vm => {
      if (vm.nimplant.active) {
        vm.pollConsoleForUpdates()
      }
    })
  },

  beforeRouteLeave(to, from, next) {
    if (this.pollingConsole) {
      clearInterval(this.pollingConsole)
    }

    next()
  }
}
</script>