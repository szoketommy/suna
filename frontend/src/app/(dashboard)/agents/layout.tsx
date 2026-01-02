import { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'Worker Conversation | agentiK',
  description: 'Interactive Worker conversation powered by agentiK',
  openGraph: {
    title: 'Worker Conversation | agentiK',
    description: 'Interactive Worker conversation powered by agentiK',
    type: 'website',
  },
};

export default async function AgentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
