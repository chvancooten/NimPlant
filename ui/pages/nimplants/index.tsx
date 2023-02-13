import { FaLaptopCode } from 'react-icons/fa'
import { Text, ScrollArea, Group, Card, Loader } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import TitleBar from '../../components/TitleBar'
import type { NextPage } from 'next'
import NimplantOverviewCardList from '../../components/NimplantOverviewCardList'

// Overview page for showing real-time information for all nimplants
const NimplantList: NextPage = () => {
  const largeScreen = useMediaQuery('(min-width: 800px)')
  
  return (
    <>
    <TitleBar title="Nimplants" icon={<FaLaptopCode size='2em' />} />
    <ScrollArea ml={largeScreen ? "sm" : 0} mr={largeScreen ? "lg" : "sm"} mt="xl">
      <Group pl={largeScreen ? 75 : 10} mb="lg" grow sx={(theme) => ({ color: theme.colors.gray[5] })}>
        <Text size="lg">
          Nimplant
        </Text>
        <Text size="lg">
          System
        </Text>
        <Text size="lg">
          Network
        </Text>
      </Group>

      <Card withBorder radius="md" py={0} px={largeScreen? "xl" : "sm"}>
        <NimplantOverviewCardList />
      </Card>
    </ScrollArea>
    </>
  )
}
export default NimplantList