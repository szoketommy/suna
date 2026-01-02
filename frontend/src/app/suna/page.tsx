import { Metadata } from 'next';
import Link from 'next/link';
import { ArrowRight, Github } from 'lucide-react';
import Image from 'next/image';

export const metadata: Metadata = {
  title: 'agentiK is now agentiK | agentiK agentiK - Open Source AI Worker',
  description: 'agentiK has rebranded to agentiK. agentiK (formerly agentiK) is the same powerful open source AI assistant and generalist AI worker you know and love, now with a new name and bigger vision.',
  keywords: [
    'agentiK',
    'agentiK agentiK',
    'agentiK AI',
    'agentiK assistant',
    'agentiK.so',
    'where is agentiK',
    'agentiK',
    'agentiK rebrand',
    'agentiK is now agentiK',
    'AI assistant',
    'open source AI',
    'generalist AI worker',
    'AI worker',
    'autonomous AI',
  ],
  openGraph: {
    title: 'agentiK is now agentiK',
    description: 'agentiK (formerly agentiK) - Same powerful open source AI worker, new name.',
    type: 'website',
    url: 'https://www.agentik.com/agentik',
    siteName: 'agentiK',
    images: [
      {
        url: '/banner.png',
        width: 1200,
        height: 630,
        alt: 'agentiK - Formerly agentiK',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'agentiK is now agentiK',
    description: 'agentiK (formerly agentiK) - Same powerful open source AI worker, new name.',
    images: ['/banner.png'],
  },
  alternates: {
    canonical: 'https://www.agentik.com/agentik',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function agentiKPage() {
  return (
    <>
      {/* Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            name: 'agentiK',
            alternateName: ['agentiK', 'agentiK agentiK', 'agentiK AI'],
            url: 'https://www.agentik.com',
            logo: 'https://www.agentik.com/favicon.png',
            sameAs: [
              'https://github.com/agentik-ai',
              'https://x.com/agentik',
              'https://linkedin.com/company/agentik',
            ],
            description:
              'agentiK (formerly known as agentiK) is an open source generalist AI worker that helps you accomplish real-world tasks through natural conversation.',
          }),
        }}
      />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            itemListElement: [
              {
                '@type': 'ListItem',
                position: 1,
                name: 'Home',
                item: 'https://www.agentik.com',
              },
              {
                '@type': 'ListItem',
                position: 2,
                name: 'agentiK is now agentiK',
                item: 'https://www.agentik.com/agentik',
              },
            ],
          }),
        }}
      />

      <main className="w-full relative overflow-hidden bg-background">
        <div className="relative flex flex-col items-center w-full px-4 sm:px-6">
          {/* Hero Section with Logo */}
          <div className="relative z-10 pt-16 sm:pt-24 md:pt-32 mx-auto h-full w-full max-w-6xl flex flex-col items-center justify-center">
            <div className="flex flex-col items-center justify-center gap-3 sm:gap-4 pt-8 sm:pt-20 max-w-4xl mx-auto pb-10">
              {/* agentiK Symbol with grain texture */}
              <div className="relative mb-8 sm:mb-12" style={{ width: '80px', height: '80px' }}>
                <Image
                  src="/agentik-symbol.svg"
                  alt="agentiK"
                  fill
                  className="object-contain dark:invert"
                  priority
                  style={{ mixBlendMode: 'normal' }}
                />
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage: 'url(/grain-texture.png)',
                    backgroundSize: '100px 100px',
                    backgroundRepeat: 'repeat',
                    mixBlendMode: 'multiply',
                    opacity: 0.6,
                    maskImage: 'url(/agentik-symbol.svg)',
                    WebkitMaskImage: 'url(/agentik-symbol.svg)',
                    maskSize: 'contain',
                    WebkitMaskSize: 'contain',
                    maskRepeat: 'no-repeat',
                    WebkitMaskRepeat: 'no-repeat',
                    maskPosition: 'center',
                    WebkitMaskPosition: 'center',
                  }}
                />
              </div>

              {/* Main Heading */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-medium tracking-tighter text-balance text-center">
                agentiK
              </h1>

            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 w-full max-w-3xl mx-auto px-2 sm:px-0 pb-16">
              <Link
                href="/"
                className="flex h-12 items-center justify-center w-full sm:w-auto px-8 text-center rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-sm font-medium"
              >
                Go to agentiK
                <ArrowRight className="ml-2 size-4" />
              </Link>
              <a
                href="https://github.com/agentik-ai/agentik"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-12 items-center justify-center w-full sm:w-auto px-8 text-center rounded-full border border-border bg-background hover:bg-accent/50 transition-all font-medium"
              >
                <Github className="mr-2 size-4" />
                View on GitHub
              </a>
            </div>
          </div>

          {/* Content Sections */}
          <div className="relative z-10 w-full max-w-4xl mx-auto pb-20 sm:pb-32">
            <div className="space-y-20 sm:space-y-32 text-center">
              {/* What Changed */}
              <div className="space-y-6">
                <h2 className="text-2xl md:text-3xl lg:text-4xl font-medium tracking-tighter">
                  What changed?
                </h2>
                <div className="space-y-3 text-base md:text-lg text-muted-foreground font-medium">
                  <p>Our name changed from agentiK to agentiK</p>
                  <p>Our domain is now agentik.com</p>
                </div>
              </div>

              {/* Divider */}
              <div className="w-12 h-px bg-border mx-auto" />

              {/* What Stayed */}
              <div className="space-y-6">
                <h2 className="text-2xl md:text-3xl lg:text-4xl font-medium tracking-tighter">
                  What stayed the same?
                </h2>
                <div className="space-y-3 text-base md:text-lg text-muted-foreground font-medium">
                  <p>Same powerful AI capabilities</p>
                  <p>All your existing agents and workflows</p>
                </div>
              </div>

              {/* Divider */}
              <div className="w-12 h-px bg-border mx-auto" />

              {/* GitHub */}
              <div className="space-y-6">
                <h2 className="text-2xl md:text-3xl lg:text-4xl font-medium tracking-tighter">
                  Where to find us?
                </h2>
                <p className="text-base md:text-lg text-muted-foreground font-medium">
                  Our GitHub repository remains at github.com/agentik-ai/agentik
                </p>
              </div>
            </div>
          </div>

          {/* Footer Wordmark Section */}
          <div className="relative w-full mx-auto overflow-hidden pb-20 sm:pb-32">
            <div className="relative w-full max-w-5xl mx-auto aspect-[1150/344] px-8 md:px-16">
              <div className="relative w-full h-full" style={{ isolation: 'isolate' }}>
                <Image
                  src="/wordmark.svg"
                  alt="agentiK"
                  fill
                  className="object-contain dark:invert opacity-10"
                  priority
                  style={{ mixBlendMode: 'normal' }}
                />
                {/* Grain texture overlay */}
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage: 'url(/grain-texture.png)',
                    backgroundSize: '100px 100px',
                    backgroundRepeat: 'repeat',
                    mixBlendMode: 'multiply',
                    opacity: 0.6,
                    maskImage: 'url(/wordmark.svg)',
                    WebkitMaskImage: 'url(/wordmark.svg)',
                    maskSize: 'contain',
                    WebkitMaskSize: 'contain',
                    maskRepeat: 'no-repeat',
                    WebkitMaskRepeat: 'no-repeat',
                    maskPosition: 'center',
                    WebkitMaskPosition: 'center',
                  }}
                />
              </div>
            </div>
          </div>

          {/* SEO Footer Text */}
          <div className="relative z-10 text-center max-w-2xl mx-auto pb-20 pt-12 border-t border-border/50">
            <p className="text-sm text-muted-foreground/60 leading-relaxed font-medium">
              Looking for agentiK? You've found us. agentiK is the evolution of agentiK — the same open
              source AI assistant and generalist AI worker, now with a name that better represents
              our vision. For users searching for "agentiK AI", "agentiK assistant", "agentiK.so", "where is
              agentiK", or "agentiK agentiK" — this is the official continuation of the agentiK project under
              the agentiK brand.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
