import { Paper, Group, Stack } from "@mantine/core"
import { ReactNode } from "react"

type InfoCardType = {
  icon: ReactNode,
  content: ReactNode,
}

// Component for single information card (for server and nimplant data)
function InfoCard({icon, content}: InfoCardType) {
  return (
    <Paper color="blue" shadow="sm" p="md" withBorder
    sx={{ height: '100%' }}
    >
      <Stack pl={5} align="flex-start" justify="space-evenly" spacing="lg" sx={{ height: '100%' }} >
        <Group sx={(theme) => ({ color: theme.colors.gray[3] })}>
          {icon}
        </Group>

        <Group sx={(theme) => ({ color: theme.colors.gray[7] })}>
          {content}
        </Group>
      </Stack>
    </Paper>
  )
}

export default InfoCard