'use client';

import { useState } from 'react';
import { UrlInput } from '@/components/UrlInput';
import { TrustCard } from '@/components/TrustCard';
import { ingestWeb, processContext, ProcessResult } from '@/lib/api';
import { Sparkles, ShieldCheck, Zap, BrainCircuit } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (url: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const context = await ingestWeb(url);
      const processResult = await processContext(context);
      setResult({ ...processResult, product_context: context });
    } catch (err) {
      console.error(err);
      setError('Failed to analyze product. Please check the URL and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[rgb(var(--background))] text-white selection:bg-[rgb(var(--sage-accent))]/30 overflow-hidden">
      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[rgb(var(--sage-green))]/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[rgb(var(--sage-accent))]/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute top-[40%] left-[50%] -translate-x-1/2 w-[60%] h-[60%] bg-blue-500/5 rounded-full blur-[150px]" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 flex flex-col items-center min-h-screen">

        {/* Header / Nav */}
        <nav className="w-full flex justify-between items-center mb-16 animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[rgb(var(--sage-green))] to-[rgb(var(--sage-accent))] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-black" />
            </div>
            <span className="font-bold text-xl tracking-tight">Sage</span>
          </div>
          <div className="flex gap-4 text-sm text-gray-400">
            <span className="hover:text-white cursor-pointer transition-colors">About</span>
            <span className="hover:text-white cursor-pointer transition-colors">Principles</span>
          </div>
        </nav>

        {/* Hero Section */}
        <div className={cn("text-center space-y-8 max-w-4xl transition-all duration-700", result ? "mb-8 scale-90 opacity-80" : "mb-20")}>
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-[rgb(var(--sage-accent))] animate-in fade-in zoom-in duration-500">
            <Sparkles className="w-4 h-4" />
            <span>AI-Powered Product Truth Engine</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-white/50 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
            Uncover the Truth <br /> Behind Any Product
          </h1>

          <p className="text-xl text-gray-400 leading-relaxed max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
            Don't rely on biased reviews. Get an instant, evidence-backed analysis powered by advanced AI reasoning.
          </p>

          {/* Feature Pills */}
          {!result && (
            <div className="flex flex-wrap justify-center gap-4 pt-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
              <FeaturePill icon={<Zap className="w-4 h-4" />} text="Instant Analysis" />
              <FeaturePill icon={<ShieldCheck className="w-4 h-4" />} text="Scam Detection" />
              <FeaturePill icon={<BrainCircuit className="w-4 h-4" />} text="Deep Reasoning" />
            </div>
          )}
        </div>

        {/* Input Section */}
        <div className="w-full animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
          <UrlInput onAnalyze={handleAnalyze} isLoading={isLoading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 animate-in fade-in slide-in-from-top-2">
            {error}
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="w-full mt-12 animate-in fade-in slide-in-from-bottom-12 duration-1000">
            <TrustCard result={result} />
          </div>
        )}

        {/* Footer */}
        <footer className="mt-auto pt-24 pb-8 text-center text-sm text-gray-600">
          <p>© 2025 Sage Assistant. Built for Truth.</p>
        </footer>
      </div>
    </main>
  );
}

function FeaturePill({ icon, text }: { icon: React.ReactNode, text: string }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/5 text-gray-300 text-sm">
      {icon}
      <span>{text}</span>
    </div>
  );
}
