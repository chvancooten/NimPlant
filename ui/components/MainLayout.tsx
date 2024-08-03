import React from "react";
import Head from 'next/head';
import { AppShell, Burger, useMantineTheme, Image, Badge, Space, Box, Text } from "@mantine/core";
import { useMediaQuery, useDisclosure } from "@mantine/hooks";
import NavbarContents from "./NavbarContents";

// Basic component for highlighted text
export function Highlight({ children }: { children: React.ReactNode }) {
  return <Text c='rose' component='span' fw={700}>{children}</Text>
}

// Main layout component
type ChildrenProps = React.PropsWithChildren<{}>;
function MainLayout({ children }: ChildrenProps) {
  const theme = useMantineTheme();
  const isSmallScreen = useMediaQuery('(max-width: 767px)'); // 'sm' breakpoint
  const [sidebarOpened, { toggle }] = useDisclosure();

  return (
    <>
      {/* Header information (static for all pages) */}
      <Head>
        <title key="title">Nimplant</title>
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="icon" type="image/png" href="/favicon.png" />
      </Head>

      {/* Main layout (header-sidebar-content) is managed via AppShell */}
      <AppShell
        header={{ height: 100 }}
        navbar={{
          width: { sm: 220, lg: 300 },
          breakpoint: 'sm',
          collapsed: { mobile: !sidebarOpened },
        }}
        padding="md"
      >
        <AppShell.Header style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Burger
            opened={sidebarOpened}
            onClick={toggle}
            hiddenFrom="sm"
            size="sm"
            color={theme.colors.gray[6]}
            p="xl"
          />

          <div style={{ display: 'flex', alignItems: 'center', width: '380px', height: '100%' }}>
            <Image alt="Logo" m="lg" mr="xs" src='/nimplant-logomark.svg' fit='contain' height={70} />

            {!isSmallScreen && (
              <Box mb="lg" style={{ alignSelf: "flex-end" }}>
                <Space w="xs" />
                <Badge
                  component="a"
                  href="https://github.com/chvancooten/nimplant"
                  target="_blank"
                  variant="light"
                  color="gray"
                  style={{ textTransform: 'lowercase', cursor: 'pointer' }}
                >
                  v1.4
                </Badge>
              </Box>
            )}
          </div>
        </AppShell.Header>

        <AppShell.Navbar p="md" style={{ background: theme.colors.rose[7], color: 'white' }} onClick={toggle}>
          <NavbarContents />
        </AppShell.Navbar>

        <AppShell.Main>
          {children}
        </AppShell.Main>
      </AppShell>
    </>
  )
}

export default MainLayout;