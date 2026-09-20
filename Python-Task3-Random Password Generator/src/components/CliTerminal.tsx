import React, { useState, useRef, useEffect } from 'react';
import { Terminal as TerminalIcon, RotateCcw, Copy, Check, Info } from 'lucide-react';
import { cryptoRandomInt, cryptoShuffle } from '../utils/cryptoGenerator';

interface TerminalLine {
  id: string;
  type: 'system' | 'prompt' | 'input' | 'output' | 'error' | 'success';
  text: string;
}

type Step =
  | 'length'
  | 'upper'
  | 'lower'
  | 'digits'
  | 'symbols'
  | 'result'
  | 'restart';

export const CliTerminal: React.FC = () => {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      id: '1',
      type: 'system',
      text: '============================================================',
    },
    {
      id: '2',
      type: 'system',
      text: '       CIPHERCRAFT - RANDOM PASSWORD GENERATOR (CLI)        ',
    },
    {
      id: '3',
      type: 'system',
      text: ' Tech Stack: Python 3.11+ standard library (random, string) ',
    },
    {
      id: '4',
      type: 'system',
      text: '============================================================',
    },
    {
      id: '5',
      type: 'prompt',
      text: 'Enter desired password length (minimum 8): ',
    },
  ]);

  const [step, setStep] = useState<Step>('length');
  const [currentInput, setCurrentInput] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);

  // Session state accumulation
  const [tempLength, setTempLength] = useState<number>(16);
  const [tempUpper, setTempUpper] = useState<boolean>(true);
  const [tempLower, setTempLower] = useState<boolean>(true);
  const [tempDigits, setTempDigits] = useState<boolean>(true);
  const [tempSymbols, setTempSymbols] = useState<boolean>(true);
  const [lastGenerated, setLastGenerated] = useState<string>('');

  const inputRef = useRef<HTMLInputElement>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [lines]);

  const addLine = (type: TerminalLine['type'], text: string) => {
    setLines((prev) => [...prev, { id: Math.random().toString(), type, text }]);
  };

  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const val = currentInput.trim();
    setCurrentInput('');

    // Print what the user typed
    addLine('input', val);

    if (step === 'length') {
      const parsed = parseInt(val);
      if (isNaN(parsed)) {
        addLine('error', '[!] Validation Error: Please enter a valid numerical integer.');
        addLine('prompt', 'Enter desired password length (minimum 8): ');
        return;
      }
      if (parsed < 8) {
        addLine('error', '[!] Validation Error: Password length must be at least 8 characters.');
        addLine('prompt', 'Enter desired password length (minimum 8): ');
        return;
      }
      setTempLength(parsed);
      setStep('upper');
      addLine('output', `[i] Length set to ${parsed} characters.`);
      addLine('system', '\nSelect character types to include (at least 2 required):');
      addLine('prompt', '  - Include uppercase letters (A-Z)? [Y/n]: ');
    } else if (step === 'upper') {
      const isYes = val === '' || val.toLowerCase().startsWith('y');
      setTempUpper(isYes);
      setStep('lower');
      addLine('prompt', '  - Include lowercase letters (a-z)? [Y/n]: ');
    } else if (step === 'lower') {
      const isYes = val === '' || val.toLowerCase().startsWith('y');
      setTempLower(isYes);
      setStep('digits');
      addLine('prompt', '  - Include numbers (0-9)? [Y/n]: ');
    } else if (step === 'digits') {
      const isYes = val === '' || val.toLowerCase().startsWith('y');
      setTempDigits(isYes);
      setStep('symbols');
      addLine('prompt', '  - Include symbols (!@#$%^&*...)? [Y/n]: ');
    } else if (step === 'symbols') {
      const isSymbolsYes = val === '' || val.toLowerCase().startsWith('y');
      setTempSymbols(isSymbolsYes);

      // Validate at least 2 character types selected
      const selectedCount =
        (tempUpper ? 1 : 0) +
        (tempLower ? 1 : 0) +
        (tempDigits ? 1 : 0) +
        (isSymbolsYes ? 1 : 0);

      if (selectedCount < 2) {
        addLine('error', '\n[!] Security Policy Violation: You must select at least 2 character types.');
        addLine('error', '    Please reconfigure your character type selections.\n');
        setStep('upper');
        addLine('prompt', '  - Include uppercase letters (A-Z)? [Y/n]: ');
        return;
      }

      // Generate the password using CSPRNG with guaranteed representation per selected class
      const pools: string[] = [];
      if (tempUpper) pools.push('ABCDEFGHIJKLMNOPQRSTUVWXYZ');
      if (tempLower) pools.push('abcdefghijklmnopqrstuvwxyz');
      if (tempDigits) pools.push('0123456789');
      if (isSymbolsYes) pools.push('!@#$%^&*()_+-=[]{}|;:,.<>?');

      const guaranteedChars: string[] = [];
      let combinedPool = '';
      for (const p of pools) {
        guaranteedChars.push(p[cryptoRandomInt(p.length)]);
        combinedPool += p;
      }

      const remainingLength = Math.max(0, tempLength - guaranteedChars.length);
      const extraChars: string[] = [];
      for (let i = 0; i < remainingLength; i++) {
        extraChars.push(combinedPool[cryptoRandomInt(combinedPool.length)]);
      }

      const pwd = cryptoShuffle([...guaranteedChars, ...extraChars]).join('');

      setLastGenerated(pwd);
      addLine('system', '------------------------------------------------------------');
      addLine('success', ' [✓] GENERATED PASSWORD:');
      addLine('success', `     ${pwd}`);
      addLine('system', '------------------------------------------------------------');
      addLine('output', ` [i] Length: ${tempLength} chars | Pool Size: ${combinedPool.length} symbols`);
      addLine('system', '------------------------------------------------------------');
      addLine('prompt', 'Would you like to generate another password? [Y/n]: ');
      setStep('restart');
    } else if (step === 'restart') {
      const isYes = val === '' || val.toLowerCase().startsWith('y');
      if (isYes) {
        setStep('length');
        addLine('system', '\n============================================================');
        addLine('system', '       STARTING NEW GENERATION SESSION                      ');
        addLine('system', '============================================================');
        addLine('prompt', 'Enter desired password length (minimum 8): ');
      } else {
        addLine('system', '\nThank you for using CipherCraft. Stay secure! Session ended.');
        addLine('system', 'Press [Restart Session] above to run again.');
      }
    }
  };

  const restartSession = () => {
    setLines([
      {
        id: '1',
        type: 'system',
        text: '============================================================',
      },
      {
        id: '2',
        type: 'system',
        text: '       CIPHERCRAFT - RANDOM PASSWORD GENERATOR (CLI)        ',
      },
      {
        id: '3',
        type: 'system',
        text: ' Tech Stack: Python 3.11+ standard library (random, string) ',
      },
      {
        id: '4',
        type: 'system',
        text: '============================================================',
      },
      {
        id: '5',
        type: 'prompt',
        text: 'Enter desired password length (minimum 8): ',
      },
    ]);
    setStep('length');
    setCurrentInput('');
  };

  const copyResult = () => {
    if (!lastGenerated) return;
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(lastGenerated).catch(() => {});
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleQuickInput = (val: string) => {
    setCurrentInput(val);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col w-full max-w-5xl mx-auto gap-5 pb-12">
      {/* Title & Info Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#131a26] border border-[#262a33]">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-[#181c24] border border-[#262a33] text-[#4edea3]">
            <TerminalIcon className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-['Space_Grotesk'] text-base font-bold text-[#dfe2ee]">
                Interactive Python CLI Terminal
              </span>
              <span className="px-2 py-0.5 rounded bg-[#10b981]/20 text-[#4edea3] font-['JetBrains_Mono'] text-[10px] font-bold border border-[#10b981]/30">
                Beginner Tier
              </span>
            </div>
            <span className="text-xs text-[#86948a]">
              Interactive sandbox simulating <code className="text-[#4cd7f6]">python beginner_cli.py</code> with prompt validation & generation loop.
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {lastGenerated && (
            <button
              onClick={copyResult}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#181c24] border border-[#10b981]/40 text-[#4edea3] hover:bg-[#181c24]/80 text-xs font-mono transition-all"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Last'}</span>
            </button>
          )}

          <button
            onClick={restartSession}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#181c24] border border-[#262a33] hover:border-[#3c4a42] text-[#bbcabf] hover:text-white text-xs font-mono transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restart Session</span>
          </button>
        </div>
      </div>

      {/* Terminal Window */}
      <div 
        onClick={() => inputRef.current?.focus()}
        className="relative rounded-2xl bg-[#0a0e16] border border-[#262a33] shadow-2xl overflow-hidden cursor-text min-h-[460px] flex flex-col"
      >
        {/* Terminal Title Bar */}
        <div className="h-10 bg-[#131a26] border-b border-[#262a33] px-4 flex items-center justify-between select-none">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="ml-2 font-['JetBrains_Mono'] text-xs text-[#86948a]">
              bash - python3 ./cli_generator.py
            </span>
          </div>

          <span className="font-['JetBrains_Mono'] text-[10px] text-[#4edea3] uppercase tracking-wider">
            Virtual Shell Active
          </span>
        </div>

        {/* Terminal Screen Body */}
        <div className="flex-1 p-5 font-['JetBrains_Mono'] text-sm leading-relaxed overflow-y-auto max-h-[520px]">
          {lines.map((line) => {
            let color = 'text-[#dfe2ee]';
            if (line.type === 'system') color = 'text-[#86948a] font-semibold';
            if (line.type === 'prompt') color = 'text-[#4cd7f6] font-bold';
            if (line.type === 'input') color = 'text-[#4edea3] font-semibold';
            if (line.type === 'error') color = 'text-rose-400 font-semibold';
            if (line.type === 'success') color = 'text-[#4edea3] font-bold text-base bg-[#10b981]/10 px-2 py-0.5 rounded';
            if (line.type === 'output') color = 'text-[#bbcabf]';

            return (
              <div key={line.id} className={`${color} whitespace-pre-wrap py-0.5`}>
                {line.type === 'input' && <span className="text-[#86948a] mr-1">$ </span>}
                {line.text}
              </div>
            );
          })}

          {/* Active Input Line */}
          <form onSubmit={handleInputSubmit} className="flex items-center gap-1.5 pt-1 text-sm">
            <span className="text-[#4cd7f6] font-bold">
              {step === 'length' && 'Enter desired password length (min 8): '}
              {step === 'upper' && 'Include uppercase letters? [Y/n]: '}
              {step === 'lower' && 'Include lowercase letters? [Y/n]: '}
              {step === 'digits' && 'Include numbers? [Y/n]: '}
              {step === 'symbols' && 'Include symbols? [Y/n]: '}
              {step === 'restart' && 'Generate another password? [Y/n]: '}
            </span>
            <input
              ref={inputRef}
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              autoFocus
              className="flex-1 bg-transparent text-[#4edea3] font-bold outline-none font-['JetBrains_Mono']"
            />
          </form>

          <div ref={terminalEndRef} />
        </div>

        {/* Quick Suggestion Chips below terminal */}
        <div className="bg-[#131a26]/90 border-t border-[#262a33] p-3 px-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-xs font-mono text-[#86948a]">
            <span>Quick inputs:</span>
            {step === 'length' && (
              <>
                <button
                  type="button"
                  onClick={() => handleQuickInput('16')}
                  className="px-2 py-0.5 rounded bg-[#181c24] border border-[#262a33] text-[#4cd7f6] hover:border-[#4cd7f6]"
                >
                  16
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickInput('20')}
                  className="px-2 py-0.5 rounded bg-[#181c24] border border-[#262a33] text-[#4cd7f6] hover:border-[#4cd7f6]"
                >
                  20
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickInput('32')}
                  className="px-2 py-0.5 rounded bg-[#181c24] border border-[#262a33] text-[#4cd7f6] hover:border-[#4cd7f6]"
                >
                  32
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickInput('5')}
                  title="Test min 8 validation rejection"
                  className="px-2 py-0.5 rounded bg-rose-950/40 border border-rose-500/40 text-rose-300 hover:border-rose-400"
                >
                  5 (Test &lt; 8 Error)
                </button>
              </>
            )}

            {(step === 'upper' || step === 'lower' || step === 'digits' || step === 'symbols' || step === 'restart') && (
              <>
                <button
                  type="button"
                  onClick={() => handleQuickInput('y')}
                  className="px-2.5 py-0.5 rounded bg-[#10b981]/20 border border-[#10b981]/40 text-[#4edea3] font-bold"
                >
                  y (Yes)
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickInput('n')}
                  className="px-2.5 py-0.5 rounded bg-[#181c24] border border-[#262a33] text-[#86948a] hover:text-white"
                >
                  n (No)
                </button>
              </>
            )}
          </div>

          <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#86948a]">
            <Info className="w-3.5 h-3.5 text-[#4cd7f6]" />
            <span>Type response and press [Enter]</span>
          </div>
        </div>
      </div>
    </div>
  );
};
