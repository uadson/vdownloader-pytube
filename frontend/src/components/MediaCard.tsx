import React, { useState } from 'react';
import { User, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { VideoInfo } from '../types';
import { DownloadOptionList } from './DownloadOptionList';

interface MediaCardProps {
  media: VideoInfo;
}

export const MediaCard: React.FC<MediaCardProps> = ({ media }) => {
  const [isDescExpanded, setIsDescExpanded] = useState(false);

  return (
    <div className="w-full max-w-4xl mx-auto rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-300">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6">
        {/* Preview / Thumbnail */}
        <div className="md:col-span-5 flex flex-col items-center">
          <div className="relative w-full aspect-video rounded-xl overflow-hidden border border-slate-800 bg-slate-950 group shadow-lg">
            <img
              src={media.thumbnail}
              alt={media.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              loading="lazy"
            />
            <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-black/80 backdrop-blur-md text-white text-xs font-mono font-medium flex items-center space-x-1">
              <Clock className="w-3 h-3 text-slate-300" />
              <span>{media.duration_formatted}</span>
            </div>
          </div>

          <div className="w-full mt-3 flex items-center justify-between text-xs text-slate-400 px-1">
            <span className="flex items-center space-x-1.5 truncate">
              <User className="w-3.5 h-3.5 text-brand-400 shrink-0" />
              <span className="font-medium text-slate-300 truncate">{media.author}</span>
            </span>
          </div>
        </div>

        {/* Informações e Seletor de Download */}
        <div className="md:col-span-7 flex flex-col justify-between space-y-4">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight leading-snug line-clamp-2">
              {media.title}
            </h2>

            {/* Descrição expansível */}
            {media.description && (
              <div className="mt-2 text-xs text-slate-400 bg-slate-950/40 p-3 rounded-lg border border-slate-800/80">
                <p className={isDescExpanded ? 'whitespace-pre-line' : 'line-clamp-2'}>
                  {media.description}
                </p>
                {media.description.length > 120 && (
                  <button
                    type="button"
                    onClick={() => setIsDescExpanded(!isDescExpanded)}
                    className="mt-1 text-brand-400 hover:text-brand-300 font-medium flex items-center space-x-1 transition-colors"
                  >
                    <span>{isDescExpanded ? 'Ver menos' : 'Ver mais'}</span>
                    {isDescExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                )}
              </div>
            )}
          </div>

          <div className="pt-2">
            <h3 className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-2">
              Escolha a qualidade para download:
            </h3>
            <DownloadOptionList url={media.url} options={media.options} />
          </div>
        </div>
      </div>
    </div>
  );
};
