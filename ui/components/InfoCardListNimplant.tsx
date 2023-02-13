import { FaClock, FaLaptopCode, FaFingerprint, FaWindows, FaNetworkWired, FaSkull } from "react-icons/fa"
import { getNimplantInfo, nimplantExit, timeSince } from "../modules/nimplant";
import { Grid, Title, Text, Modal, Button, Space, Skeleton, Stack } from "@mantine/core"
import { Highlight } from "./MainLayout";
import InfoCard from "./InfoCard"
import { useState } from "react";

// Component for single information card (for server and nimplant data)
function InfoCardListNimplant({guid}: {guid: string}) {
  const [exitModalOpen, setExitModalOpen] = useState(false);
  const { nimplantInfo, nimplantInfoLoading, nimplantInfoError } = getNimplantInfo(guid)

  // Return the actual cards
  return (
    <Stack ml="xl" mr={40} mt="xl" spacing="xs">

      <Modal
        opened={exitModalOpen}
        onClose={() => setExitModalOpen(false)}
        title={<b>Danger zone!</b>}
        centered
      >
        Are you sure you want to kill this Nimplant? 

        <Space h='xl' />

        <Button 
          onClick={() => {setExitModalOpen(false); nimplantExit(guid)}}
          leftIcon={<FaSkull />} sx={{width: '100%'}}
        >
          Yes, kill kill kill!
        </Button>
      </Modal>

      <Button
        mb="sm"
        onClick={() => setExitModalOpen(true)}
        leftIcon={<FaSkull />} sx={{maxWidth:'200px'}}
      >
        Kill Nimplant
      </Button>

      <Title order={2}>
        Nimplant Information
      </Title>

      <Grid columns={2} gutter="lg">
        <Grid.Col xs={2} md={2}>
          <InfoCard icon={<FaLaptopCode size='1.5em' />} content={
            <Skeleton visible={!nimplantInfo}>
              <Text>
                Nimplant <Highlight>#{nimplantInfo && nimplantInfo.id}</Highlight>{' '}
                (GUID <Highlight>{nimplantInfo && nimplantInfo.guid}</Highlight>)
              </Text>
            </Skeleton>
          } />
        </Grid.Col>

        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaClock size='1.5em' />} content={
            <Skeleton visible={!nimplantInfo}>
              <Text sx={{whiteSpace: 'pre-line'}}>
                Last seen: <Highlight>{nimplantInfo && timeSince(nimplantInfo.lastCheckin)}</Highlight>{' '}
                (sleep <Highlight>{nimplantInfo && nimplantInfo.sleepTime} seconds</Highlight>,{' '}
                jitter <Highlight>{nimplantInfo && nimplantInfo.sleepJitter}%</Highlight>){'\n'}
                First seen: <Highlight>{nimplantInfo && timeSince(nimplantInfo.firstCheckin)}</Highlight>{' '}
                (kill date <Highlight>{nimplantInfo && nimplantInfo.killDate}</Highlight>)
              </Text>
            </Skeleton>
          } />
        </Grid.Col>  

        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaFingerprint size='1.5em' />} content={
            <Skeleton visible={!nimplantInfo}>
              <Text sx={{whiteSpace: 'pre-line'}}>
                Username: <Highlight>{nimplantInfo && nimplantInfo.username}</Highlight>{'\n'}
                Hostname: <Highlight>{nimplantInfo && nimplantInfo.hostname}</Highlight>
              </Text>
            </Skeleton>
          } />
        </Grid.Col>  

        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaNetworkWired size='1.5em' />} content={
            <Skeleton visible={!nimplantInfo}>
              <Text sx={{whiteSpace: 'pre-line'}}>
                Internal IP address: <Highlight>{nimplantInfo && nimplantInfo.ipAddrInt}</Highlight>{'\n'}
                External IP address: <Highlight>{nimplantInfo && nimplantInfo.ipAddrExt}</Highlight>
              </Text>
            </Skeleton>
          } />
        </Grid.Col>
        
        <Grid.Col xs={2} md={1}>
          <InfoCard icon={<FaWindows size='1.5em' />} content={
            <Skeleton visible={!nimplantInfo}>
              <Text sx={{whiteSpace: 'pre-line'}}>
              <Highlight>{nimplantInfo && nimplantInfo.osBuild}</Highlight>{'\n'}
                Process <Highlight>{nimplantInfo && nimplantInfo.pname}</Highlight> (ID <Highlight>{nimplantInfo && nimplantInfo.pid}</Highlight>)
              </Text>
            </Skeleton>
          } />
        </Grid.Col>  
      </Grid>
    </Stack>
  )
}

export default InfoCardListNimplant