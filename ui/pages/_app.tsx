import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '../styles/global.css'

import { createTheme, MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import type { AppProps } from 'next/app';
import MainLayout from '../components/MainLayout';

// type ExtendedCustomColors = 'rose' | DefaultMantineColor;

// declare module '@mantine/core' {
//   export interface MantineThemeColorsOverride {
//     colors: Record<ExtendedCustomColors, Tuple<string, 10>>;
//   }
// }

const theme = createTheme({
  fontFamily: 'Inter, sans-serif',
  fontFamilyMonospace: 'Roboto Mono, Courier, monospace',
  headings: { fontFamily: 'Montserrat, sans-serif' },
  colors: {
    'rose': ['#FFF1F2', '#FFE4E6', '#FECDD3', '#FDA4AF', '#FB7185', '#F43F5E', '#E11D48', '#BE123C', '#9F1239', '#881337'],
  },
  primaryColor: 'rose',
});

// Define providers and main layout for all pages
export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <MantineProvider theme={theme}>
      <Notifications position="top-right" />
      <MainLayout>
        <Component {...pageProps} />
      </MainLayout>
    </MantineProvider>
  );
}
