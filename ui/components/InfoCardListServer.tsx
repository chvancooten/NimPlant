import { FaServer, FaClock, FaHeadphones, FaInternetExplorer, FaSkull } from "react-icons/fa"
import { getListenerString, getServerInfo } from "../modules/nimplant";
import { Grid, Title, Text, Button, Skeleton, Stack } from "@mantine/core"
import { Highlight } from "./MainLayout";
import { useState } from "react";
import ExitServerModal from "./modals/ExitServer";
import InfoCard from "./InfoCard"

// Component for single information card (for server and nimplant data)
function InfoCardListServer() {
  const [exitModalOpen, setExitModalOpen] = useState(false);
  const { serverInfo, serverInfoLoading, serverInfoError } = getServerInfo()

  // Return the actual cards
  return (
    <Stack ml="xl" mr={40} mt="xl" spacing="xs">

      <ExitServerModal modalOpen={exitModalOpen} setModalOpen={setExitModalOpen} />

      <Button
        mb="sm"
        onClick={() => setExitModalOpen(true)}
        leftIcon={<FaSkull />} sx={{maxWidth:'200px'}}
      >
        Kill server
      </Button>

      <Title order={2}>
        Connection Information
      </Title>

      <Grid columns={2} gutter="lg">
        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaServer size='1.5em' />} content={
            <Skeleton visible={!serverInfo}>
              <Text>Connected to Server {' '}
                <Highlight>{serverInfo && serverInfo.name}</Highlight>
                {' '}at{' '}
                <Highlight>{serverInfo && `http://${serverInfo.config.managementIp}:${serverInfo.config.managementPort}`}</Highlight>
              </Text>
            </Skeleton>
          } />
        </Grid.Col>

        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaHeadphones size='1.5em' />} content={
            <Skeleton visible={!serverInfo}>
              <Text>Listener running at <Highlight>{serverInfo && getListenerString(serverInfo)}</Highlight></Text>
            </Skeleton>
          } />
        </Grid.Col>  
      </Grid>


      <Title order={2} pt={20}>
        Nimplant Profile
      </Title>

      <Grid columns={2} gutter="lg">
        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaClock size='1.5em' />} content={
            <Skeleton visible={!serverInfo}>
              <Text>
                Nimplants sleep for {' '}
                <Highlight>{serverInfo && `${serverInfo.config.sleepTime}`}</Highlight> 
                {' '}seconds (
                <Highlight>{serverInfo && `${serverInfo.config.sleepJitter}`}%</Highlight>
                {' '}jitter) by default. Kill date is{' '}
                <Highlight>{serverInfo && `${serverInfo.config.killDate}`}</Highlight>
              </Text>
            </Skeleton>
          } />
        </Grid.Col>
        
        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaInternetExplorer size='1.5em' />} content={
            <Skeleton visible={!serverInfo}>
              <Text>
                Default Nimplant user agent: <Highlight>{serverInfo && `${serverInfo.config.userAgent}`}</Highlight>
              </Text>
            </Skeleton>
          } />
        </Grid.Col>  
      </Grid>
    </Stack>
  )
}

export default InfoCardListServer