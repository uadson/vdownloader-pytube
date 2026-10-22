import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { UrlInput } from '../components/UrlInput';

describe('UrlInput Component', () => {
  it('deve renderizar o input com o placeholder correto', () => {
    render(<UrlInput onSubmit={vi.fn()} isLoading={false} />);
    const inputElement = screen.getByPlaceholderText(/Cole aqui o link do vídeo do YouTube/i);
    expect(inputElement).toBeInTheDocument();
  });

  it('deve disparar onSubmit com a url digitada ao enviar o formulário', () => {
    const handleSubmit = vi.fn();
    render(<UrlInput onSubmit={handleSubmit} isLoading={false} />);

    const inputElement = screen.getByPlaceholderText(/Cole aqui o link do vídeo do YouTube/i);
    fireEvent.change(inputElement, {
      target: { value: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' },
    });

    const submitButton = screen.getByRole('button', { name: /Obter Mídia/i });
    fireEvent.click(submitButton);

    expect(handleSubmit).toHaveBeenCalledWith('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  });

  it('deve desabilitar o botão e exibir carregamento quando isLoading for true', () => {
    render(<UrlInput onSubmit={vi.fn()} isLoading={true} />);
    const submitButton = screen.getByRole('button', { name: /Processando.../i });
    expect(submitButton).toBeDisabled();
  });
});
