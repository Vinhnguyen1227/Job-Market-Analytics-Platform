import MyProfilePage from '@/frontend/my profile/page';
import { createClient } from '@/backend/supabase/server';
import { PageErrorBoundary } from '@/frontend/components/PageErrorBoundary';
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My Profile',
  description: 'Quản lý hồ sơ cá nhân, kinh nghiệm làm việc, học vấn và kỹ năng của bạn trên CareerIntel.',
}

export default async function Profile() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  return (
    <PageErrorBoundary pageName="Hồ sơ cá nhân">
      <MyProfilePage user={user} />
    </PageErrorBoundary>
  );
}
