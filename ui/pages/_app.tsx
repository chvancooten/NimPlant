import '../styles/global.css'
import { MantineProvider, Tuple, DefaultMantineColor } from '@mantine/core';
import { NotificationsProvider } from '@mantine/notifications';
import MainLayout from '../components/MainLayout';
import type { AppProps } from 'next/app'

type ExtendedCustomColors = 'rose' | DefaultMantineColor;

declare module '@mantine/core' {
  export interface MantineThemeColorsOverride {
    colors: Record<ExtendedCustomColors, Tuple<string, 10>>;
  }
}

// Define providers and main layout for all pages
function MyApp({ Component, pageProps }: AppProps) {
  return (
  <>
    <MantineProvider 
      withGlobalStyles
      withNormalizeCSS
      theme={{
        fontFamily: 'Inter, sans-serif',
        fontFamilyMonospace: 'Roboto Mono, Courier, monospace',
        headings: { fontFamily: 'Montserrat, sans-serif' },
        colors: {
          'rose': ['#FFF1F2', '#FFE4E6', '#FECDD3', '#FDA4AF', '#FB7185', '#F43F5E', '#E11D48', '#BE123C', '#9F1239', '#881337'],
        },
        primaryColor: 'rose',
      }}>
        <NotificationsProvider position="top-right">
          <MainLayout>
              <Component {...pageProps} />
          </MainLayout>
        </NotificationsProvider>
    </MantineProvider>
  </>
  );
}

export default MyApp
