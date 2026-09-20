import React from 'react';
import { Shield, Lock, Radio } from 'lucide-react';
import { NavNodeId } from '../types';

interface HeaderProps {
  activeNode: NavNodeId;
  onSelectNode: (node: NavNodeId) => void;
  airgapMode: boolean;
  onToggleAirgap: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeNode,
  onSelectNode,
  airgapMode,
  onToggleAirgap,
}) => {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-[#0a0e16]/90 backdrop-blur-xl border-b border-[#262a33]/60 z-40 flex items-center justify-between px-4 sm:px-6">
      <div className="flex items-center gap-3 sm:gap-6">
        {/* Shield Logo & Brand */}
        <div 
          onClick={() => onSelectNode('tkinter-gui')}
          className="flex items-center gap-2.5 cursor-pointer select-none group"
        >
          <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-[#181c24] border border-[#10b981]/40 shadow-[0_0_12px_rgba(78,222,163,0.25)] group-hover:border-[#4edea3] transition-all">
            <Shield className="w-5 h-5 text-[#4edea3]" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-[#4cd7f6] shadow-[0_0_4px_#4cd7f6]" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-['Space_Grotesk'] text-base font-bold tracking-tight text-[#dfe2ee] group-hover:text-white transition-colors">
              OASIS INFOBYTE
            </span>
            <span className="font-['JetBrains_Mono'] text-[10px] uppercase tracking-wider text-[#86948a]">
              Task 3: Password Gen
            </span>
          </div>
        </div>

        <div className="h-5 w-[1px] bg-[#262a33] hidden md:block" />

        {/* Active Engine Badges */}
        <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 bg-[#181c24] border border-[#262a33] rounded-full">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10b981] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#4edea3]" />
          </span>
          <span className="font-['JetBrains_Mono'] text-[10px] font-semibold text-[#4edea3] tracking-wide">
            PYTHON 3 SECRETS ACTIVE
          </span>
        </div>

        <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 bg-[#181c24]/80 border border-[#262a33] rounded-full">
          <Lock className="w-3.5 h-3.5 text-[#4cd7f6]" />
          <span className="font-['JetBrains_Mono'] text-[10px] font-medium text-[#4cd7f6] tracking-wide">
            TKINTER DESKTOP GUI READY
          </span>
        </div>
      </div>

      {/* Right Action Controls */}
      <div className="flex items-center gap-3">
        {/* Quick Node Switcher on Mobile/Tablet */}
        <div className="flex lg:hidden items-center bg-[#181c24] p-1 rounded-lg border border-[#262a33]">
          <button
            type="button"
            onClick={() => onSelectNode('tkinter-gui')}
            className={`px-2 py-1 rounded text-xs font-mono font-medium transition-colors ${
              activeNode === 'tkinter-gui'
                ? 'bg-[#10b981] text-[#003824] font-bold'
                : 'text-[#bbcabf] hover:text-white'
            }`}
          >
            GUI
          </button>
          <button
            type="button"
            onClick={() => onSelectNode('internship-docs')}
            className={`px-2 py-1 rounded text-xs font-mono font-medium transition-colors ${
              activeNode === 'internship-docs'
                ? 'bg-[#10b981] text-[#003824] font-bold'
                : 'text-[#bbcabf] hover:text-white'
            }`}
          >
            AUDIT
          </button>
          <button
            type="button"
            onClick={() => onSelectNode('cli-terminal')}
            className={`px-2 py-1 rounded text-xs font-mono font-medium transition-colors ${
              activeNode === 'cli-terminal'
                ? 'bg-[#10b981] text-[#003824] font-bold'
                : 'text-[#bbcabf] hover:text-white'
            }`}
          >
            CLI
          </button>
        </div>

        {/* Secure / Air-gap State Switcher */}
        <div className="flex items-center bg-[#181c24] rounded-lg p-1 border border-[#262a33]">
          <button
            type="button"
            onClick={() => onToggleAirgap()}
            className={`px-2.5 py-1 rounded font-['JetBrains_Mono'] text-[11px] font-semibold transition-all ${
              !airgapMode
                ? 'bg-[#10b981] text-[#003824] shadow-[0_0_10px_rgba(78,222,163,0.3)]'
                : 'text-[#86948a] hover:text-[#dfe2ee]'
            }`}
          >
            SECURE
          </button>
          <button
            type="button"
            onClick={() => onToggleAirgap()}
            className={`px-2.5 py-1 rounded font-['JetBrains_Mono'] text-[11px] font-semibold transition-all flex items-center gap-1 ${
              airgapMode
                ? 'bg-[#4cd7f6] text-[#003640] shadow-[0_0_10px_rgba(76,215,246,0.3)]'
                : 'text-[#86948a] hover:text-[#dfe2ee]'
            }`}
          >
            {airgapMode && <Radio className="w-3 h-3 animate-pulse" />}
            AIRGAP
          </button>
        </div>

        {/* User / Session Avatar */}
        <div 
          title="Cryptographic Auditor Session"
          className="w-8 h-8 rounded-full bg-gradient-to-br from-[#10b981] to-[#06b6d4] flex items-center justify-center text-[#003824] font-bold text-xs shadow-[0_0_10px_rgba(78,222,163,0.35)] cursor-pointer"
        >
          CP
        </div>
      </div>
    </header>
  );
};
