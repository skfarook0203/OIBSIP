import React from 'react';
import { Key, Shield, Terminal, CheckSquare, Cpu } from 'lucide-react';
import { NavNodeId } from '../types';

interface SidebarProps {
  activeNode: NavNodeId;
  onSelectNode: (node: NavNodeId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeNode, onSelectNode }) => {
  const navItems = [
    {
      id: 'tkinter-gui' as NavNodeId,
      label: 'Tkinter Desktop GUI',
      icon: Key,
      badge: 'GUI',
      desc: 'Native Desktop App',
    },
    {
      id: 'internship-docs' as NavNodeId,
      label: 'Internship Docs & Audit',
      icon: CheckSquare,
      badge: 'TASK 3',
      desc: 'OASIS Checklist & Setup',
    },
    {
      id: 'cli-terminal' as NavNodeId,
      label: 'CLI Terminal Runner',
      icon: Shield,
      badge: 'CLI',
      desc: 'Headless Mode (--cli)',
    },
  ];

  return (
    <aside className="hidden lg:flex fixed left-0 top-16 bottom-0 w-64 bg-[#0a0e16] border-r border-[#262a33]/60 z-30 flex-col justify-between py-5 select-none">
      <div className="flex flex-col gap-4">
        <div className="px-5">
          <span className="font-['JetBrains_Mono'] text-[10px] font-semibold uppercase tracking-widest text-[#86948a]">
            Cryptographic Nodes
          </span>
        </div>

        <nav className="flex flex-col gap-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeNode === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onSelectNode(item.id)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-all text-left ${
                  isActive
                    ? 'bg-[#181c24] text-[#4edea3] font-semibold border border-[#10b981]/30 shadow-[inset_0_0_14px_rgba(78,222,163,0.12)]'
                    : 'text-[#bbcabf] hover:bg-[#181c24]/60 hover:text-white border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-[18px] h-[18px] ${isActive ? 'text-[#4edea3]' : 'text-[#86948a]'}`} />
                  <div className="flex flex-col">
                    <span className="text-sm font-medium leading-none">
                      {item.label}
                    </span>
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#86948a] mt-1">
                      {item.desc}
                    </span>
                  </div>
                </div>

                <span
                  className={`font-['JetBrains_Mono'] text-[9px] px-1.5 py-0.5 rounded border ${
                    isActive
                      ? 'bg-[#10b981]/20 text-[#4edea3] border-[#10b981]/40'
                      : 'bg-[#181c24] text-[#86948a] border-[#262a33]'
                  }`}
                >
                  {item.badge}
                </span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Telemetry Card */}
      <div className="px-4">
        <div className="bg-[#131a26] border border-[#262a33] rounded-xl p-3.5 flex flex-col gap-1.5 shadow-inner">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-[#4cd7f6]" />
              <span className="font-['JetBrains_Mono'] text-[10px] font-semibold text-[#86948a] uppercase">
                Entropy Core
              </span>
            </div>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10b981] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#4edea3]" />
            </span>
          </div>

          <div className="font-['JetBrains_Mono'] text-xs font-bold text-[#4cd7f6] tracking-wide">
            256-BIT TRNG
          </div>
          <div className="font-['JetBrains_Mono'] text-[10px] text-[#86948a]">
            Pool Latency: 0.2ms
          </div>
        </div>
      </div>
    </aside>
  );
};
