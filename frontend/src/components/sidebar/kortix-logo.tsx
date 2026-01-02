'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface agentiKLogoProps {
  size?: number;
  variant?: 'symbol' | 'logomark';
  className?: string;
}

export function agentiKLogo({ size = 24, variant = 'symbol', className }: agentiKLogoProps) {
  const { theme, systemTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // After mount, we can access the theme
  useEffect(() => {
    setMounted(true);
  }, []);

  const shouldInvert = mounted && (
    theme === 'dark' || (theme === 'system' && systemTheme === 'dark')
  );

  // For logomark variant, use logomark-white.svg which is already white
  // and invert it for light mode instead
  if (variant === 'logomark') {
    return (
      <img
        src="/logomark-white.svg"
        alt="agentiK"
        className={cn(`${shouldInvert ? '' : 'invert'} flex-shrink-0`, className)}
        style={{ height: `${size}px`, width: 'auto' }}
      />
    );
  }

  // Default symbol variant behavior
  return (
    <img
      src="/agentik-symbol.svg"
      alt="agentiK"
      className={cn(`${shouldInvert ? 'invert' : ''} flex-shrink-0`, className)}
      style={{ width: `${size}px`, height: `${size}px` }}
    />
  );
}
