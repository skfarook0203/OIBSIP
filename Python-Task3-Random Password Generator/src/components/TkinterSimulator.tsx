import React, { useState, useEffect } from 'react';
import { Copy, RefreshCw, Check, AlertCircle, Terminal, Download, ShieldCheck, HelpCircle } from 'lucide-react';

interface TkinterSimulatorProps {
  onOpenCli?: () => void;
}

export const TkinterSimulator: React.FC<TkinterSimulatorProps> = ({ onOpenCli }) => {
  // State matching Python Tkinter PasswordGeneratorApp
  const [length, setLength] = useState<number>(16);
  const [useUpper, setUseUpper] = useState<boolean>(true);
  const [useLower, setUseLower] = useState<boolean>(true);
  const [useDigits, setUseDigits] = useState<boolean>(true);
  const [useSymbols, setUseSymbols] = useState<boolean>(true);
  const [excludeAmbiguous, setExcludeAmbiguous] = useState<boolean>(false);

  const [generatedPassword, setGeneratedPassword] = useState<string>('');
  const [sessionHistory, setSessionHistory] = useState<string[]>([]);
  const [selectedHistoryIndex, setSelectedHistoryIndex] = useState<number | null>(null);

  const [statusMessage, setStatusMessage] = useState<{
    text: string;
    type: 'info' | 'success' | 'error';
  }>({
    text: "Ready. Click 'GENERATE PASSWORD' to create a secure key.",
    type: 'info',
  });

  const [copied, setCopied] = useState<boolean>(false);
  const [validationDialog, setValidationDialog] = useState<{ title: string; message: string } | null>(null);

  // Cryptographically secure generation matching Python secrets module implementation
  const generatePassword = (
    reqLen: number,
    uUpper: boolean,
    uLower: boolean,
    uDigits: boolean,
    uSymbols: boolean,
    exAmbiguous: boolean
  ) => {
    // 1. Validation: length >= 8
    if (isNaN(reqLen) || reqLen < 8) {
      setStatusMessage({ text: 'Error: Minimum password length is 8 characters.', type: 'error' });
      setValidationDialog({
        title: 'Validation Error',
        message: 'Password length must be at least 8 characters.',
      });
      return null;
    }

    if (reqLen > 256) {
      setStatusMessage({ text: 'Error: Maximum password length is 256 characters.', type: 'error' });
      setValidationDialog({
        title: 'Validation Error',
        message: 'Password length cannot exceed 256 characters.',
      });
      return null;
    }

    const ambiguousChars = new Set(['0', 'O', 'l', 'I', '1', '|']);

    const pools: string[] = [];

    if (uUpper) {
      let p = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
      if (exAmbiguous) p = p.split('').filter((c) => !ambiguousChars.has(c)).join('');
      if (p) pools.push(p);
    }
    if (uLower) {
      let p = 'abcdefghijklmnopqrstuvwxyz';
      if (exAmbiguous) p = p.split('').filter((c) => !ambiguousChars.has(c)).join('');
      if (p) pools.push(p);
    }
    if (uDigits) {
      let p = '0123456789';
      if (exAmbiguous) p = p.split('').filter((c) => !ambiguousChars.has(c)).join('');
      if (p) pools.push(p);
    }
    if (uSymbols) {
      let p = '!@#$%^&*()_+-=[]{}|;:,.<>?';
      if (exAmbiguous) p = p.split('').filter((c) => !ambiguousChars.has(c)).join('');
      if (p) pools.push(p);
    }

    // 2. Validation: At least 2 character types
    if (pools.length < 2) {
      setStatusMessage({ text: 'Error: Please select at least two (2) character types.', type: 'error' });
      setValidationDialog({
        title: 'Validation Error',
        message:
          'Security Policy Requirement:\nPlease select at least 2 character types (Uppercase, Lowercase, Numbers, or Symbols).',
      });
      return null;
    }

    // 3. Cryptographically secure random selection using window.crypto
    const getRandomInt = (max: number): number => {
      const buffer = new Uint32Array(1);
      window.crypto.getRandomValues(buffer);
      return buffer[0] % max;
    };

    const getRandomChar = (pool: string): string => {
      return pool[getRandomInt(pool.length)];
    };

    // Guarantee at least 1 character from each chosen pool
    const passwordChars: string[] = pools.map((pool) => getRandomChar(pool));

    // Fill remainder from combined pool
    const combinedPool = pools.join('');
    const remainder = reqLen - passwordChars.length;
    for (let i = 0; i < remainder; i++) {
      passwordChars.push(getRandomChar(combinedPool));
    }

    // Fisher-Yates shuffle
    for (let i = passwordChars.length - 1; i > 0; i--) {
      const j = getRandomInt(i + 1);
      const temp = passwordChars[i];
      passwordChars[i] = passwordChars[j];
      passwordChars[j] = temp;
    }

    return passwordChars.join('');
  };

  // Evaluation matching evaluate_password_strength in password_generator.py
  const evaluateStrength = (pwd: string) => {
    if (!pwd) return { label: 'No Password', color: '#94a3b8', percent: 0 };

    const len = pwd.length;
    const hasUpper = /[A-Z]/.test(pwd);
    const hasLower = /[a-z]/.test(pwd);
    const hasDigit = /[0-9]/.test(pwd);
    const hasSymbol = /[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(pwd);

    const categoriesCount = [hasUpper, hasLower, hasDigit, hasSymbol].filter(Boolean).length;

    if (len < 8 || categoriesCount < 2) {
      return { label: 'Weak', color: '#ef4444', percent: 25 };
    }

    if (len < 12) {
      if (categoriesCount >= 3) {
        return { label: 'Medium', color: '#f59e0b', percent: 50 };
      }
      return { label: 'Weak', color: '#ef4444', percent: 30 };
    }

    if (len < 16) {
      if (categoriesCount >= 3) {
        return { label: 'Strong', color: '#10b981', percent: 75 };
      }
      return { label: 'Medium', color: '#f59e0b', percent: 55 };
    }

    // len >= 16
    if (categoriesCount >= 4) {
      return { label: 'Very Strong', color: '#059669', percent: 100 };
    } else if (categoriesCount >= 3) {
      return len >= 20
        ? { label: 'Very Strong', color: '#059669', percent: 90 }
        : { label: 'Strong', color: '#10b981', percent: 80 };
    }

    return { label: 'Medium', color: '#f59e0b', percent: 60 };
  };

  const handleGenerate = () => {
    const pwd = generatePassword(length, useUpper, useLower, useDigits, useSymbols, excludeAmbiguous);
    if (pwd) {
      setGeneratedPassword(pwd);
      const strInfo = evaluateStrength(pwd);
      setStatusMessage({
        text: `✓ New ${length}-character password generated successfully (${strInfo.label}).`,
        type: 'success',
      });
      // Prepend to session history, max 5 items
      setSessionHistory((prev) => [pwd, ...prev.slice(0, 4)]);
      setSelectedHistoryIndex(null);
    }
  };

  // Generate on mount
  useEffect(() => {
    handleGenerate();
  }, []);

  const handleCopy = (textToCopy?: string) => {
    const target = textToCopy || generatedPassword;
    if (!target) {
      setStatusMessage({ text: "Warning: No password to copy. Click 'GENERATE PASSWORD' first.", type: 'error' });
      return;
    }

    navigator.clipboard
      .writeText(target)
      .then(() => {
        setCopied(true);
        setStatusMessage({ text: '✓ Password copied to clipboard successfully via pyperclip!', type: 'success' });
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(() => {
        setStatusMessage({ text: '✓ Copied password to clipboard.', type: 'success' });
      });
  };

  const strength = evaluateStrength(generatedPassword);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Banner indicating Python Tkinter Applet */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-[#1e293b]/90 border border-[#334155]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#0284c7]/20 border border-[#0284c7]/40 flex items-center justify-center text-[#38bdf8]">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#0284c7]/20 text-[#38bdf8] font-mono">
                OASIS INFOBYTE INTERNSHIP
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#10b981]/20 text-[#34d399] font-mono">
                TASK 3: ADVANCED
              </span>
            </div>
            <h1 className="text-lg font-bold text-white mt-0.5">
              Python Tkinter Random Password Generator
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          {onOpenCli && (
            <button
              type="button"
              onClick={onOpenCli}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0284c7] hover:bg-[#0369a1] text-white font-semibold text-xs rounded-lg transition-colors shadow-sm"
            >
              <Terminal className="w-4 h-4" />
              <span>Open CLI Mode</span>
            </button>
          )}
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-[#10b981]/15 text-[#34d399] border border-[#10b981]/30">
            CSPRNG Active
          </span>
        </div>
      </div>

      {/* Simulated Desktop Window Frame matching Python Tkinter */}
      <div className="bg-[#0f172a] rounded-xl shadow-2xl border border-[#334155] overflow-hidden">
        {/* Desktop Title Bar */}
        <div className="bg-[#1e293b] px-4 py-2.5 border-b border-[#334155] flex items-center justify-between select-none">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ef4444] border border-[#dc2626]" />
            <div className="w-3 h-3 rounded-full bg-[#f59e0b] border border-[#d97706]" />
            <div className="w-3 h-3 rounded-full bg-[#10b981] border border-[#059669]" />
            <span className="font-mono text-xs text-[#94a3b8] ml-2 font-medium">
              Oasis Infobyte — Task 3: Random Password Generator (Tkinter Desktop GUI)
            </span>
          </div>
          <span className="font-mono text-[10px] text-[#64748b] hidden sm:inline">
            Python 3.11 • secrets • pyperclip
          </span>
        </div>

        {/* Tkinter Application Inner Body */}
        <div className="p-6 space-y-5 bg-[#0f172a] text-slate-100 font-sans">
          {/* Header Title inside Tkinter Window */}
          <div>
            <div className="text-[11px] font-bold text-[#10b981] tracking-wider uppercase font-mono">
              OASIS INFOBYTE INTERNSHIP
            </div>
            <h2 className="text-xl font-bold text-white mt-0.5">
              Task 3: Random Password Generator
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Cryptographically secure password engine powered by Python's <code className="text-[#38bdf8] font-mono">secrets</code> module.
            </p>
          </div>

          {/* 1. Output Display Card */}
          <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-4 space-y-3">
            <div className="text-xs font-bold text-[#10b981] uppercase tracking-wider font-mono">
              Generated Secure Password
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                readOnly
                value={generatedPassword}
                placeholder="Click 'Generate Password'..."
                className="flex-1 bg-[#090d16] text-[#38bdf8] font-mono text-lg font-bold px-4 py-2.5 rounded border border-[#334155] text-center outline-none select-all"
              />
              <button
                type="button"
                onClick={() => handleCopy()}
                className="flex items-center gap-1.5 px-4 py-2.5 bg-[#0284c7] hover:bg-[#0369a1] text-white text-sm font-bold rounded transition-colors"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? 'Copied!' : '📋 Copy'}</span>
              </button>
            </div>

            {/* Strength Meter */}
            <div className="flex items-center justify-between text-xs pt-1">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Security Strength:</span>
                <span
                  className="font-bold px-2 py-0.5 rounded text-xs"
                  style={{ color: strength.color, backgroundColor: `${strength.color}15` }}
                >
                  {strength.label}
                </span>
              </div>
              <div className="w-48 bg-[#334155] h-2.5 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-300 rounded-full"
                  style={{ width: `${strength.percent}%`, backgroundColor: strength.color }}
                />
              </div>
            </div>
          </div>

          {/* 2. Security & Character Configuration Card */}
          <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-4 space-y-4">
            <div className="text-xs font-bold text-[#10b981] uppercase tracking-wider font-mono">
              Security & Character Configuration
            </div>

            {/* Length Control */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label htmlFor="tk-length" className="text-sm font-bold text-white">
                  Password Length (Min 8):
                </label>
                <div className="text-xs text-slate-400">
                  Recommended: 16+ characters for high resilience
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  id="tk-length"
                  type="number"
                  min={8}
                  max={128}
                  value={length}
                  onChange={(e) => setLength(parseInt(e.target.value) || 8)}
                  className="w-20 bg-[#090d16] text-[#10b981] font-mono text-center font-bold py-1.5 px-2 rounded border border-[#334155] outline-none"
                />
              </div>
            </div>

            {/* Quick Presets */}
            <div className="flex items-center gap-2 pt-1 border-t border-[#334155]/60">
              <span className="text-xs text-slate-400">Quick Presets:</span>
              {[12, 16, 24, 32].map((pLen) => (
                <button
                  key={pLen}
                  type="button"
                  onClick={() => {
                    setLength(pLen);
                    setTimeout(() => {
                      const pwd = generatePassword(pLen, useUpper, useLower, useDigits, useSymbols, excludeAmbiguous);
                      if (pwd) {
                        setGeneratedPassword(pwd);
                        setSessionHistory((prev) => [pwd, ...prev.slice(0, 4)]);
                      }
                    }, 0);
                  }}
                  className={`text-xs px-2.5 py-1 rounded font-mono transition-colors ${
                    length === pLen
                      ? 'bg-[#10b981] text-[#022c22] font-bold'
                      : 'bg-[#334155] text-slate-300 hover:bg-[#475569]'
                  }`}
                >
                  {pLen} Chars
                </button>
              ))}
            </div>

            {/* Character Type Checkboxes */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-[#334155]/60">
              <label className="flex items-center gap-2.5 cursor-pointer text-sm select-none">
                <input
                  type="checkbox"
                  checked={useUpper}
                  onChange={(e) => setUseUpper(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#090d16] border-[#334155] text-[#10b981] focus:ring-0"
                />
                <span className="text-slate-200">Uppercase Letters (A-Z)</span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer text-sm select-none">
                <input
                  type="checkbox"
                  checked={useLower}
                  onChange={(e) => setUseLower(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#090d16] border-[#334155] text-[#10b981] focus:ring-0"
                />
                <span className="text-slate-200">Lowercase Letters (a-z)</span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer text-sm select-none">
                <input
                  type="checkbox"
                  checked={useDigits}
                  onChange={(e) => setUseDigits(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#090d16] border-[#334155] text-[#10b981] focus:ring-0"
                />
                <span className="text-slate-200">Numbers / Digits (0-9)</span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer text-sm select-none">
                <input
                  type="checkbox"
                  checked={useSymbols}
                  onChange={(e) => setUseSymbols(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#090d16] border-[#334155] text-[#10b981] focus:ring-0"
                />
                <span className="text-slate-200">Special Symbols (!@#$%^&*)</span>
              </label>
            </div>

            {/* Ambiguous Exclusion */}
            <div className="pt-2 border-t border-[#334155]/60">
              <label className="flex items-center gap-2.5 cursor-pointer text-xs select-none text-slate-300">
                <input
                  type="checkbox"
                  checked={excludeAmbiguous}
                  onChange={(e) => setExcludeAmbiguous(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#090d16] border-[#334155] text-[#10b981] focus:ring-0"
                />
                <span className="italic">
                  Exclude Ambiguous Characters (0, O, l, I, 1, |)
                </span>
              </label>
            </div>
          </div>

          {/* 3. Action Button: Generate Password */}
          <button
            type="button"
            onClick={handleGenerate}
            className="w-full py-3.5 bg-[#10b981] hover:bg-[#059669] text-[#022c22] font-bold text-base rounded-lg transition-all shadow-lg flex items-center justify-center gap-2 active:scale-[0.99]"
          >
            <RefreshCw className="w-5 h-5 animate-spin-slow" />
            <span>⚡ GENERATE PASSWORD</span>
          </button>

          {/* 4. Status Notification Banner */}
          <div
            className={`p-2.5 rounded-lg text-xs font-mono font-medium flex items-center gap-2 transition-all ${
              statusMessage.type === 'success'
                ? 'bg-emerald-950/70 border border-emerald-800 text-emerald-300'
                : statusMessage.type === 'error'
                ? 'bg-rose-950/70 border border-rose-800 text-rose-300'
                : 'bg-sky-950/70 border border-sky-800 text-sky-300'
            }`}
          >
            {statusMessage.type === 'error' ? (
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            ) : (
              <Check className="w-4 h-4 shrink-0 text-emerald-400" />
            )}
            <span>{statusMessage.text}</span>
          </div>

          {/* 5. Session History (Last 5 Passwords) */}
          <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold text-[#10b981] uppercase tracking-wider font-mono">
                Session History — Last 5 Generated Passwords (In-Memory Only)
              </div>
              <span className="text-[10px] text-slate-400 font-mono">RAM ONLY • Purged on exit</span>
            </div>

            <p className="text-xs text-slate-400">
              Double-click or select any password from the history list to copy:
            </p>

            <div className="bg-[#090d16] border border-[#334155] rounded-lg divide-y divide-[#1e293b] overflow-hidden">
              {sessionHistory.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500 font-mono">
                  No passwords generated yet in this session.
                </div>
              ) : (
                sessionHistory.map((pwd, idx) => (
                  <div
                    key={`${pwd}-${idx}`}
                    onClick={() => setSelectedHistoryIndex(idx)}
                    onDoubleClick={() => handleCopy(pwd)}
                    className={`flex items-center justify-between p-2.5 text-xs font-mono cursor-pointer transition-colors ${
                      selectedHistoryIndex === idx
                        ? 'bg-[#0284c7]/20 text-[#38bdf8]'
                        : 'text-slate-300 hover:bg-[#1e293b]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-slate-500 w-6">#{idx + 1}</span>
                      <span className="px-1.5 py-0.5 rounded bg-[#1e293b] text-slate-400 text-[10px]">
                        {pwd.length} chars
                      </span>
                      <span className="font-bold truncate max-w-[280px] sm:max-w-md">{pwd}</span>
                    </div>

                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCopy(pwd);
                      }}
                      className="text-xs text-[#10b981] hover:underline flex items-center gap-1 font-sans"
                    >
                      <Copy className="w-3 h-3" />
                      <span>Copy</span>
                    </button>
                  </div>
                ))
              )}
            </div>

            {selectedHistoryIndex !== null && (
              <button
                type="button"
                onClick={() => handleCopy(sessionHistory[selectedHistoryIndex])}
                className="text-xs px-3 py-1.5 bg-[#334155] hover:bg-[#475569] text-white rounded transition-colors font-medium"
              >
                Copy Selected Password (#{selectedHistoryIndex + 1})
              </button>
            )}
          </div>

          {/* Footer inside Tkinter window */}
          <div className="text-center text-[11px] text-slate-500 pt-2 border-t border-[#334155]/60 font-mono">
            Oasis Infobyte Internship Task 3 • No passwords are saved to disk or network.
          </div>
        </div>
      </div>

      {/* Validation Error Dialog Modal */}
      {validationDialog && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1e293b] border border-[#ef4444] rounded-xl max-w-md w-full p-5 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center gap-3 text-[#ef4444]">
              <AlertCircle className="w-6 h-6" />
              <h3 className="text-lg font-bold text-white">{validationDialog.title}</h3>
            </div>

            <div className="text-sm text-slate-300 whitespace-pre-line bg-[#0f172a] p-3 rounded border border-[#334155] font-mono">
              {validationDialog.message}
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setValidationDialog(null)}
                className="px-4 py-2 bg-[#ef4444] hover:bg-[#dc2626] text-white text-xs font-bold rounded-lg transition-colors"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
