import { DownloadTaskStatus, VideoInfo } from '../types';

export interface DownloadProgress {
  loadedBytes: number;
  totalBytes?: number;
  percentage?: number;
}

interface FilePickerAcceptType {
  description?: string;
  accept: Record<string, string[]>;
}

interface SaveFilePickerOptions {
  suggestedName?: string;
  types?: FilePickerAcceptType[];
  excludeAcceptAllOption?: boolean;
}

interface WritableStreamHandle {
  write: (data: Blob | ArrayBuffer | Uint8Array) => Promise<void>;
  close: () => Promise<void>;
}

interface CustomFileHandle {
  createWritable: () => Promise<WritableStreamHandle>;
}

export const fetchVideoInfo = async (videoUrl: string): Promise<VideoInfo> => {
  const response = await fetch('/api/info', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: videoUrl.trim() }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Erro ao conectar ao servidor' }));
    throw new Error(errorData.detail || 'Não foi possível extrair os dados do vídeo.');
  }

  return response.json();
};

export const getDownloadUrl = (
  videoUrl: string,
  mediaType: 'video' | 'audio',
  resolution?: string | null
): string => {
  const params = new URLSearchParams({
    url: videoUrl,
    media_type: mediaType,
  });

  if (resolution) {
    params.append('resolution', resolution);
  }

  return `/api/download?${params.toString()}`;
};

export const startDownloadTask = async (
  videoUrl: string,
  mediaType: 'video' | 'audio',
  resolution?: string | null
): Promise<DownloadTaskStatus> => {
  const response = await fetch('/api/download/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url: videoUrl,
      media_type: mediaType,
      resolution: resolution || 'best',
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Falha ao iniciar processamento da mídia.' }));
    throw new Error(errorData.detail || 'Não foi possível registrar o download no servidor.');
  }

  return response.json();
};

