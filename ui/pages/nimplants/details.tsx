import { getNimplantConsole, getNimplantInfo, restoreConnectionError, showConnectionError, submitCommand } from '../../modules/nimplant'
import { FaTerminal, FaInfoCircle, FaLaptopCode } from 'react-icons/fa'
import { Tabs } from '@mantine/core'
import { useEffect, useState } from 'react'
import { useMediaQuery } from '@mantine/hooks'
import { useRouter } from 'next/router'
import Console from '../../components/Console'
import ErrorPage from 'next/error'
import InfoCardListNimplant from '../../components/InfoCardListNimplant'
import TitleBar from '../../components/TitleBar'
import type { NextPage } from 'next'

// Tabbed page for showing single nimplant information and console
const NimplantIndex: NextPage = () => {
    const largeScreen = useMediaQuery('(min-width: 800px)');

    const router = useRouter();
    const [activeTab, setActiveTab] = useState(1); // default to console tab

    const guid = router.query.guid as string
    const { nimplantInfo, nimplantInfoLoading, nimplantInfoError } = getNimplantInfo(guid)
    const { nimplantConsole, nimplantConsoleLoading, nimplantConsoleError } = getNimplantConsole(guid)

    useEffect(() => {
      // If the server responds but the GUID is not found, throw invalid GUID error
       if (nimplantInfoError && nimplantConsoleError){
        showConnectionError()
      } else {
        restoreConnectionError()
      }  
    })

    if (!guid || (!nimplantInfoLoading && nimplantInfo == "Invalid Nimplant GUID")){
      return <ErrorPage statusCode={404} />
    } else {
      return (
        <>
        <TitleBar title={largeScreen ? `Nimplant #${router.query.guid?.toString()}` : 'Nimplant'} icon={<FaLaptopCode size='2em' />} noBorder />

        <Tabs defaultValue="npconsole">
          <Tabs.List mx={-25} grow>
            <Tabs.Tab value="npinfo" icon={<FaInfoCircle />}>Information</Tabs.Tab>
            <Tabs.Tab value="npconsole" icon={<FaTerminal />}>Console</Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="npinfo">
            <InfoCardListNimplant guid={guid} />
          </Tabs.Panel>

          <Tabs.Panel value="npconsole">
            <Console 
              allowInput 
              consoleData={nimplantConsole}
              disabled={!nimplantInfo ? false : !nimplantInfo.active}
              guid={router.query.guid?.toString()}
              inputFunction={submitCommand}
            />
          </Tabs.Panel>
        </Tabs>
        </>
      )
    }
    
    
}
export default NimplantIndex