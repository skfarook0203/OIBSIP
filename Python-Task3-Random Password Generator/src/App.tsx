/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { NavNodeId } from './types';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { TkinterSimulator } from './components/TkinterSimulator';
import { InternshipDocs } from './components/InternshipDocs';
import { CliTerminal } from './components/CliTerminal';

export default function App() {
  const [activeNode, setActiveNode] = useState<NavNodeId>('tkinter-gui');
  const [airgapMode, setAirgapMode] = useState<boolean>(false);

  const toggleAirgap = () => {
    setAirgapMode((prev) => !prev);
  };

  return (
    <div className="min-h-screen bg-[#0f131c] text-[#dfe2ee] font-sans antialiased selection:bg-[#10b981]/30 selection:text-[#6ffbbe]">
      {/* Top Application Header */}
      <Header
        activeNode={activeNode}
        onSelectNode={setActiveNode}
        airgapMode={airgapMode}
        onToggleAirgap={toggleAirgap}
      />

      {/* Left Sidebar (Desktop) */}
      <Sidebar activeNode={activeNode} onSelectNode={setActiveNode} />

      {/* Main Viewport Container */}
      <div className="lg:pl-64 transition-all duration-300">
        <main className="pt-20 px-4 sm:px-8 py-6 min-h-screen">
          {activeNode === 'tkinter-gui' && (
            <TkinterSimulator
              onOpenCli={() => setActiveNode('cli-terminal')}
            />
          )}

          {activeNode === 'internship-docs' && <InternshipDocs />}

          {activeNode === 'cli-terminal' && <CliTerminal />}
        </main>
      </div>
    </div>
  );
}
