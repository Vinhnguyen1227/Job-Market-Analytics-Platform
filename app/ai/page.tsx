import AIAssistantPage from '@/frontend/ai assistant/page';
import { createClient } from '@/backend/supabase/server';

export default async function AIPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  return <AIAssistantPage user={user} />;
}
