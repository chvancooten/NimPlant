<template>
      <form @submit.prevent="runCommandOnNimPlant">
        <label for="command" class="flex items-center fixed bottom-0 w-full">
          <span class="absolute mx-4">$</span>
          <input v-if="nimplant.active"
                 name="command"
                 type="text"
                 class="w-full bg-gray-900 text-gray-50 border-0 pl-10 pr-6 py-3 border-t-2 border-gray-500 focus:border-primary-500 focus:bg-gray-800 focus:ring-0"
                 v-model="command"
                 autofocus="true"
                 ref="input"
                 @keyup.up="navigateHistory(-1)"
                 @keyup.down="navigateHistory(1)"
          />
          <input v-else
                 name="command"
                 type="text"
                 class="w-full text-gray-400 border-0 pl-10 pr-6 py-3 border-t-2 border-gray-500 bg-gray-800 italic"
                 autofocus="true"
                 disabled="true"
                 value="NimPlant is not active"
          />
        </label>
      </form>
</template>

<script>
export default {
  props: ['nimplant'],

  data: () => ({
    command: '',
    originalCommand: '',
    navigated: false,
    steps: 0,
    input: null
  }),

  mounted() {
    this.focusInput()

    this.steps = this.nimplantHistory?.length + 1
  },

  computed: {
    nimplantHistory() {
      return this.$store.getters.nimplantHistory(this.$route.params.guid)
    },
    commands() {
      return this.nimplantHistory.concat([this.originalCommand])
    }
  },

  methods: {
    runCommandOnNimPlant() {
      this.$store.dispatch('runCommandOnNimPlant', { guid: this.nimplant.guid, command: this.command })
      this.command = ""

      this.$emit('ranCommand')
    },
    focusInput() {
      if (this.nimplant.active) {
        this.$refs.input.focus()
      }
    },
    navigateHistory(steps) {
      if (this.steps >= 2 || (this.steps == 1 && steps != -1)) {
        this.steps = this.steps + steps

        if (this.steps > this.commands.length) {
          this.steps = this.commands.length
        }

        if (! this.navigated) {
          this.originalCommand = this.command
          this.navigated = true
        }

        this.command = this.commands[this.steps - 1]
      }
    },
    resetHistory() {
      this.steps = this.commands.length

      if (this.navigated) {
        this.command = this.originalCommand
      } else {
        this.command = this.commands[this.steps - 1]
      }
    }
  }
}
</script>