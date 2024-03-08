import { Dots } from '../components/Dots';
import { FaGithub, FaHome, FaTwitter } from 'react-icons/fa'
import { Title, Text, Button, Container, useMantineTheme, ScrollArea } from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks'
import TitleBar from '../components/TitleBar'
import type { NextPage } from 'next'
import classes from '../styles/styles.module.css'

const Index: NextPage = () => {
  const largeScreen = useMediaQuery('(min-width: 800px)');
  const theme = useMantineTheme();
  
  return (
    <>
    <TitleBar title="Home" icon={<FaHome size='2em' />} />
    <ScrollArea ml={largeScreen ? "sm" : 0} mr={largeScreen ? "md" : "sm"} mt="xl">
      
    <Container className={classes.wrapper} size={1400}>
      <Dots className={classes.dots} style={{ left: 0, top: 0 }} />
      <Dots className={classes.dots} style={{ left: 60, top: 0 }} />
      <Dots className={classes.dots} style={{ left: 0, top: 140 }} />
      <Dots className={classes.dots} style={{ right: 0, top: 60 }} />

      <div className={classes.inner}>
        <Title className={classes.title}>
          A {' '}
          <Text component="span" color={theme.primaryColor} inherit>
            first-stage implant
          </Text>{' '}
          for adversarial operations
        </Title>

        <Container p={0} size={600}>
          <Text size="lg" color="dimmed" className={classes.description}>
            Nimplant is a lightweight stage-1 implant and C2 server. Get started using the action menu, or check out the Github repo for more information.
          </Text>
        </Container>

        <div className={classes.controls}>
          <Button 
            component="a" href="https://github.com/chvancooten/nimplant" target="_blank"
            leftSection={<FaGithub />} className={classes.control} size="lg" variant="default" color="gray"
          >
            View on GitHub
          </Button>
          <Button
            component="a" href="https://twitter.com/chvancooten" target="_blank"
            leftSection={<FaTwitter />} className={classes.control} size="lg"
          >
            Follow me on Twitter
          </Button>
        </div>
      </div>
    </Container>
      
    </ScrollArea>
    </>
  )
}

export default Index