export const getDownloadTaskStatus = async (taskId: string): Promise<DownloadTaskStatus> => {
  const response = await fetch(`/api/download/task/${taskId}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Tarefa de download não encontrada.' }));
    throw new Error(errorData.detail || 'Não foi possível consultar o status do download.');
  }
  return response.json();
};

export const getTaskDownloadUrl = (taskId: string): string => `/api/download/file/${taskId}`;

export const pollTaskUntilReady = async (
  taskId: string,
  onStatusUpdate?: (status: DownloadTaskStatus) => void,
  intervalMs: number = 1500,
  maxAttempts: number = 1200 // Suporta downloads longos de até 30 minutos
): Promise<DownloadTaskStatus> => {
  let attempts = 0;
  let consecutiveErrors = 0;
  const maxConsecutiveErrors = 5;

  while (attempts < maxAttempts) {
    try {
      const taskStatus = await getDownloadTaskStatus(taskId);
      consecutiveErrors = 0; // Reset ao obter resposta com sucesso

      if (onStatusUpdate) {
        onStatusUpdate(taskStatus);
      }

      if (taskStatus.status === 'ready') {
        return taskStatus;
      }

      if (taskStatus.status === 'failed') {
        throw new Error(taskStatus.error || 'Falha ao processar a mídia no servidor.');
      }
    } catch (err) {
      // Se for o erro de falha explícita da task lançado acima, propaga
      if (err instanceof Error && err.message.startsWith('Falha ao processar a mídia')) {
        throw err;
      }

      consecutiveErrors++;
      if (consecutiveErrors >= maxConsecutiveErrors) {
        throw new Error(
          err instanceof Error
            ? `Erro de conexão com o servidor: ${err.message}`
            : 'Perda de comunicação contínua com o servidor.'
        );
      }
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
    attempts++;
  }

  throw new Error('Tempo limite excedido ao processar a mídia no servidor.');
};

export const triggerDirectDownload = (downloadUrl: string, filename?: string): void => {
  const anchor = document.createElement('a');
  anchor.href = downloadUrl;
  if (filename) {
    anchor.setAttribute('download', filename);
  } else {
    anchor.setAttribute('download', '');
  }
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
};

export const downloadWithFolderSelection = async (
  videoUrl: string,
  mediaType: 'video' | 'audio',
  resolution: string | null | undefined,
  title: string,
  ext: string,
  onStatusChange?: (message: string, progress?: DownloadProgress) => void
): Promise<'completed' | 'cancelled'> => {
  const cleanTitle = title.replace(/[\\/*?:"<>|\uff5c]/g, '_').trim() || 'download';
  const suggestedFilename = `${cleanTitle}.${ext}`;

  // Se o navegador suporta a File System Access API (abre a janela do Explorer nativa)
  const windowWithPicker = window as unknown as {
    showSaveFilePicker?: (options: SaveFilePickerOptions) => Promise<CustomFileHandle>;
  };

  if (typeof windowWithPicker.showSaveFilePicker === 'function') {
    let fileHandle: CustomFileHandle;
    try {
      const mime = mediaType === 'audio' ? 'audio/mpeg' : 'video/mp4';
      fileHandle = await windowWithPicker.showSaveFilePicker({
        suggestedName: suggestedFilename,
        types: [
          {
            description: mediaType === 'audio' ? 'Arquivo de Áudio' : 'Arquivo de Vídeo',
            accept: {
              [mime]: [`.${ext}`],
            },
          },
        ],
      });
    } catch (err) {
      // Se o usuário clicou em Cancelar no Explorer
      if (err instanceof Error && err.name === 'AbortError') {
        return 'cancelled';
      }
      throw err;
    }

    if (onStatusChange) {
      onStatusChange('Iniciando processamento no servidor...');
    }

    // 1. Inicia a tarefa assíncrona no servidor
    const initialTask = await startDownloadTask(videoUrl, mediaType, resolution);

    // 2. Realiza polling do progresso no servidor até estar pronto
    const readyTask = await pollTaskUntilReady(initialTask.task_id, (task) => {
      if (onStatusChange) {
        if (task.message) {
          onStatusChange(task.message);
        } else if (task.status === 'downloading') {
          onStatusChange(`Baixando mídia no servidor: ${task.progress.toFixed(0)}%...`);
        } else if (task.status === 'processing') {
          onStatusChange('Mesclando faixas de mídia com FFmpeg...');
        }
      }
    });

    if (onStatusChange) {
      onStatusChange('Conectando e transferindo para a pasta selecionada...');
    }

    // 3. Transfere o arquivo gerado diretamente para o fileHandle escolhido no Explorer
    const fileDownloadUrl = getTaskDownloadUrl(readyTask.task_id);
    const response = await fetch(fileDownloadUrl);
    if (!response.ok) {
      throw new Error('Falha ao transferir arquivo processado do servidor.');
    }

    const contentLengthHeader = response.headers.get('content-length');
    const totalBytes = contentLengthHeader ? parseInt(contentLengthHeader, 10) : undefined;

    if (!response.body) {
      const blob = await response.blob();
      const writable = await fileHandle.createWritable();
      await writable.write(blob);
      await writable.close();
      return 'completed';
    }

    const reader = response.body.getReader();
    const writable = await fileHandle.createWritable();
    let loadedBytes = 0;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (value) {
          await writable.write(value);
          loadedBytes += value.length;
          if (onStatusChange) {
            const percentage = totalBytes ? Math.round((loadedBytes / totalBytes) * 100) : undefined;
            const progress: DownloadProgress = { loadedBytes, totalBytes, percentage };
            const mbs = (loadedBytes / (1024 * 1024)).toFixed(1);
            const msg = percentage !== undefined
              ? `Gravando no seu computador: ${percentage}% concluído (${mbs} MB)...`
              : `Gravando no seu computador: ${mbs} MB transferidos...`;
            onStatusChange(msg, progress);
          }
        }
      }
    } finally {
      await writable.close();
    }

    return 'completed';
  }

  // Fallback tradicional para mobile ou navegadores sem a File System Access API
  if (onStatusChange) {
    onStatusChange('Iniciando processamento no servidor...');
  }
  const initialTask = await startDownloadTask(videoUrl, mediaType, resolution);
  const readyTask = await pollTaskUntilReady(initialTask.task_id, (task) => {
    if (onStatusChange) {
      if (task.message) {
        onStatusChange(task.message);
      } else if (task.status === 'downloading') {
        onStatusChange(`Baixando mídia no servidor: ${task.progress.toFixed(0)}%...`);
      }
    }
  });

  const fileDownloadUrl = getTaskDownloadUrl(readyTask.task_id);
  triggerDirectDownload(fileDownloadUrl, suggestedFilename);
  return 'completed';
};
