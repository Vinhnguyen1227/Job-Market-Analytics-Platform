import Groq from 'groq-sdk';
import { NextRequest } from 'next/server';

const SYSTEM_PROMPT = `You are CareerIntel AI, an expert career assistant for the Vietnamese job market.
Your role is to help users with:
- Job market trends and insights in Vietnam
- Career advice and development paths  
- Salary benchmarks across industries
- Resume/CV tips and improvements
- Interview preparation
- In-demand skills and certifications
- Top companies and industries hiring in Vietnam

Always be concise, practical, and encouraging. Use data-driven insights when possible.
Respond in the same language the user writes in (Vietnamese or English).`;

export async function POST(req: NextRequest) {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    return new Response(
      JSON.stringify({ error: 'GROQ_API_KEY is not set in environment variables.' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }

  try {
    const { messages } = await req.json();

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return new Response('Invalid request', { status: 400 });
    }

    const groq = new Groq({ apiKey });

    // Build messages array with system prompt
    const groqMessages = [
      { role: 'system' as const, content: SYSTEM_PROMPT },
      ...messages.map((m: { role: string; content: string }) => ({
        role: m.role === 'assistant' ? 'assistant' as const : 'user' as const,
        content: m.content,
      })),
    ];

    const stream = await groq.chat.completions.create({
      model: 'llama-3.3-70b-versatile',
      messages: groqMessages,
      stream: true,
      max_tokens: 1024,
    });

    // Pipe Groq stream to a ReadableStream for the browser
    const readableStream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder();
        try {
          for await (const chunk of stream) {
            const text = chunk.choices[0]?.delta?.content ?? '';
            if (text) {
              controller.enqueue(encoder.encode(text));
            }
          }
        } catch (err) {
          controller.error(err);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(readableStream, {
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  } catch (error: any) {
    console.error('[/api/chat] Groq error:', error?.message ?? error);
    return new Response(
      JSON.stringify({ error: error?.message ?? 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
