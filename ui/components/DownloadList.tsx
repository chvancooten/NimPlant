import { FaRegMeh } from 'react-icons/fa'
import { formatBytes, formatTimestamp, getDownloads } from '../modules/nimplant'
import { Text, Group } from '@mantine/core'
import Link from 'next/link'

function DownloadList() {
  const { downloads, downloadsLoading, downloadsError } = getDownloads()


  // Check data length and return placeholder if no downloads are present
  if (!downloads || downloads.length === 0) return (
      <Group py="xl" sx={(theme) => ({ color: theme.colors.gray[5] })}>
        <FaRegMeh size='1.5em' />
        <Text size="md">Nothing here...</Text>
      </Group>
  )

  // Otherwise render an overview of downloads
  return (
  <>
  {downloads.map((file: any, index: number) => (
    <Group key={index} py="xl" grow
    sx={(theme) => ({ 
      '&:not(:last-child)': {
        borderBottom: `1px solid ${theme.colors.gray[1]}`,
      },
      
      '&:hover': {
        cursor: 'pointer',
      }
    })}
  >
      <Link href={`/api/downloads/${file.name}`} passHref style={{ textDecoration: 'none' }}>
        <Group grow>
        <Text size="lg" color="dark">
          {file.name}
        </Text>
        <Text pl={10} size="lg" color="gray">
          {formatBytes(file.size)}
        </Text>
        <Text pl={20} size="lg" color="gray">
          {formatTimestamp(file.lastmodified)}
        </Text>
        </Group>
      </Link>
    </Group>
  ))}
  </>
  )
}

export default DownloadList