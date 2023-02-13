import { createStyles, Title, Text, Button, Container, useMantineTheme, ScrollArea } from '@mantine/core';
import { FaGithub, FaHome, FaTwitter } from 'react-icons/fa'
import { useMediaQuery } from '@mantine/hooks'
import TitleBar from '../components/TitleBar'
import type { NextPage } from 'next'
import { Dots } from '../components/Dots';

// Source: https://github.com/mantinedev/ui.mantine.dev/blob/master/components/HeroText/HeroText.tsx
const useStyles = createStyles((theme) => ({
  wrapper: {
    position: 'relative',
    paddingTop: 120,
    paddingBottom: 80,

    '@media (max-width: 755px)': {
      paddingTop: 80,
      paddingBottom: 60,
    },
  },

  inner: {
    position: 'relative',
    zIndex: 1,
  },

  dots: {
    position: 'absolute',
    color: theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[1],

    '@media (max-width: 755px)': {
      display: 'none',
    },
  },

  dotsLeft: {
    left: 0,
    top: 0,
  },

  title: {
    textAlign: 'center',
    fontWeight: 800,
    fontSize: 40,
    letterSpacing: -1,
    color: theme.colorScheme === 'dark' ? theme.white : theme.black,
    marginBottom: theme.spacing.xs,
    fontFamily: `Greycliff CF, ${theme.fontFamily}`,

    '@media (max-width: 520px)': {
      fontSize: 28,
      textAlign: 'left',
    },
  },

  description: {
    textAlign: 'center',

    '@media (max-width: 520px)': {
      textAlign: 'left',
      fontSize: theme.fontSizes.md,
    },
  },

  controls: {
    marginTop: theme.spacing.lg,
    display: 'flex',
    justifyContent: 'center',

    '@media (max-width: 520px)': {
      flexDirection: 'column',
    },
  },

  control: {
    '&:not(:first-of-type)': {
      marginLeft: theme.spacing.md,
    },

    '@media (max-width: 520px)': {
      height: 42,
      fontSize: theme.fontSizes.md,

      '&:not(:first-of-type)': {
        marginTop: theme.spacing.md,
        marginLeft: 0,
      },
    },
  },
}));

const Index: NextPage = () => {
  const largeScreen = useMediaQuery('(min-width: 800px)');
  const { classes } = useStyles();
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
            leftIcon={<FaGithub />} className={classes.control} size="lg" variant="default" color="gray"
          >
            View on GitHub
          </Button>
          <Button
            component="a" href="https://twitter.com/chvancooten" target="_blank"
            leftIcon={<FaTwitter />} className={classes.control} size="lg"
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
