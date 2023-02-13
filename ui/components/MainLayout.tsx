import React, { useState } from "react";
import Head from 'next/head';
import { AppShell, Header, Navbar, MediaQuery, Burger, useMantineTheme, Image, Badge, Space, Box, Text } from "@mantine/core";
import NavbarContents from "./NavbarContents";

// Basic component for highlighted text
export function Highlight({children}: {children: React.ReactNode}) {
  return <Text color='rose' component='span' weight={700}>{children}</Text>
}

// Main layout component
type ChildrenProps = React.PropsWithChildren<{}>;
function MainLayout({ children }: ChildrenProps) {
  const theme = useMantineTheme();
  const [sidebarOpened, setSidebarOpened] = useState(false)
  
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
        navbarOffsetBreakpoint="sm"
        fixed
        styles={() => ({
          main: { 
            paddingRight: '0px',
            height: 'calc(100vh-100px)',
           },
        })}  

        header={
          <Header height={100} p="md">
            <div style={{ display: 'flex', alignItems: 'center', width: '380px', height: '100%' }}>
              <MediaQuery largerThan="sm" styles={{ display: 'none' }}>
                <Burger
                  opened={sidebarOpened}
                  onClick={() => setSidebarOpened((o) => !o)}
                  size="sm"
                  color={theme.colors.gray[6]}
                  mr="xl"
                />
              </MediaQuery>
  
              <Image alt="Logo" m="sm" src='/nimplant-logomark.svg' fit='contain' height={70} />
              
              <MediaQuery smallerThan="sm" styles={{ display: 'none' }}>
                <Box style={{  alignSelf: "flex-end", marginBottom: "10px" }}>
                  <Space w="xs" />
                  <Badge component="a" href="https://github.com/chvancooten/nimplant" target="_blank" variant="light" color="gray"
                  style={{textTransform: 'lowercase',  cursor: 'pointer' }} >v1.0</Badge>
                </Box>
              </MediaQuery>
            </div>
          </Header>
        }

        navbar={
          <Navbar p="md" hiddenBreakpoint="sm" hidden={!sidebarOpened} width={{ sm: 215, lg: 300 }}
            styles={{ root: { background: theme.colors.rose[7], color: 'white' }}}
            onClick={() => setSidebarOpened(false)}
          >
            <NavbarContents />
          </Navbar>
        }
      >
        {children}
      </AppShell>        
    </>
  )
}

export default MainLayout