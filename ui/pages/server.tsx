import { getServerConsole, restoreConnectionError, showConnectionError } from '../modules/nimplant'
import { FaInfoCircle, FaServer, FaTerminal } from 'react-icons/fa'
import { Tabs } from '@mantine/core'
import { useEffect } from 'react'
import Console from '../components/Console'
import InfoCardListServer from '../components/InfoCardListServer'
import TitleBar from '../components/TitleBar'
import type { NextPage } from 'next'

// Tabbed page for showing server information
const ServerInfo: NextPage = () => { 

  const { serverConsole, serverConsoleLoading, serverConsoleError } = getServerConsole()

  useEffect(() => {
    if (serverConsoleError) {
      showConnectionError()
    } else if (serverConsole){
      restoreConnectionError()
    }
  })

  return (
    <>
    <TitleBar title="Server Info" icon={<FaServer size='2em' />} noBorder />
    <Tabs defaultValue="serverinfo">
      <Tabs.List mx={-25} grow>
        <Tabs.Tab value="serverinfo" icon={<FaInfoCircle />}>Information</Tabs.Tab>
        <Tabs.Tab value="serverconsole" icon={<FaTerminal />}>Console</Tabs.Tab>
      </Tabs.List>

      <Tabs.Panel value="serverinfo">
        <InfoCardListServer />
      </Tabs.Panel>

      <Tabs.Panel value="serverconsole">
        <Console consoleData={serverConsole} />
      </Tabs.Panel>

    </Tabs>
    </>
  )
}
export default ServerInfo