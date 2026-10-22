export interface DownloadOption {
  format_id: string;
  label: string;
  media_type: 'video' | 'audio';
  resolution: string | null;
  ext: string;
  is_audio: boolean;
}

export interface VideoInfo {
  id?: string;
  title: string;
  author: string;
  duration: number;
  duration_formatted: string;
  thumbnail: string;
  description: string;
  url: string;
  options: DownloadOption[];
}

export interface ApiError {
  detail: string;
}
