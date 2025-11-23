import React, { useState } from 'react';
import { Search, ArrowRight } from 'lucide-react';
import { Input } from './ui/Input';
import { Button } from './ui/Button';

interface UrlInputProps {
    onAnalyze: (url: string) => void;
    isLoading: boolean;
}

export function UrlInput({ onAnalyze, isLoading }: UrlInputProps) {
    const [url, setUrl] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (url.trim()) {
            onAnalyze(url);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto relative z-20">
            <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1 group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-[rgb(var(--sage-green))] to-[rgb(var(--sage-accent))] rounded-lg blur opacity-30 group-hover:opacity-75 transition duration-1000 group-hover:duration-200" />
                    <Input
                        type="url"
                        placeholder="Paste product URL (Amazon, Shopify, etc.)"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="relative bg-[#0A0A0C] border-white/10 h-12 text-lg"
                        icon={<Search className="w-5 h-5" />}
                        disabled={isLoading}
                    />
                </div>
                <Button
                    type="submit"
                    disabled={isLoading || !url.trim()}
                    className="h-12 px-8 font-semibold text-lg shadow-[0_0_20px_rgba(79,209,197,0.3)] hover:shadow-[0_0_30px_rgba(79,209,197,0.5)] transition-shadow"
                >
                    {isLoading ? 'Analyzing...' : 'Analyze'}
                    {!isLoading && <ArrowRight className="ml-2 w-5 h-5" />}
                </Button>
            </div>
        </form>
    );
}
