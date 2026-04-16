import MyProfilePage from '@/frontend/my profile/page';
import { createClient } from '@/backend/supabase/server';

export default async function Profile() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  return <MyProfilePage user={user} />;
}
