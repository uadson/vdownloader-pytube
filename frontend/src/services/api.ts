import { VideoInfo } from '../types';

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

export const triggerDownload = (
  videoUrl: string,
  mediaType: 'video' | 'audio',
  resolution?: string | null
): void => {
  const downloadUrl = getDownloadUrl(videoUrl, mediaType, resolution);
  const anchor = document.createElement('a');
  anchor.href = downloadUrl;
  anchor.setAttribute('download', '');
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
};
