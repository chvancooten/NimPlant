import { Group, Paper, Title } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import React from "react";

type TitleBar = {
  title: string,
  icon: React.ReactNode,
  noBorder?: boolean,
}

// Simple title bar to show as page header
function TitleBar({title, icon, noBorder=false} : TitleBar) {
  return (
    <>
      <Paper p="xl" pl={50} m={-25} mb={noBorder ? 0 : "md"} withBorder={noBorder ? false : true}
      sx={(theme) => ({
        height: '100px',
        backgroundColor: theme.colors.gray[0],
      })}>
    
        <Group>
          {icon} <Title order={1}>{title}</Title>
        </Group>

      </Paper>
    </>
  )
}

export default TitleBar