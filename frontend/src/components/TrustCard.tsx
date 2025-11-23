'use client';

import React, { useState } from 'react';
import { ProcessResult } from '@/lib/api';
import { ShieldCheck, ShieldAlert, ShieldX, CheckCircle2, XCircle, AlertTriangle, MessageSquare, ChevronDown, ChevronUp, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';

interface TrustCardProps {
    result: ProcessResult;
}

interface ChatMessage {
    id: number;
    text: string;
    sender: 'user' | 'bot';
}

export function TrustCard({ result }: TrustCardProps) {
    const { tcs_score, tcs_band, tcs_components, trust_summary } = result;
    const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showReasoning, setShowReasoning] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: ChatMessage = { id: Date.now(), text: input, sender: 'user' };
        setChatHistory(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const res = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    product_context: result.product_context,
                    message: userMsg.text
                })
            });

            if (!res.ok) throw new Error("Failed to get response");
            const data = await res.json();

            const botMsg: ChatMessage = { id: Date.now() + 1, text: data.response, sender: 'bot' };
            setChatHistory(prev => [...prev, botMsg]);
        } catch (err) {
            console.error(err);
            const errorMsg: ChatMessage = { id: Date.now() + 1, text: "Sorry, I encountered an error.", sender: 'bot' };
            setChatHistory(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 0.8) return 'text-[rgb(var(--trust-blue))]';
        if (score >= 0.5) return 'text-[rgb(var(--caution-amber))]';
        return 'text-[rgb(var(--danger-red))]';
    };

    const getBandColor = (band: string) => {
        switch (band.toLowerCase()) {
            case 'trusted': return 'bg-[rgb(var(--trust-blue))]/20 text-[rgb(var(--trust-blue))] border-[rgb(var(--trust-blue))]/30';
            case 'pilot': return 'bg-[rgb(var(--caution-amber))]/20 text-[rgb(var(--caution-amber))] border-[rgb(var(--caution-amber))]/30';
            case 'caution': return 'bg-[rgb(var(--danger-red))]/20 text-[rgb(var(--danger-red))] border-[rgb(var(--danger-red))]/30';
            default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
        }
    };

    return (
        <div className="w-full max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header Card */}
            <Card className="relative overflow-hidden p-8 md:p-10">
                <div className="absolute top-0 right-0 p-4 opacity-[0.03] pointer-events-none">
                    <ShieldCheck className="w-96 h-96" />
                </div>

                <div className="relative z-10 flex flex-col md:flex-row gap-10 items-center md:items-start">
                    {/* Score Circle */}
                    <div className="relative group shrink-0">
                        <div className={cn("w-48 h-48 rounded-full border-8 flex items-center justify-center bg-black/40 backdrop-blur-sm transition-all duration-500",
                            tcs_score >= 0.8 ? "border-[rgb(var(--trust-blue))]" : tcs_score >= 0.5 ? "border-[rgb(var(--caution-amber))]" : "border-[rgb(var(--danger-red))]"
                        )}>
                            <div className="text-center">
                                <div className={cn("text-6xl font-bold tracking-tighter", getScoreColor(tcs_score))}>
                                    {Math.round(tcs_score * 100)}
                                </div>
                                <div className="text-xs text-gray-400 uppercase tracking-widest mt-2 font-medium">Trust Score</div>
                            </div>
                        </div>
                        <div className={cn("absolute -bottom-5 left-1/2 -translate-x-1/2 px-6 py-2 rounded-full text-sm font-bold border uppercase tracking-wide shadow-lg whitespace-nowrap", getBandColor(tcs_band))}>
                            {tcs_band}
                        </div>
                    </div>

                    {/* Verdict */}
                    <div className="flex-1 text-center md:text-left space-y-6">
                        <div>
                            <h2 className="text-3xl font-bold text-white mb-3">Sage Verdict</h2>
                            <p className="text-lg text-gray-300 leading-relaxed font-light">
                                {trust_summary.overall_verdict}
                            </p>
                        </div>

                        {/* Progressive Disclosure: Reasoning */}
                        <div className="bg-white/5 rounded-xl border border-white/5 overflow-hidden">
                            <button
                                onClick={() => setShowReasoning(!showReasoning)}
                                className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors text-sm font-medium text-gray-400"
                            >
                                <span className="flex items-center gap-2">
                                    <Info className="w-4 h-4" />
                                    Why this score?
                                </span>
                                {showReasoning ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>
                            {showReasoning && (
                                <div className="p-4 pt-0 text-sm text-gray-400 border-t border-white/5 animate-in slide-in-from-top-2">
                                    <p>
                                        This score is calculated based on {tcs_components.groundedness * 100}% groundedness in available data,
                                        {tcs_components.accuracy * 100}% accuracy of claims, and {tcs_components.coverage * 100}% coverage of key features.
                                        We detected {tcs_components.conflict_detection * 100}% conflict rate in user reviews.
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <Metric label="Groundedness" value={tcs_components.groundedness} />
                            <Metric label="Accuracy" value={tcs_components.accuracy} />
                            <Metric label="Coverage" value={tcs_components.coverage} />
                            <Metric label="Conflict Det." value={tcs_components.conflict_detection} />
                        </div>
                    </div>
                </div>
            </Card>

            {/* Aspects Grid */}
            <div className="grid md:grid-cols-2 gap-6">
                {trust_summary.aspects.map((aspect) => (
                    <Card key={aspect.name} className="hover:bg-white/10 transition-colors duration-300">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-semibold text-white capitalize">{aspect.name}</h3>
                            <div className={cn("px-4 py-1.5 rounded-full text-sm font-bold border",
                                aspect.score_0_10 >= 8 ? "bg-green-500/10 text-green-400 border-green-500/20" : aspect.score_0_10 >= 5 ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"
                            )}>
                                {aspect.score_0_10}/10
                            </div>
                        </div>

                        <div className="space-y-4">
                            {aspect.pros.length > 0 && (
                                <div>
                                    <div className="text-xs text-green-400 uppercase font-bold mb-2 flex items-center gap-2">
                                        <CheckCircle2 className="w-4 h-4" /> Pros
                                    </div>
                                    <ul className="text-sm text-gray-300 space-y-2">
                                        {aspect.pros.map((pro, i) => <li key={i} className="flex items-start gap-2"><span className="text-green-500/50 mt-1">•</span> {pro}</li>)}
                                    </ul>
                                </div>
                            )}

                            {aspect.cons.length > 0 && (
                                <div>
                                    <div className="text-xs text-red-400 uppercase font-bold mb-2 flex items-center gap-2 mt-4">
                                        <XCircle className="w-4 h-4" /> Cons
                                    </div>
                                    <ul className="text-sm text-gray-300 space-y-2">
                                        {aspect.cons.map((con, i) => <li key={i} className="flex items-start gap-2"><span className="text-red-500/50 mt-1">•</span> {con}</li>)}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </Card>
                ))}
            </div>

            {/* Claims & Uncertainties */}
            <div className="grid md:grid-cols-2 gap-6">
                <Card>
                    <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                        <ShieldCheck className="w-5 h-5 text-[rgb(var(--sage-green))]" /> Verified Claims
                    </h3>
                    <ul className="space-y-3">
                        {trust_summary.claims.map((claim, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-3 p-3 rounded-lg bg-white/5">
                                <CheckCircle2 className="w-4 h-4 text-[rgb(var(--sage-green))] mt-0.5 shrink-0" />
                                {claim}
                            </li>
                        ))}
                    </ul>
                </Card>

                {trust_summary.uncertainties.length > 0 && (
                    <Card className="border-[rgb(var(--caution-amber))]/20 bg-[rgb(var(--caution-amber))]/5">
                        <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-[rgb(var(--caution-amber))]" /> Uncertainties
                        </h3>
                        <ul className="space-y-3">
                            {trust_summary.uncertainties.map((u, i) => (
                                <li key={i} className="text-sm text-gray-300 flex items-start gap-3 p-3 rounded-lg bg-[rgb(var(--caution-amber))]/10 border border-[rgb(var(--caution-amber))]/10">
                                    <AlertTriangle className="w-4 h-4 text-[rgb(var(--caution-amber))] mt-0.5 shrink-0" />
                                    {u}
                                </li>
                            ))}
                        </ul>
                    </Card>
                )}
            </div>

            {/* Chat Section */}
            <Card className="mt-8">
                <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-[rgb(var(--sage-accent))]" /> Ask Sage
                </h3>

                <div className="bg-black/40 rounded-xl p-6 h-80 overflow-y-auto mb-6 space-y-4 flex flex-col scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                    {chatHistory.length === 0 && (
                        <div className="text-center text-gray-500 my-auto">
                            <p>Have questions about the analysis?</p>
                            <p className="text-sm">Ask Sage to dig deeper.</p>
                        </div>
                    )}
                    {chatHistory.map((msg) => (
                        <div key={msg.id} className={cn("max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed",
                            msg.sender === 'user'
                                ? "bg-[rgb(var(--sage-accent))]/20 text-white self-end rounded-br-none border border-[rgb(var(--sage-accent))]/20"
                                : "bg-white/10 text-gray-300 self-start rounded-bl-none border border-white/5"
                        )}>
                            {msg.text}
                        </div>
                    ))}
                    {isLoading && (
                        <div className="bg-white/10 text-gray-300 self-start p-4 rounded-2xl rounded-bl-none text-sm animate-pulse flex items-center gap-2">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                        </div>
                    )}
                </div>

                <div className="flex gap-3">
                    <Input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask a follow-up question..."
                        className="flex-1 bg-black/20 border-white/10"
                    />
                    <Button
                        onClick={handleSend}
                        disabled={isLoading || !input.trim()}
                        className="px-6"
                    >
                        Send
                    </Button>
                </div>
            </Card>
        </div>
    );
}

function Metric({ label, value }: { label: string, value: number }) {
    return (
        <div className="bg-black/20 rounded-xl p-4 text-center border border-white/5">
            <div className="text-2xl font-bold text-white mb-1">{Math.round(value * 100)}%</div>
            <div className="text-[10px] text-gray-400 uppercase tracking-wider">{label}</div>
        </div>
    );
}
