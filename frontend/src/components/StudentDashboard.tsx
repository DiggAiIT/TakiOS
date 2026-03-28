'use client';

import React from 'react';
import { 
    ActivitySquare, 
    BookOpen, 
    CheckCircle2, 
    Clock, 
    Trophy,
    Target,
    Zap,
    Flag,
    ShieldCheck
} from 'lucide-react';

export default function StudentDashboard() {
    // Mock data for the student's active project (e.g. they finished the Wizard)
    const activeProject = {
        title: "EKG-Wearable für Sportler",
        level: "B",
        progress: 35,
        currentPhase: 2,
        totalModules: 8,
        completedModules: 3,
        nextMilestone: "Hardware-Prototyp Gehäuse",
    };

    const radarStats = [
        { label: "Mathematik/Physik", value: 40 },
        { label: "Medizin/Anatomie", value: 70 },
        { label: "Elektrotechnik", value: 85 },
        { label: "Software/IT", value: 60 },
        { label: "Regulatorik", value: 20 },
    ];

    return (
        <div className="text-white space-y-8 animate-in fade-in duration-700">
            {/* Header section */}
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
                        Projekt-Zentrale
                    </h1>
                    <p className="text-gray-400 mt-1">Hier steuerst du die Realisierung deines Medizinprodukts.</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-5 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm font-semibold transition-colors flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        Compliance Check
                    </button>
                    <button className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-xl text-sm font-semibold shadow-lg shadow-purple-500/20 transition-all">
                        Weiterarbeiten
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* 1. Progress-Karte (Main Project View) */}
                <div className="lg:col-span-2 bg-[#121214] border border-white/10 rounded-3xl p-8 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                        <ActivitySquare className="w-48 h-48 text-purple-400" />
                    </div>
                    
                    <div className="relative z-10">
                        <div className="flex items-center gap-3 mb-6">
                            <span className="px-3 py-1 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-lg text-xs font-bold font-mono tracking-wider">
                                LEVEL {activeProject.level}
                            </span>
                            <span className="text-sm font-medium text-gray-400 flex items-center gap-1.5">
                                <Target className="w-4 h-4" /> Fokus: Signalverarbeitung
                            </span>
                        </div>
                        
                        <h2 className="text-4xl font-black mb-2">{activeProject.title}</h2>
                        
                        <div className="mt-10">
                            <div className="flex justify-between items-end mb-3">
                                <span className="text-gray-400 font-medium">Realisierungsfortschritt</span>
                                <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
                                    {activeProject.progress}%
                                </span>
                            </div>
                            <div className="w-full h-3 bg-black/50 rounded-full overflow-hidden border border-white/5">
                                <div 
                                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full relative"
                                    style={{ width: `${activeProject.progress}%` }}
                                >
                                    <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite]" />
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8">
                            <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                                <BookOpen className="w-5 h-5 text-blue-400 mb-2" />
                                <div className="text-2xl font-bold">{activeProject.completedModules}/{activeProject.totalModules}</div>
                                <div className="text-xs text-gray-400 mt-1">Fachmodule</div>
                            </div>
                            <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                                <Flag className="w-5 h-5 text-emerald-400 mb-2" />
                                <div className="text-2xl font-bold">Phase {activeProject.currentPhase}</div>
                                <div className="text-xs text-gray-400 mt-1">Von 4 Meilensteinen</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Wissens-Radar (Spider Chart Mockup using pure CSS shapes for aesthetics) */}
                <div className="bg-[#121214] border border-white/10 rounded-3xl p-8 flex flex-col justify-between">
                    <div>
                        <h3 className="text-lg font-bold flex items-center gap-2 mb-1">
                            <Zap className="w-5 h-5 text-yellow-400" />
                            Kompetenz-Radar
                        </h3>
                        <p className="text-sm text-gray-400">Dein Skillset im Kontext dieses Projekts.</p>
                    </div>
                    
                    <div className="flex-1 flex items-center justify-center my-8 relative">
                        {/* Custom SVG Radar Chart */}
                        <svg viewBox="0 0 100 100" className="w-full max-w-[200px] overflow-visible drop-shadow-[0_0_15px_rgba(168,85,247,0.4)]">
                            {/* Spider Web Background */}
                            {[20, 40, 60, 80, 100].map((r) => (
                                <polygon 
                                    key={r}
                                    points={`50,${50-r} ${50+r*0.95},${50-r*0.31} ${50+r*0.59},${50+r*0.81} ${50-r*0.59},${50+r*0.81} ${50-r*0.95},${50-r*0.31}`}
                                    fill="none" 
                                    stroke="rgba(255,255,255,0.1)" 
                                    strokeWidth="0.5"
                                />
                            ))}
                            {/* The Radar Shape */}
                            <polygon 
                                points={`50,${50-40} ${50+70*0.95},${50-70*0.31} ${50+85*0.59},${50+85*0.81} ${50-60*0.59},${50+60*0.81} ${50-20*0.95},${50-20*0.31}`}
                                fill="rgba(168, 85, 247, 0.3)" 
                                stroke="rgba(168, 85, 247, 1)" 
                                strokeWidth="2"
                                className="transition-all duration-1000"
                            />
                        </svg>
                    </div>

                    <div className="space-y-3">
                        {radarStats.map((stat, i) => (
                            <div key={i} className="flex items-center justify-between text-xs font-medium">
                                <span className="text-gray-300">{stat.label}</span>
                                <span className={stat.value > 50 ? 'text-purple-400' : 'text-gray-500'}>{stat.value}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* 3. Realisierungs-Timeline & Aktuelle Aufgaben */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-[#121214] border border-white/10 rounded-3xl p-8">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-blue-400" />
                        Nächste Schritte
                    </h3>
                    <div className="space-y-4">
                        <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20 flex gap-4 items-start cursor-pointer hover:bg-purple-500/20 transition-colors">
                            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center shrink-0">
                                <Trophy className="w-4 h-4 text-purple-400" />
                            </div>
                            <div>
                                <h4 className="font-semibold text-purple-300">Kontext-Test absolvieren</h4>
                                <p className="text-sm text-gray-400 mt-1">Modul 'Signale & Systeme' ist bereit für dein EKG-Wearable.</p>
                            </div>
                        </div>
                        <div className="p-4 rounded-xl bg-white/5 border border-white/5 flex gap-4 items-start cursor-pointer hover:bg-white/10 transition-colors">
                            <div className="w-8 h-8 rounded-full bg-black/50 border border-white/10 flex items-center justify-center shrink-0">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            </div>
                            <div>
                                <h4 className="font-semibold text-gray-300">Eselsbrücke überprüfen</h4>
                                <p className="text-sm text-gray-400 mt-1">KI hat eine neue Metapher für deine Schaltung erstellt.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-[#121214] border border-white/10 rounded-3xl p-8 bg-[url('/grid-pattern.svg')] bg-center bg-cover border-b-4 border-b-blue-600">
                    <div className="h-full flex flex-col justify-between">
                        <div>
                            <span className="px-3 py-1 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-xs font-bold uppercase tracking-wider mb-4 inline-block">
                                Quality & Regulatory
                            </span>
                            <h3 className="text-2xl font-bold mt-2">ISO 13485 QMS-Check</h3>
                            <p className="text-gray-400 mt-2">Bereit für die nächste Audit-Simulation für dein Wearable.</p>
                        </div>
                        <button className="mt-8 w-full py-3 bg-white text-black font-bold rounded-xl hover:bg-gray-200 transition-colors">
                            Templates laden
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
