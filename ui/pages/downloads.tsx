import { FaDownload } from 'react-icons/fa'
import { Card, Group, ScrollArea, Text } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import DownloadList from '../components/DownloadList'
import TitleBar from '../components/TitleBar'
import type { NextPage } from 'next'

// Tabbed page for showing server information
const ServerInfo: NextPage = () => {
  const largeScreen = useMediaQuery('(min-width: 800px)')

  return (
    <>
    <TitleBar title="Downloads" icon={<FaDownload size='2em' />} noBorder />
    <ScrollArea ml={largeScreen ? "sm" : 0} mr={largeScreen ? "lg" : "sm"} mt="xl">
      <Group pl={largeScreen ? 25 : 10} mb="lg" grow sx={(theme) => ({ color: theme.colors.gray[5] })}>
        <Text size="lg">
          Filename
        </Text>
        <Text size="lg">
          Size
        </Text>
        <Text size="lg">
          Downloaded
        </Text>
      </Group>

      <Card withBorder radius="md" my="sm" py={0} px={largeScreen? "xl" : "sm"}>
        <DownloadList />
      </Card>
    </ScrollArea>
    </>
  )
}
export default ServerInfo