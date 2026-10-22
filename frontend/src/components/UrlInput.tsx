import React, { useState } from 'react';
import { Search, Clipboard, X, Loader2 } from 'lucide-react';

interface UrlInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

export const UrlInput: React.FC<UrlInputProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim());
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setUrl(text);
    } catch {
      // Falha silenciosa caso o navegador não autorize a leitura da área de transferência
    }
  };

  const handleClear = () => {
    setUrl('');
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="relative flex items-center shadow-2xl rounded-2xl bg-slate-900 border border-slate-800 p-2 focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/30 transition-all duration-300">
        <div className="pl-3 pr-2 text-slate-400">
          <Search className="w-5 h-5" />
        </div>

        <input
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="Cole aqui o link do vídeo do YouTube (ex: https://youtube.com/watch?v=...)"
          className="flex-1 bg-transparent border-none text-slate-100 placeholder-slate-500 text-sm sm:text-base focus:outline-none px-2 py-2 w-full"
          disabled={isLoading}
          required
        />

        {url && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="p-1.5 text-slate-400 hover:text-slate-200 transition-colors"
            title="Limpar link"
            aria-label="Limpar link"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        {!url && !isLoading && (
          <button
            type="button"
            onClick={handlePaste}
            className="hidden sm:flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 transition-all mr-2"
            title="Colar da área de transferência"
          >
            <Clipboard className="w-3.5 h-3.5" />
            <span>Colar</span>
          </button>
        )}

        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="ml-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-medium text-sm transition-all duration-200 shadow-md shadow-brand-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shrink-0"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Processando...</span>
            </>
          ) : (
            <span>Obter Mídia</span>
          )}
        </button>
      </div>
    </form>
  );
};
