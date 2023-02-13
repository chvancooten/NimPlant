import { FaLink, FaUnlink, FaNetworkWired, FaCloud, FaFingerprint, FaClock, FaAngleRight } from 'react-icons/fa'
import { Text, Group, Stack, Space } from '@mantine/core'
import { timeSince } from '../modules/nimplant';
import Link from 'next/link'
import React from "react";
import Types from '../modules/nimplant.d'

type NimplantOverviewCardType = {
  np: Types.NimplantOverview
  largeScreen: boolean,
}

// Component for single nimplant card (for 'nimplants' overview screen)
function NimplantOverviewCard({np, largeScreen} : NimplantOverviewCardType) {
  return (
    <Group grow py={20} pl={largeScreen ? 50 : 0}
      sx={(theme) => ({ 
        '&:not(:last-child)': {
          borderBottom: `1px solid ${theme.colors.gray[1]}`,
        },

        '&:hover': {
          cursor: 'pointer',
        }
      })}
    >
      <Link href={`/nimplants/details?guid=${np.guid}`} passHref style={{ textDecoration: 'none' }}>
        <Group sx={(theme) => ({ color: theme.colors.gray[7] })} grow>
          <Group>
            <Group ml={largeScreen ? -50 : 0} hidden={largeScreen ? false : false} 
              sx={(theme) => (np.late
                              ? { color: theme.colors.orange[3] }
                              : np.active
                                ? { color: theme.colors.green[3] }
                                : { color: theme.colors.rose[3] }
                              )}
            >
              {np.active && !np.late ? <FaLink size='1.5em' /> : <FaUnlink size='1.5em' />}
            </Group>
            <Stack spacing={0} align="flex-start">
              <Text weight="bold" pl={largeScreen ? 10 : 0} 
                sx={(theme) => ({ color: theme.colors.rose[6] })}
              >
                {largeScreen ? `${np.id} - ${np.guid}` : np.guid}
              </Text>

              <Group pl={largeScreen ? 10 : 0}
                sx={(theme) => ({ color: theme.colors.gray[5] })}
              >
                <Group hidden={largeScreen ? false : true}>
                  <FaClock />
                </Group>
                <Text ml={largeScreen ? -10 : 0}>
                  {timeSince(np.lastCheckin)}
                </Text>
                </Group>
            </Stack>
          </Group>

          <Group pl={largeScreen ? 10 : 0}>
            <Stack spacing={0} align="flex-start">
              <Text>
                {np.username} @ {np.hostname}
              </Text>
              <Group 
                sx={(theme) => ({ color: theme.colors.gray[5] })}
              >
                <Group hidden={largeScreen ? false : true}>
                  <FaFingerprint />
                </Group>
                <Text ml={largeScreen ? -10 : 0}>{np.pname} ({np.pid})</Text>
              </Group>
            </Stack>
          </Group>

          <Group pl={largeScreen ? 15 : 5}>
            <Stack spacing={0} align="flex-start">
              <Group>
                <Group hidden={largeScreen ? false : true}>
                  <FaNetworkWired />
                </Group>
                <Text ml={largeScreen ? -10 : 0}>{np.ipAddrInt}</Text>
              </Group>
              <Group 
                sx={(theme) => ({ color: theme.colors.gray[5] })}
              >
                <Group hidden={largeScreen ? false : true}>
                  <FaCloud />
                </Group>
                <Text ml={largeScreen ? -10 : 0}>{np.ipAddrExt}</Text>
              </Group>
            </Stack>

            <Group hidden={largeScreen ? false : true} m={0} p={0}
              sx={(theme) => ({ color: theme.colors.gray[5], position: 'absolute', float: 'right', right: '50px'})}
            >
              <Space />
              <FaAngleRight size="1.5em" />
            </Group>

          </Group>
        </Group>
      </Link>
    </Group>
  )
}

export default NimplantOverviewCard