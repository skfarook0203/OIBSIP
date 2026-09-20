import React from 'react';
import { CheckCircle2, Shield, Terminal, FolderTree, BookOpen, ExternalLink, Download } from 'lucide-react';

export const InternshipDocs: React.FC = () => {
  const checklistItems = [
    { id: 1, title: 'Python Implementation', desc: 'Core application written in clean, modern Python 3 with functions and classes.' },
    { id: 2, title: 'Tkinter Desktop GUI', desc: 'Native Tkinter desktop window featuring ttk styling, custom cards, and dark theme.' },
    { id: 3, title: "secrets Module (CSPRNG)", desc: "Strictly uses Python's 'secrets' module instead of 'random' for cryptographic security." },
    { id: 4, title: 'string Module Used', desc: 'Utilizes string.ascii_uppercase, string.ascii_lowercase, string.digits, and symbols.' },
    { id: 5, title: 'pyperclip Clipboard Integration', desc: 'One-click clipboard copy button powered by pyperclip with Tkinter fallback.' },
    { id: 6, title: 'Password Length Input (Min 8)', desc: 'User-definable length with quick presets (12, 16, 24, 32) and validation for <8 characters.' },
    { id: 7, title: 'Character Type Checkboxes', desc: 'Individual toggles for Uppercase, Lowercase, Digits, and Special Symbols.' },
    { id: 8, title: 'At Least 2 Character Types Validation', desc: 'Strict validation requiring >= 2 active types before generation with GUI error alerts.' },
    { id: 9, title: 'Guaranteed Class Representation', desc: 'Guarantees that at least one character from every active pool appears in the password.' },
    { id: 10, title: 'Zero-Bias Array Shuffling', desc: 'Cryptographic Fisher-Yates shuffle utilizing secrets.randbelow to eliminate placement bias.' },
    { id: 11, title: 'Password Strength Indicator', desc: 'Calculates dynamic rating (Weak, Medium, Strong, Very Strong) with color-coded progress bar.' },
    { id: 12, title: 'Session-Only History (Last 5 Passwords)', desc: 'In-memory deque(maxlen=5) retaining recent passwords for copying, purged on window close.' },
    { id: 13, title: 'Ambiguous Character Exclusion', desc: 'Optional toggle to exclude confusing characters (0, O, l, I, 1, |) without breaking pools.' },
    { id: 14, title: 'Robust Error & Exception Handling', desc: 'Gracefully handles empty strings, non-numeric values, impossible lengths, and clipboard errors.' },
    { id: 15, title: 'Clean Python Project Structure', desc: 'Standard project with password_generator.py, requirements.txt, and README.md.' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-5 rounded-xl bg-[#1e293b] border border-[#334155] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#10b981]/20 border border-[#10b981]/40 flex items-center justify-center text-[#10b981]">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#0284c7]/20 text-[#38bdf8] font-mono">
                OASIS INFOBYTE
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#10b981]/20 text-[#34d399] font-mono">
                TASK 3 AUDIT
              </span>
            </div>
            <h1 className="text-lg font-bold text-white mt-0.5">
              Task 3: Random Password Generator — Internship Documentation
            </h1>
          </div>
        </div>

        <a
          href="/README.md"
          download="README.md"
          className="flex items-center gap-1.5 px-3 py-1.5 bg-[#334155] hover:bg-[#475569] text-white text-xs font-medium rounded-lg transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Download README.md</span>
        </a>
      </div>

      {/* Checklist Audit */}
      <div className="bg-[#0f172a] rounded-xl border border-[#334155] p-6 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-[#334155] pb-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[#10b981]" />
              <span>OASIS INFOBYTE Requirements Compliance Audit</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              All 15 specifications verified against the official internship task criteria.
            </p>
          </div>
          <span className="px-2.5 py-1 bg-[#10b981]/20 border border-[#10b981]/40 text-[#10b981] text-xs font-mono font-bold rounded-full">
            15 / 15 VERIFIED
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          {checklistItems.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-lg bg-[#1e293b]/70 border border-[#334155] flex items-start gap-3"
            >
              <div className="mt-0.5 w-4 h-4 rounded-full bg-[#10b981]/20 flex items-center justify-center shrink-0">
                <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              </div>
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-slate-200">
                  {item.id}. {item.title}
                </div>
                <div className="text-[11px] text-slate-400 leading-relaxed">
                  {item.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Project Structure Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#1e293b] border border-[#334155] rounded-xl p-5 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
            <FolderTree className="w-4 h-4 text-[#38bdf8]" />
            <span>Repository Directory Structure</span>
          </h3>
          <div className="bg-[#090d16] p-4 rounded-lg border border-[#334155] text-xs font-mono text-slate-300 leading-relaxed">
            <pre>{`CipherCraft-PasswordGenerator/
│
├── password_generator.py    # Main Tkinter Desktop & CLI Application
├── requirements.txt        # Dependencies (pyperclip)
├── test_generator.py       # Cryptographic Unit Tests
├── README.md               # Project Documentation & Guide
├── screenshots/            # UI Preview Captures
├── package.json            # Project manifest
└── src/                    # Interactive web preview interface`}</pre>
          </div>
        </div>

        <div className="bg-[#1e293b] border border-[#334155] rounded-xl p-5 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
            <Terminal className="w-4 h-4 text-[#10b981]" />
            <span>Execution Commands</span>
          </h3>
          <div className="space-y-3 text-xs">
            <div className="bg-[#090d16] p-3 rounded-lg border border-[#334155] font-mono text-slate-300">
              <span className="text-slate-500"># 1. Install dependencies</span>
              <div className="text-[#38bdf8] font-bold">python -m pip install -r requirements.txt</div>
            </div>

            <div className="bg-[#090d16] p-3 rounded-lg border border-[#334155] font-mono text-slate-300">
              <span className="text-slate-500"># 2. Run Desktop GUI (Windows / macOS / Linux)</span>
              <div className="text-[#10b981] font-bold">python password_generator.py</div>
            </div>

            <div className="bg-[#090d16] p-3 rounded-lg border border-[#334155] font-mono text-slate-300">
              <span className="text-slate-500"># 3. Run Cryptographic Unit Tests</span>
              <div className="text-amber-400 font-bold">python -m unittest test_generator.py</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
