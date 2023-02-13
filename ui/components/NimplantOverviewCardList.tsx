import { FaRegMeh } from 'react-icons/fa'
import { getNimplants, restoreConnectionError, showConnectionError } from '../modules/nimplant'
import { Text, Group, Loader } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import NimplantOverviewCard from './NimplantOverviewCard'
import type Types from '../modules/nimplant.d'
import { useEffect } from 'react'

// Component for single nimplant card (for 'nimplants' overview screen)
function NimplantOverviewCardList() {
  const largeScreen = useMediaQuery('(min-width: 800px)')

  // Query API
  const {nimplants, nimplantsLoading, nimplantsError} = getNimplants()

  useEffect(() => {
    // Render placeholder if data is not yet available
    if (nimplantsError) {
      showConnectionError()
    } else if (nimplants) {
      restoreConnectionError()
    }
  })

  // Logic for displaying component
  if (nimplantsLoading || nimplantsError) {
    return (
      <Group py="xl" sx={(theme) => ({ color: theme.colors.gray[5] })}>
      <Loader variant="dots" />
      <Text size="md">Loading...</Text>
      </Group>
    )
  } 

  // Check data length and return placeholder if no nimplants are active
  if (nimplants.length === 0) return (
    <Group py="xl" sx={(theme) => ({ color: theme.colors.gray[5] })}>
    <FaRegMeh size='1.5em' />
    <Text size="md">Nothing here...</Text>
    </Group>
  )

  // Otherwise render the NimplantOverviewCard component for each nimplant
  return nimplants.map((np: Types.NimplantOverview) => (
    <NimplantOverviewCard key={np.guid} np={np} largeScreen={largeScreen} />
  ))
}

export default NimplantOverviewCardList