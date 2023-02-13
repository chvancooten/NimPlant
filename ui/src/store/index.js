import { createStore } from "vuex";
import api from "../api/nimplant";

export const UPDATE_SERVER = 'UPDATE_SERVER'
export const UPDATE_SERVER_CONSOLE = 'UPDATE_SERVER_CONSOLE'
export const UPDATE_NIMPLANTS = 'UPDATE_NIMPLANTS'
export const ADD_NIMPLANT = 'ADD_NIMPLANT'
export const UPSERT_NIMPLANT_CONSOLE = 'UPSERT_NIMPLANT_CONSOLE'
export const UPSERT_NIMPLANT_HISTORY = 'UPSERT_NIMPLANT_HISTORY'
export const ADD_COMMAND_HISTORY_ENTRY = 'ADD_COMMAND_HISTORY_ENTRY'

export default createStore({
    state: {
        server: null,
        serverConsole: null,
        nimplants: null,
        nimplantDetails: {},
        nimplantConsoles: {},
        nimplantHistories: {},
        commandHistory: JSON.parse(localStorage.getItem("commandHistory") ?? '{}'),
    },
    getters: {
        server: ({ server }) => server,
        serverConsole: ({ serverConsole }) => serverConsole,
        nimplants: ({ nimplants }) => nimplants,
        nimplant: ({nimplantDetails}) => (guid) => nimplantDetails.hasOwnProperty(guid) ? nimplantDetails[guid] : null,
        nimplantConsole: ({nimplantConsoles}) => (guid) => nimplantConsoles.hasOwnProperty(guid) ? nimplantConsoles[guid] : null,
        nimplantHistory: ({nimplantHistories}) => (guid) => nimplantHistories.hasOwnProperty(guid) ? nimplantHistories[guid] : null,
        commandHistory: ({commandHistory}) => (guid) => commandHistory.hasOwnProperty(guid) ? commandHistory[guid] : null,
    },
    mutations: {
        [UPDATE_SERVER](state, server) {
            state.server = server
        },

        [UPDATE_SERVER_CONSOLE](state, serverConsole) {
            state.serverConsole = serverConsole
        },

        [UPDATE_NIMPLANTS](state, nimplants) {
            state.nimplants = nimplants
        },

        [ADD_NIMPLANT](state, nimplant) {
            state.nimplantDetails[nimplant.guid] = nimplant
        },

        [UPSERT_NIMPLANT_CONSOLE](state, { guid, nimplantConsole }) {
            state.nimplantConsoles[guid] = nimplantConsole
        },

        [UPSERT_NIMPLANT_HISTORY](state, { guid, history }) {
            localStorage.setItem(`commands:${guid}`, JSON.stringify(history))

            state.nimplantHistories[guid] = history
        },

        [ADD_COMMAND_HISTORY_ENTRY](state, { guid, command }) {
            if (!state.nimplantHistories.hasOwnProperty(guid)) {
                state.nimplantHistories[guid] = []
            }

            state.nimplantHistories[guid].push(command)

            localStorage.setItem(`commands:${guid}`, JSON.stringify(state.nimplantHistories[guid]))
        },
    },
    actions: {
        async fetchServer({ commit }) {
            try {
                const server = await api.getServer()
                commit(UPDATE_SERVER, server)

            } catch (error) {
                console.error(error);
            }
        },

        async fetchServerConsole({ commit }) {
            try {
                const serverConsole = await api.getServerConsole()
                commit(UPDATE_SERVER_CONSOLE, serverConsole)

            } catch (error) {
                console.error(error);
            }
        },

        async fetchNimPlants({ commit }) {
            try {
                const nimplants = await api.getNimPlants()
                commit(UPDATE_NIMPLANTS, nimplants)

            } catch (error) {
                console.error(error);
            }
        },

        async fetchNimPlant({ commit }, guid) {
            try {
                const nimplant = await api.getNimPlant(guid)
                commit(ADD_NIMPLANT, nimplant)
            } catch (error) {
                console.error(error);
            }
        },

        async fetchNimPlantConsole({ commit }, guid) {
            try {
                const { nimplant, console: nimplantConsole } = await api.getNimPlantConsole(guid)

                if (nimplant) {
                    commit(ADD_NIMPLANT, nimplant)
                }

                commit(UPSERT_NIMPLANT_CONSOLE, { guid, nimplantConsole })
            } catch (error) {
                console.error(error);
            }
        },

        async runCommandOnNimPlant({ commit, dispatch }, { guid, command }) {
            try {
                const commandResult = await api.postNimPlantCommand(guid, command)

                console.log(commandResult)

                commit(ADD_COMMAND_HISTORY_ENTRY, { guid, command })

                await dispatch('fetchNimPlantConsole', guid)
            } catch (error) {
                console.error(error);
            }
        },
    },

    modules: {}
});
