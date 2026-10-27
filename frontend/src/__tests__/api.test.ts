import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  startDownloadTask,
  getDownloadTaskStatus,
  downloadWithFolderSelection,
} from '../services/api';

describe('API Service - Tarefas Assíncronas', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('startDownloadTask deve enviar requisição POST /api/download/start', async () => {
    const mockResponse = {
      task_id: 'task-123',
      status: 'pending',
      progress: 0.0,
      message: 'Tarefa enfileirada...',
    };

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(mockResponse),
    });
    vi.stubGlobal('fetch', mockFetch);

    const result = await startDownloadTask(
      'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      'video',
      '720p'
    );

    expect(mockFetch).toHaveBeenCalledWith('/api/download/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        media_type: 'video',
        resolution: '720p',
      }),
    });
    expect(result.task_id).toBe('task-123');
    expect(result.status).toBe('pending');
  });

  it('getDownloadTaskStatus deve consultar GET /api/download/task/:id', async () => {
    const mockResponse = {
      task_id: 'task-123',
      status: 'ready',
      progress: 100.0,
      message: 'Pronto!',
      filename: 'video.mp4',
    };

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(mockResponse),
    });
    vi.stubGlobal('fetch', mockFetch);

    const result = await getDownloadTaskStatus('task-123');

    expect(mockFetch).toHaveBeenCalledWith('/api/download/task/task-123');
    expect(result.status).toBe('ready');
    expect(result.filename).toBe('video.mp4');
  });

  it('downloadWithFolderSelection no modo fallback deve iniciar tarefa e acionar download direto', async () => {
    const startResp = {
      task_id: 'task-abc',
      status: 'pending',
      progress: 0.0,
    };

    const readyResp = {
      task_id: 'task-abc',
      status: 'ready',
      progress: 100.0,
      filename: 'teste.mp4',
    };

    const mockFetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockResolvedValue(startResp),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockResolvedValue(readyResp),
      });
    vi.stubGlobal('fetch', mockFetch);

    const statusUpdates: string[] = [];

    const result = await downloadWithFolderSelection(
      'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      'video',
      '720p',
      'Vídeo Teste',
      'mp4',
      (msg) => statusUpdates.push(msg)
    );

    expect(result).toBe('completed');
    expect(statusUpdates.length).toBeGreaterThan(0);
  });
});
