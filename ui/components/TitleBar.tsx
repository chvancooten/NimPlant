import { Group, Paper, Title } from "@mantine/core";
import React from "react";

type TitleBar = {
  title: string,
  icon: React.ReactNode,
  noBorder?: boolean,
}

// Simple title bar to show as page header
function TitleBar({ title, icon, noBorder = false }: TitleBar) {
  return (
    <>
      <Paper p="xl" pl={50} m={-25} mb={noBorder ? 0 : "md"} withBorder={noBorder ? false : true}
        style={{ height: '100px', backgroundColor: 'var(--mantine-color-gray-0)' }}
      >

        <Group>
          {icon} <Title order={1}>{title}</Title>
        </Group>

      </Paper>
    </>
  )
}

export default TitleBar