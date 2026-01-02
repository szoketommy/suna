import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'API Keys | agentiK',
  description: 'Manage your API keys for programmatic access to agentiK',
  openGraph: {
    title: 'API Keys | agentiK',
    description: 'Manage your API keys for programmatic access to agentiK',
    type: 'website',
  },
};

export default async function APIKeysLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
