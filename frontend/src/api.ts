import { MemoryItem, PdfDocument, PdfChatMessage, SettingsState } from './types';

const API_BASE = '/api';

export async function startResearch(
  topic: string,
  targetWordCount = 2500,
  selfCorrectionRounds = 1,
  searchProvider = 'tavily',
  workspace = 'default'
) {
  const res = await fetch(`${API_BASE}/research/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic,
      target_word_count: targetWordCount,
      self_correction_rounds: selfCorrectionRounds,
      search_provider: searchProvider,
      workspace,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to start research' }));
    throw new Error(err.detail || 'Failed to start research');
  }
  return res.json();
}

export async function getResearchStatus(taskId: string) {
  const res = await fetch(`${API_BASE}/research/status/${taskId}`);
  if (!res.ok) throw new Error('Failed to fetch research status');
  return res.json();
}

export async function fetchMemories(query?: string, workspace = 'default'): Promise<MemoryItem[]> {
  const params = new URLSearchParams({ workspace });
  if (query) params.append('query', query);
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const res = await fetch(`${API_BASE}/memory?${params.toString()}`, {
      signal: controller.signal
    });
    if (!res.ok) throw new Error('Failed to fetch memories');
    return await res.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function deleteMemory(docId: string, workspace = 'default'): Promise<boolean> {
  const res = await fetch(`${API_BASE}/memory/${docId}?workspace=${workspace}`, {
    method: 'DELETE',
  });
  return res.ok;
}

export async function fetchPdfFiles(workspace = 'default'): Promise<PdfDocument[]> {
  const res = await fetch(`${API_BASE}/pdf/files?workspace=${workspace}`);
  if (!res.ok) throw new Error('Failed to list PDFs');
  return res.json();
}

export async function uploadPdf(file: File, workspace = 'default'): Promise<PdfDocument> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('workspace', workspace);

  const res = await fetch(`${API_BASE}/pdf/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to upload PDF' }));
    throw new Error(err.detail || 'Failed to upload PDF');
  }
  return res.json();
}

export async function chatPdf(query: string, filename?: string, workspace = 'default') {
  const res = await fetch(`${API_BASE}/pdf/chat?workspace=${workspace}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filename, top_k: 4 }),
  });
  if (!res.ok) throw new Error('PDF Chat failed');
  return res.json();
}

export async function exportReportPdf(title: string, markdownContent: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, markdown_content: markdownContent }),
  });
  if (!res.ok) throw new Error('Failed to generate PDF');
  return res.blob();
}

export async function exportReportLatex(title: string, markdownContent: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/latex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, markdown_content: markdownContent }),
  });
  if (!res.ok) throw new Error('Failed to generate LaTeX');
  return res.blob();
}

export async function exportReportBibtex(title: string, markdownContent?: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/bibtex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, markdown_content: markdownContent }),
  });
  if (!res.ok) throw new Error('Failed to generate BibTeX');
  return res.blob();
}

export async function fetchSettings(): Promise<SettingsState> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function updateSettings(keys: Record<string, string>): Promise<boolean> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(keys),
  });
  return res.ok;
}
