import JobSearchPage from '@/frontend/job search/page';
import { createClient } from '@/backend/supabase/server';

export default async function JobSearch() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  return <JobSearchPage user={user} />;
}
