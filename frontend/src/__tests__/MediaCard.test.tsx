import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MediaCard } from '../components/MediaCard';
import { VideoInfo } from '../types';

const mockMedia: VideoInfo = {
  id: 'test1234',
  title: 'Vídeo Exemplo de Teste',
  author: 'Canal de Tecnologia',
  duration: 210,
  duration_formatted: '03:30',
  thumbnail: 'https://i.ytimg.com/vi/test/hqdefault.jpg',
  description: 'Esta é uma descrição de teste para o vídeo.',
  url: 'https://www.youtube.com/watch?v=test1234',
  options: [
    {
      format_id: 'video_720p',
      label: 'Vídeo 720p (HD)',
      media_type: 'video',
      resolution: '720p',
      ext: 'mp4',
      is_audio: false,
    },
    {
      format_id: 'audio_mp3',
      label: 'Áudio MP3 (Melhor Qualidade)',
      media_type: 'audio',
      resolution: null,
      ext: 'mp3',
      is_audio: true,
    },
  ],
};

describe('MediaCard Component', () => {
  it('deve renderizar título, autor, duração e thumbnail do vídeo', () => {
    render(<MediaCard media={mockMedia} />);

    expect(screen.getByText('Vídeo Exemplo de Teste')).toBeInTheDocument();
    expect(screen.getByText('Canal de Tecnologia')).toBeInTheDocument();
    expect(screen.getByText('03:30')).toBeInTheDocument();

    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', 'https://i.ytimg.com/vi/test/hqdefault.jpg');
  });

  it('deve exibir opções de vídeo inicialmente e permitir alternar para áudio', () => {
    render(<MediaCard media={mockMedia} />);

    expect(screen.getByText('Vídeo 720p (HD)')).toBeInTheDocument();

    // Clica na aba de Áudio
    const audioTabButton = screen.getByRole('button', { name: /Áudio \(1\)/i });
    fireEvent.click(audioTabButton);

    expect(screen.getByText('Áudio MP3 (Melhor Qualidade)')).toBeInTheDocument();
  });
});
