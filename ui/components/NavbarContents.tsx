import { Box, Center, Group, Image, AppShellSection, Text, UnstyledButton } from "@mantine/core";
import { FaHome, FaServer, FaLaptopCode, FaDownload } from 'react-icons/fa'
import { useMediaQuery } from "@mantine/hooks";
import Link from "next/link";
import React from "react";
import classes from '../styles/buttonstyles.module.css';

import { useRouter } from 'next/router'

interface MainLinkProps {
  icon: React.ReactNode;
  label: string;
  target: string;
  active: boolean;
}

// Component for single navigation items
function NavItem({ icon, label, target, active }: MainLinkProps) {
    const largeScreen = useMediaQuery('(min-width: 1200px)');
    return (
    <Link href={target} passHref style={{ textDecoration: 'none', color: 'inherit' }}>
      <UnstyledButton
        className={`${classes.button} ${active ? classes.buttonActive : classes.buttonInactive}`}
      >
        <Group>
          {icon} <Text size={largeScreen ? 'xl' : 'lg'}>{label}</Text>
        </Group>
      </UnstyledButton>
    </Link>
  );
}

// Construct the navbar
function NavbarContents() {
  const currentPath = useRouter().pathname

  return (
    <>
      <AppShellSection grow>
        <Box p="md">
          <NavItem icon={<FaHome size='1.5em' />} label="Home" target='/' active={currentPath === '/'} />
          <NavItem icon={<FaServer size='1.5em' />} label="Server" target='/server' active={currentPath === '/server'} />
          <NavItem icon={<FaDownload size='1.5em' />} label="Downloads" target='/downloads' active={currentPath === '/downloads'} />
          <NavItem icon={<FaLaptopCode size='1.5em' />} label="Nimplants" target='/nimplants' active={currentPath.startsWith('/nimplants')} />
        </Box>
      </AppShellSection>
      <AppShellSection>
        <Center>
          <Image alt='Logo' src='/nimplant.svg' h={60} />
        </Center>
      </AppShellSection>
    </>
  )
}

export default NavbarContents