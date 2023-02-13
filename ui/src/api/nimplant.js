import axios from "axios";
import parse from "date-fns/parse"

const http = axios.create({
    baseURL: import.meta.env.VITE_APP_BASE_URL
});

const endpoints = {
    server: '/server',
    serverExit: '/server/exit',
    serverConsole:  (lines = 100) => `/server/console/${lines}`,
    nimplants: '/nimplants',
    nimplant: (guid) => `/nimplants/${guid}`,
    nimplantExit: (guid) => `/nimplants/${guid}/exit`,
    nimplantCommand: (guid) => `/nimplants/${guid}/command`,
    nimplantConsole: (guid, lines = 100) => `/nimplants/${guid}/console/${lines}`,
    nimplantHistory: (guid, lines = 100) => `/nimplants/${guid}/history/${lines}`,
}

const Server = {
    guid: null,
    config: {
        server: {
            ip: null,
            port: 0
        },
        listener: {
            type: null,
            hostname: null,
            ip: null,
            port: 0,
            registerPath: null,
            taskPath: null,
            resultPath: null,
        },
        nimplant: {
            useragent: null,
            sleep: 0,
            jitter: 0,
            killAfter: 0
        }
    }
}

const ServerConsole = {
    id: '',
    lines: 0,
    result: ''
}

const NimPlant = {
    id: 0,
    guid: null,
    active: false,
    externalIp: null,
    internalIp: null,
    username: null,
    hostname: null,
    pid: 0,
    lastCheckIn: null,
    // Details
    osBuild: null,
    sleep: 0,
    killAfter: 0,
    firstCheckIn: null,
    task: null,
    hostingFile: null,
    cryptKey: null
}

const NimPlantConsole = {
    nimplant: {
        id: 0,
        guid: null,
        active: false,
        externalIp: null,
        internalIp: null,
        username: null,
        hostname: null,
        pid: 0,
        lastCheckIn: null,
        // Details
        osBuild: null,
        sleep: 0,
        killAfter: 0,
        firstCheckIn: null,
        task: null,
        hostingFile: null,
        cryptKey: null
    },
    console: {
        id: '',
        lines: 0,
        result: ''
    }
}

/**
 * @return {Promise<Server>}
 */
export async function getServer() {
    try {
        const { data } = await http.get(endpoints.server);

        return data

    } catch (error) {
        console.error(error)
        return null
    }
}

/**
 * @return {Promise}
 */
export async function postServerExit() {
    try {
        const { data } = await http.post(endpoints.serverExit);

        return data

    } catch (error) {
        console.error(error)

        return error.response.data
    }
}

/**
 * @return {Promise<ServerConsole>}
 */
export async function getServerConsole() {
    try {
        const { data } = await http.get(endpoints.serverConsole(500));

        return data

    } catch (error) {
        console.error(error)

        return {
            id: 'CONSOLE',
            lines: 0,
            result: ""
        }
    }
}

/**
 * @return {Promise<Array<NimPlant>>}
 */
export async function getNimPlants() {
    try {
        const { data } = await http.get(endpoints.nimplants);

        let nimplants = data.nimplants?.map(nimplant => ({
            ...nimplant,
            lastCheckIn: parse(nimplant.lastCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
            firstCheckIn: parse(nimplant.firstCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
        }))

        return nimplants

    } catch (error) {
        console.error(error)
        return null
    }
}


/**
 *
 * @param guid
 * @return {Promise<NimPlant>}
 */
export async function getNimPlant(guid) {
    try {
        const { data } = await http.get(endpoints.nimplant(guid));

        let nimplant = {
            ...data,
            lastCheckIn: parse(data.lastCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
            firstCheckIn: parse(data.firstCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
        }

        return nimplant

    } catch (error) {
        console.error(error)
        return null
    }
}

/**
 *
 * @param guid
 * @return {Promise<NimPlantConsole>}
 */
export async function getNimPlantConsole(guid) {
    try {
        const { data } = await http.get(endpoints.nimplantConsole(guid, 1500));

        return {
            nimplant: {
                ...data.nimplant,
                lastCheckIn: parse(data.nimplant.lastCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
                firstCheckIn: parse(data.nimplant.firstCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
            },
            console: data.console
        }
    } catch (error) {
        console.error(error)

        return {
            nimplant: {
                guid,
            },
            console: {
                id: guid,
                lines: 0,
                result: ""
            }
        }
    }
}

/**
 *
 * @param guid
 * @return {Promise<Object>}
 */
export async function getNimPlantHistory(guid) {
    try {
        const { data } = await http.get(endpoints.nimplantHistory(guid, 1500));

        return {
            nimplant: {
                ...data.nimplant,
                lastCheckIn: parse(data.nimplant.lastCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
                firstCheckIn: parse(data.nimplant.firstCheckIn, 'dd/MM/yyyy HH:mm:ss', new Date()),
            },
            history: data.history
        }
    } catch (error) {
        console.error(error)

        return {
            nimplant: {
                guid,
            },
            history: []
        }
    }
}

/**
 *
 * @param {string} guid
 * @param {string} command
 * @return {Promise<{id, command, status: string}>}
 */
export async function postNimPlantCommand(guid, command) {
    if (command === "exit") {
        throw Error(`Cannot exit the server from a nimplant console.`)
    }

    try {
        const { data } = await http.post(endpoints.nimplantCommand(guid), { command });

        return {
            id: guid,
            command: command,
            ...data
        }
    } catch (error) {
        console.error(error)

        throw Error(`Could not run command "${command}" on nimplant "${guid}": ${error}`)
    }
}

/**
 *
 * @param {string} guid
 * @return {Promise<{id, command, status: string}>}
 */
export async function postNimPlantExit(guid) {
    try {
        const { data } = await http.post(endpoints.nimplantExit(guid));

        return {
            id: guid,
            command: "kill",
            ...data
        }
    } catch (error) {
        console.error(error)

        throw Error(`Could not run command "exit" on nimplant "${guid}": ${error}`)
    }
}

export default {
    getServer,
    postServerExit,
    getServerConsole,
    getNimPlants,
    getNimPlant,
    getNimPlantConsole,
    postNimPlantCommand,
    postNimPlantExit,
}