import { Building2, User, GraduationCap, Newspaper, FileText } from 'lucide-react';
import { LucideIcon } from 'lucide-react';

export function getEntityIcon(type?: string): LucideIcon {
  const typeLower = type?.toLowerCase() || '';
  if (typeLower === 'company') return Building2;
  if (typeLower === 'person') return User;
  if (typeLower === 'research_paper' || typeLower === 'researchpaper') return GraduationCap;
  if (typeLower === 'article') return Newspaper;
  return FileText;
}
