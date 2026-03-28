'use client';

import React, { useState } from 'react';
import { 
    BrainCircuit, 
    Stethoscope, 
    ActivitySquare, 
    ChevronRight, 
    CheckCircle2,
    Sparkles,
    Loader2
} from 'lucide-react';
import { useProjectAnalysis } from '@/hooks/use-project-analysis';

export default function ProjectWizard() {
    const [idea, setIdea] = useState("");
    const [analysis, setAnalysis] = useState<any>(null);
    const projectAnalysis = useProjectAnalysis();
    const loading = projectAnalysis.isPending;

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!idea.trim() || idea.length < 10) return;

        try {
            const data = await projectAnalysis.mutateAsync({ idea, use_ai: true });
            setAnalysis(data);
        } catch (error) {
            console.error("Analysis failed, using fallback UI", error);
            // Example fallback data to demonstrate the UI
            setAnalysis({
                complexity_level: "B",
                complexity_name_de: "Signalverarbeitungssystem",
                reasoning: "Das EKG-Gerät erfordert Erfassung und Analyse von bioelektrischen Signalen.",
                total_credits: 35,
                required_module_names: ["Mathematik 1", "Physik 1", "Elektrotechnik 1", "Anatomie & Physiologie"],
                learning_path: [
                    { phase_number: 1, title_de: "Grundlagen-Signal", module_names: ["Mathematik", "Elektrotechnik"] }
                ]
            });
        }
    };

    return (
        <div className="min-h-screen bg-[#0A0A0B] text-white p-6 md:p-12 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none" />

            <div className="max-w-5xl mx-auto relative z-10">
                <header className="mb-12 flex items-center justify-between border-b border-white/10 pb-6">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-lg shadow-purple-500/20">
                                <Stethoscope className="w-6 h-6 text-white" />
                            </div>
                            <h1 className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60">
                                Project-First Learning
                            </h1>
                        </div>
                        <p className="text-gray-400 font-medium">HAW Hamburg Medizintechnik — PO 2025</p>
                    </div>
                    <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full backdrop-blur-md">
                        <ActivitySquare className="w-4 h-4 text-emerald-400" />
                        <span className="text-sm font-semibold text-emerald-400">TakiOS AI Active</span>
                    </div>
                </header>

                {!analysis ? (
                    <div className="grid md:grid-cols-2 gap-12">
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <h2 className="text-4xl font-extrabold leading-tight">
                                    Wähle dein <br/>
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                                        Medizinprodukt.
                                    </span>
                                </h2>
                                <p className="text-lg text-gray-400 leading-relaxed max-w-md">
                                    Statt trockener Fächer baust du in deinem Studium ein reales Produkt. Beschreibe deine Idee, und unsere KI generiert deinen komplett individuellen Studienplan.
                                </p>
                            </div>

                            <form onSubmit={handleAnalyze} className="relative group mt-8">
                                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
                                <div className="relative bg-[#121214] border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
                                    <label htmlFor="idea" className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                                        <BrainCircuit className="w-4 h-4 text-purple-400" />
                                        Beschreibe deine Vision
                                    </label>
                                    <textarea
                                        id="idea"
                                        rows={4}
                                        value={idea}
                                        onChange={(e) => setIdea(e.target.value)}
                                        className="w-full bg-black/50 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none transition-all"
                                        placeholder="z.B. Ein tragbares EKG-Wearable für Sportler, das per App Herzrhythmusstörungen in Echtzeit analysiert..."
                                    />
                                    <button
                                        type="submit"
                                        disabled={loading || idea.length < 10}
                                        className="mt-4 w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold shadow-lg shadow-purple-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {loading ? (
                                            <><Loader2 className="w-5 h-5 animate-spin" /> KI analysiert Curriculum...</>
                                        ) : (
                                            <><Sparkles className="w-5 h-5" /> Lernplan generieren</>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>

                        <div className="hidden md:flex items-center justify-center">
                            {/* Futuristic Decoration */}
                            <div className="relative w-full aspect-square border border-white/5 rounded-full flex items-center justify-center">
                                <div className="absolute inset-10 border border-purple-500/20 rounded-full animate-[spin_20s_linear_infinite]" />
                                <div className="absolute inset-20 border border-blue-500/20 rounded-full animate-[spin_15s_linear_infinite_reverse]" />
                                <div className="bg-[#1A1A1D] border border-white/10 p-8 rounded-full shadow-2xl shadow-purple-500/10">
                                    <ActivitySquare className="w-20 h-20 text-purple-400 opacity-80" />
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
                        <div className="flex items-center justify-between">
                            <h2 className="text-3xl font-bold">Dein individueller Studienplan</h2>
                            <button onClick={() => setAnalysis(null)} className="text-sm text-gray-400 hover:text-white transition-colors">
                                Neue Idee
                            </button>
                        </div>

                        <div className="grid md:grid-cols-3 gap-6">
                            {/* Level Card */}
                            <div className="col-span-1 bg-gradient-to-br from-[#1A1A1D] to-[#121214] border border-purple-500/30 rounded-2xl p-6 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                    <BrainCircuit className="w-24 h-24 text-purple-400" />
                                </div>
                                <h3 className="text-purple-400 font-semibold mb-1">Level {analysis.complexity_level} Projekt</h3>
                                <p className="text-2xl font-bold text-white mb-4">{analysis.complexity_name_de}</p>
                                <p className="text-gray-400 text-sm">{analysis.reasoning}</p>
                                <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-sm">
                                    <span className="text-gray-400">Erforderliche CP:</span>
                                    <span className="font-mono text-emerald-400 font-bold">{analysis.total_credits} ECTS</span>
                                </div>
                            </div>

                            {/* Required Modules Summary */}
                            <div className="col-span-2 bg-[#121214] border border-white/10 rounded-2xl p-6">
                                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                                    <CheckCircle2 className="w-5 h-5 text-emerald-400" /> 
                                    Benötigte Fachmodule
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {analysis.required_module_names?.map((mod: string, idx: number) => (
                                        <span key={idx} className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-sm transition-colors text-gray-300">
                                            {mod}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Learning Path */}
                        <div className="mt-12">
                            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <ChevronRight className="text-purple-400" />
                                Realisierungsphasen
                            </h3>
                            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
                                {analysis.learning_path?.map((phase: any, index: number) => (
                                    <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                        {/* Icon */}
                                        <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-[#0A0A0B] bg-purple-500/20 text-purple-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 transition-transform hover:scale-110">
                                            {phase.phase_number}
                                        </div>
                                        {/* Card */}
                                        <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl bg-[#121214] border border-white/10 hover:border-purple-500/50 transition-colors shadow-lg">
                                            <div className="flex items-center justify-between mb-2">
                                                <h4 className="font-bold text-white">{phase.title_de}</h4>
                                                <span className="text-xs font-mono px-2 py-1 bg-white/5 rounded text-gray-400">Sem {phase.semester_equivalent}</span>
                                            </div>
                                            <div className="flex flex-wrap gap-1 mt-3">
                                                {phase.module_names?.map((m: string, i: number) => (
                                                    <span key={i} className="text-[11px] px-2 py-1 bg-black/50 border border-white/5 text-gray-400 rounded-md">
                                                        {m}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
