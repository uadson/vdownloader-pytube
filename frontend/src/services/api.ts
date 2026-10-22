import { VideoInfo } from '../types';

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
  onProgress?: (progress: DownloadProgress) => void
): Promise<'completed' | 'cancelled'> => {
  const downloadUrl = getDownloadUrl(videoUrl, mediaType, resolution);
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

    const response = await fetch(downloadUrl);
    if (!response.ok) {
      throw new Error('Falha ao processar download no servidor.');
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
          if (onProgress) {
            const percentage = totalBytes ? Math.round((loadedBytes / totalBytes) * 100) : undefined;
            onProgress({ loadedBytes, totalBytes, percentage });
          }
        }
      }
    } finally {
      await writable.close();
    }

    return 'completed';
  }

  // Fallback tradicional para navegadores que não suportam a API nativa ou mobile
  triggerDirectDownload(downloadUrl, suggestedFilename);
  return 'completed';
};
