import { showNotification, updateNotification } from '@mantine/notifications';
import { format } from 'date-fns';
import formatDistanceToNow from 'date-fns/formatDistanceToNow';
import parse from "date-fns/parse";
import useSWR from 'swr'
import Types from './nimplant.d'

//
// API definitions
//
if (!(process.env.NODE_ENV === 'development') && (typeof window !== "undefined")) {
    var baseUrl = window.location.origin;
} else {
    var baseUrl = 'http://localhost:31337';
}

const endpoints = {
    commands: `${baseUrl}/api/commands`,
    downloads: `${baseUrl}/api/downloads`,
    server: `${baseUrl}/api/server`,
    serverExit: `${baseUrl}/api/server/exit`,
    serverConsole:  (lines = 1000, offset = 0) => `${baseUrl}/api/server/console/${lines}/${offset}`,
    upload: `${baseUrl}/api/upload`,
    nimplants: `${baseUrl}/api/nimplants`,
    nimplantInfo: (guid: string) => `${baseUrl}/api/nimplants/${guid}`,
    nimplantExit: (guid: string) => `${baseUrl}/api/nimplants/${guid}/exit`,
    nimplantCommand: (guid: string) => `${baseUrl}/api/nimplants/${guid}/command`,
    nimplantConsole: (guid: string, lines = 1000, offset = 0) => `${baseUrl}/api/nimplants/${guid}/console/${lines}/${offset}`,
    nimplantHistory: (guid: string, lines = 1000, offset = 0) => `${baseUrl}/api/nimplants/${guid}/history/${lines}`,
}

const fetcher = async (
    input: RequestInfo,
    init: RequestInit,
    ...args: any[]
  ) => {
    const res = await fetch(input, init);
    return res.json();
  };


//
//  GET functions
//

export function getCommands () {
    const { data, error } = useSWR(endpoints.commands, fetcher)

    return {
        commandList: data,
        commandListLoading: !error && !data,
        commandListError: error
    }
}

export function getDownloads () {
    const { data, error } = useSWR(endpoints.downloads, fetcher,  { refreshInterval: 5000 })

    return {
        downloads: data,
        downloadsLoading: !error && !data,
        downloadsError: error
    }
}

export function getServerInfo () {
    const { data, error } = useSWR(endpoints.server, fetcher)

    return {
        serverInfo: data,
        serverInfoLoading: !error && !data,
        serverInfoError: error
    }
}

export function getServerConsole (lines = 5000) {
    const { data, error } = useSWR(endpoints.serverConsole(lines), fetcher, { refreshInterval: 5000 })

    return {
        serverConsole: data,
        serverConsoleLoading: !error && !data,
        serverConsoleError: error
    }
}

export function getNimplants () {
    const { data, error } = useSWR(endpoints.nimplants, fetcher, { refreshInterval: 2500 })

    return {
        nimplants: data,
        nimplantsLoading: !error && !data,
        nimplantsError: error
    }
}

export function getNimplantInfo (guid: string) {
    const { data, error } = useSWR(endpoints.nimplantInfo(guid), fetcher, { refreshInterval: 5000 })

    return {
        nimplantInfo: data,
        nimplantInfoLoading: !error && !data,
        nimplantInfoError: error
    }
}

export function getNimplantConsole (guid: string, lines = 5000) {
    const { data, error } = useSWR(endpoints.nimplantConsole(guid, lines), fetcher, { refreshInterval: 1000 })

    return {
        nimplantConsole: data,
        nimplantConsoleLoading: !error && !data,
        nimplantConsoleError: error
    }
}


//
// POST functions
//

