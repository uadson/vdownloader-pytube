import React from 'react';
import { DownloadCloud, Sparkles } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <DownloadCloud className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                vDownloader
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-brand-500/20 text-brand-200 border border-brand-500/30">
                v0.2.2
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Extração & Download de Vídeos e Áudios</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            FastAPI + yt-dlp Engine
          </span>
        </div>
      </div>
    </header>
  );
};
