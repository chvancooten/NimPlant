declare module Types {
    // Nimplant info
    export interface NimplantOverview {
        id: string;
        guid: string;
        active: boolean;
        ipAddrExt: string;
        ipAddrInt: string;
        username: string;
        hostname: string;
        pid: number;
        lastCheckin: string;
        late: boolean;
    }

    export interface ServerInfoConfig{
        killDate: string;
        listenerHost: string;
        listenerIp: string;
        listenerPort: number;
        listenerType: string;
        managementIp: string;
        managementPort: number;
        registerPath: string;
        resultPath: string;
        riskyMode: boolean;
        sleepJitter: number;
        sleepTime: number;
        taskPath: string;
        userAgent: string;
    }

    export interface ServerInfo {
        config: Config;
        guid: string;
        name: string;
        xorKey: number;
    }
}

export default nimplantTypes