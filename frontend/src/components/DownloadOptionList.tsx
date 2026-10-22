import React, { useState } from 'react';
import { Download, Film, Music, CheckCircle2, Loader2 } from 'lucide-react';
import { DownloadOption } from '../types';
import { triggerDownload } from '../services/api';

interface DownloadOptionListProps {
  url: string;
  options: DownloadOption[];
}

export const DownloadOptionList: React.FC<DownloadOptionListProps> = ({ url, options }) => {
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'video' | 'audio'>('video');

  const videoOptions = options.filter((opt) => opt.media_type === 'video');
  const audioOptions = options.filter((opt) => opt.media_type === 'audio');

  const handleDownload = (option: DownloadOption) => {
    setDownloadingId(option.format_id);
    triggerDownload(url, option.media_type, option.resolution);

    // Retorna o status de downloading após alguns segundos
    setTimeout(() => {
      setDownloadingId(null);
    }, 4000);
  };

  const currentOptions = activeTab === 'video' ? videoOptions : audioOptions;

  return (
    <div className="space-y-4">
      {/* Abas para alternar entre Vídeos e Áudios */}
      <div className="flex border-b border-slate-800">
        <button
          type="button"
          onClick={() => setActiveTab('video')}
          className={`flex items-center space-x-2 py-3 px-4 font-medium text-sm border-b-2 transition-all ${
            activeTab === 'video'
              ? 'border-brand-500 text-brand-400 bg-brand-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Film className="w-4 h-4" />
          <span>Vídeo ({videoOptions.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('audio')}
          className={`flex items-center space-x-2 py-3 px-4 font-medium text-sm border-b-2 transition-all ${
            activeTab === 'audio'
              ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Music className="w-4 h-4" />
          <span>Áudio ({audioOptions.length})</span>
        </button>
      </div>

      {/* Lista de Opções de Download */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
        {currentOptions.map((opt) => {
          const isDownloading = downloadingId === opt.format_id;

          return (
            <div
              key={opt.format_id}
              className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 flex items-center justify-between transition-all group"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-sm text-slate-200">{opt.label}</span>
                  {opt.resolution && (
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-brand-300 border border-slate-700">
                      {opt.resolution}
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400">
                  Formato: <span className="uppercase font-semibold text-slate-300">.{opt.ext}</span>
                </p>
              </div>

              <button
                type="button"
                onClick={() => handleDownload(opt)}
                disabled={isDownloading}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-sm ${
                  opt.is_audio
                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                    : 'bg-brand-600 hover:bg-brand-500 text-white'
                } disabled:opacity-75`}
                title="Baixar para seu computador ou celular"
              >
                {isDownloading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Baixando...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-3.5 h-3.5" />
                    <span>Baixar</span>
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {downloadingId && (
        <div className="flex items-center space-x-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs animate-pulse">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Download iniciado! O arquivo será salvo diretamente na pasta de downloads do seu dispositivo.</span>
        </div>
      )}
    </div>
  );
};