export function serverExit(): void {
    fetch(endpoints.serverExit, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(() => {
        showNotification({
            title: 'OK',
            message: 'Server is shutting down',
            color: 'green'
        })
    })
    .catch(() => {
        showNotification({
            title: 'Error',
            message: 'Error shutting down server',
            color: 'red'
        })
    })
}

export function nimplantExit(guid: string): void {
    fetch(endpoints.nimplantExit(guid), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(() => {
        showNotification({
            title: 'OK',
            message: 'Killing Nimplant',
            color: 'green'
        })
    })
    .catch(() => {
        showNotification({
            title: 'Error',
            message: 'Error killing Nimplant',
            color: 'red'
        })
    })
}

export function submitCommand(guid: string, command: string, _callback: Function = () => {}): void {
    fetch(endpoints.nimplantCommand(guid), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
        }).then((res) => {
            if (res.ok) {
                showNotification({
                    title: 'OK',
                    message: 'Command \''+ command.split(' ')[0] + '\' submitted',
                    color: 'green',
                  })
                  _callback()
            } else {
                showNotification({
                    title: 'Error',
                    message: 'Error sending command',
                    color: 'red',
                  })
            }
    })
}

export function uploadFile(file: File, _callbackCommand: Function = () => {}, _callbackClose: Function = () => {}): void {

    // Warn if file size is too large (>5MB)
    if (file.size > 5242880) {
        if (!confirm("The selected file is larger than 5MB, which may cause unpredictable behavior.\nAre you sure you want to continue?")) {
            _callbackClose()
            return;
        }
    }
    
    // Upload file to server
    const formData = new FormData();
    formData.append('file', file);
    formData.append('filename', file.name);

    fetch(endpoints.upload, {
        method: 'POST',
        body: formData
    }).then((res) => {
        res.json().then((data) => {
            if (res.ok) {
                showNotification({
                    title: 'OK',
                    message: 'File uploaded to server',
                    color: 'green',
                })
                _callbackCommand(data.path)
            } else {
                showNotification({
                    title: 'Error',
                    message: 'Error uploading file',
                    color: 'red',
                })
            }
        })
    })
}


//
// UTILITY functions
//

// Format a date string from the server into a human readable string
export function timeSince(npDateTime: string): string {
    const dateTime = parse(npDateTime, 'dd/MM/yyyy HH:mm:ss', new Date())
    return formatDistanceToNow(dateTime, { includeSeconds: true, addSuffix: true });
}

// Format a number of bytes into a human readable string
export function formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = 1;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format an epoch timestamp into a human readable string
export function formatTimestamp(timestamp: number): string {
    return format(new Date(timestamp * 1000), 'yyyy/MM/dd HH:mm:ss')
}

// Get a simplified listener string from the server info object
export function getListenerString(serverInfo: Types.ServerInfo): string {
    const listenerHost = serverInfo.config.listenerHost ? serverInfo.config.listenerHost : serverInfo.config.listenerIp
    var listenerPort = `:${serverInfo.config.listenerPort}`
    if ((serverInfo.config.listenerType === "HTTP" && serverInfo.config.listenerPort === 80)
       || (serverInfo.config.listenerType === "HTTPS" && serverInfo.config.listenerPort === 443)) {
         listenerPort = ""
       }
    return `${serverInfo.config.listenerType.toLowerCase()}://${listenerHost}${listenerPort}`
}

// This will be replaced by a better system to show console outputs
export function consoleToText(json: any): string {
    var res = ""
    for(var i = 0; i < json.length; i++) {
        if (json[i].task) {
            res += `[${json[i].taskTime}] > ${json[i].taskFriendly}\n`
        }
        res += `[${json[i].resultTime}]   ${json[i].result}\n`
    }

    return res
}
export function showConnectionError(): void {
    showNotification({
        id: 'ConnErr',
        disallowClose: true,
        autoClose: false,
        title: "Connection error",
        message: 'Trying to reconnect to Nimplant API server',
        color: 'red',
        loading: true,
      });
}

export function restoreConnectionError(): void {
    updateNotification({
        id: 'ConnErr',
        color: 'teal',
        title: 'Connection restored',
        message: 'Connection to the Nimplant API server was restored',
        autoClose: 3000,
      });
}