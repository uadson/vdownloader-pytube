import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { UrlInput } from './components/UrlInput';
import { MediaCard } from './components/MediaCard';
import { fetchVideoInfo } from './services/api';
import { VideoInfo } from './types';
import { AlertCircle, Youtube, Shield, Smartphone, Monitor } from 'lucide-react';

export const App: React.FC = () => {
  const [currentMedia, setCurrentMedia] = useState<VideoInfo | null>(null);

  const mutation = useMutation({
    mutationFn: (url: string) => fetchVideoInfo(url),
    onSuccess: (data) => {
      setCurrentMedia(data);
    },
  });

  const handleFetch = (url: string) => {
    mutation.mutate(url);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8 sm:py-12 flex flex-col items-center">
        {/* Hero Section */}
        <div className="text-center max-w-2xl mb-8 space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-brand-300 mb-2">
            <Youtube className="w-4 h-4 text-red-500" />
            <span>Suporte a Vídeos em HD, Full HD e Áudios em MP3</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-br from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Baixe seus vídeos favoritos com simplicidade
          </h1>

          <p className="text-slate-400 text-sm sm:text-base">
            Insira o link do YouTube abaixo para extrair detalhes, visualizar miniatura e realizar o download diretamente para seu computador ou celular.
          </p>
        </div>

        {/* Input Form */}
        <div className="w-full mb-8">
          <UrlInput onSubmit={handleFetch} isLoading={mutation.isPending} />
        </div>

        {/* Feedback de Erro */}
        {mutation.isError && (
          <div className="w-full max-w-2xl mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-start space-x-3 text-sm animate-fade-in">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Erro ao obter vídeo</p>
              <p className="text-xs text-red-400/90 mt-0.5">
                {mutation.error instanceof Error
                  ? mutation.error.message
                  : 'Verifique se o link informado é válido e se o vídeo está público no YouTube.'}
              </p>
            </div>
          </div>
        )}

        {/* Card do Vídeo / Áudio Extraído */}
        {currentMedia && (
          <div className="w-full mb-12 animate-fade-in">
            <MediaCard media={currentMedia} />
          </div>
        )}

        {/* Features e Diferenciais */}
        <div className="w-full max-w-4xl grid grid-cols-1 sm:grid-cols-3 gap-6 mt-8 pt-8 border-t border-slate-800/80">
          <div className="flex items-start space-x-3 p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <div className="p-2 rounded-lg bg-brand-500/10 text-brand-400 shrink-0">
              <Monitor className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Alta Resolução</h3>
              <p className="text-xs text-slate-400 mt-1">
                Suporte para formatos 1080p Full HD, 720p HD e 360p com taxa de quadros otimizada.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Celular e Desktop</h3>
              <p className="text-xs text-slate-400 mt-1">
                Interface totalmente responsiva que se adapta perfeitamente ao seu navegador móvel ou de mesa.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Download Direto</h3>
              <p className="text-xs text-slate-400 mt-1">
                Entrega direta de arquivos no navegador sem anúncios invasivos ou redirecionamentos.
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        <p>vDownloader &copy; 2026 - Desenvolvido com FastAPI, React & Tailwind CSS.</p>
      </footer>
    </div>
  );
};
