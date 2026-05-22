import { NextRequest, NextResponse } from 'next/server';
import pdfParse from 'pdf-parse';
import { createWorker } from 'tesseract.js';
import nlp from 'compromise';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    // Convert file to buffer
    const buffer = Buffer.from(await file.arrayBuffer());

    // Step 1: PDF Parsing
    let text = '';
    try {
      const data = await pdfParse(buffer);
      text = data.text;
    } catch (error) {
      // If PDF parsing fails, assume it's an image and use OCR
      const worker = await createWorker('eng');
      const { data: { text: ocrText } } = await worker.recognize(buffer);
      await worker.terminate();
      text = ocrText;
    }

    // Step 2: Preprocessing
    text = preprocessText(text);

    // Step 3: Model - Key Information Extraction
    const extractedInfo = extractKeyInfo(text);

    // Step 4: Postprocessing
    const jsonOutput = postprocess(extractedInfo);

    return NextResponse.json(jsonOutput);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to process PDF' }, { status: 500 });
  }
}

function preprocessText(text: string): string {
  // Clean the text: remove extra spaces, normalize
  return text.replace(/\s+/g, ' ').trim();
}

function extractKeyInfo(text: string) {
  const doc = nlp(text);

  // Extract name (assume first person mentioned)
  const people = doc.people().out('array');
  const name = people.length > 0 ? people[0] : 'Not found';

  // Extract email
  const emailMatch = text.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
  const email = emailMatch ? emailMatch[0] : 'Not found';

  // Extract phone
  const phoneMatch = text.match(/(\+?\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})/);
  const phone = phoneMatch ? phoneMatch[0] : 'Not found';

  // Extract skills (simple keyword matching)
  const skillsKeywords = ['javascript', 'python', 'java', 'react', 'node.js', 'sql', 'html', 'css'];
  const skills = skillsKeywords.filter(skill => text.toLowerCase().includes(skill.toLowerCase()));

  // Extract experience (simple regex for years)
  const experienceMatch = text.match(/(\d+)\s+years?\s+of\s+experience/i);
  const experience = experienceMatch ? experienceMatch[0] : 'Not found';

  // Extract education
  const education = doc.match('#Noun').out('array').filter((word: any) => ['bachelor', 'master', 'phd', 'degree'].includes(word.toLowerCase())).join(', ') || 'Not found';

  return { name, email, phone, skills, experience, education };
}

function postprocess(info: any) {
  return {
    extracted_information: info,
    pipeline: 'PDF → parsing → OCR → preprocessing → model → postprocessing → JSON'
  };
}