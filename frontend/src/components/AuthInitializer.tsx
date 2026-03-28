'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';

const PUBLIC_PATHS = ['/auth/login', '/auth/register'];

export function AuthInitializer() {
  const hydrate = useAuthStore((s) => s.hydrate);
  const token = useAuthStore((s) => s.token);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (!pathname) return;
    const parts = pathname.split('/');
    const locale = parts[1] || 'de';
    const pathWithoutLocale = `/${parts.slice(2).join('/')}`;
    const isPublic = PUBLIC_PATHS.some((p) => pathWithoutLocale.startsWith(p));

    if (!token && !isPublic) {
      router.replace(`/${locale}/auth/login`);
    }
  }, [pathname, router, token]);

  return null;
}
