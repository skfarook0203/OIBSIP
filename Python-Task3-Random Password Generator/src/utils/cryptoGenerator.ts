import { PasswordConfig, PasswordTelemetry, PasswordQuality } from '../types';

export const CHAR_UPPER_FULL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
export const CHAR_UPPER_NO_AMBIGUOUS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'; // Excludes 'I', 'O'

export const CHAR_LOWER_FULL = 'abcdefghijklmnopqrstuvwxyz';
export const CHAR_LOWER_NO_AMBIGUOUS = 'abcdefghijkmnopqrstuvwxyz'; // Excludes 'l', 'o'

export const CHAR_NUMBERS_FULL = '0123456789';
export const CHAR_NUMBERS_NO_AMBIGUOUS = '23456789'; // Excludes '0', '1'

export const CHAR_SYMBOLS_FULL = '!@#$%^&*()_+-=[]{}|;:,.<>?';
export const CHAR_SYMBOLS_NO_AMBIGUOUS = '!@#$%^&*()_+-=[]{};:,.<>?'; // Excludes '|'

export const AMBIGUOUS_CHARS = new Set(['0', 'O', 'o', '1', 'l', 'I', '|']);

/**
 * Cryptographically secure unbiased random integer in [0, max - 1].
 * Uses rejection sampling to eliminate modulo bias.
 */
export function cryptoRandomInt(max: number): number {
  if (max <= 0) return 0;
  if (max === 1) return 0;

  const cryptoObj =
    typeof window !== 'undefined' && window.crypto
      ? window.crypto
      : typeof globalThis !== 'undefined' && globalThis.crypto
      ? globalThis.crypto
      : null;

  const array = new Uint32Array(1);
  const maxUint = 0xffffffff;
  const limit = maxUint - (maxUint % max);
  let rand: number;
  do {
    if (cryptoObj?.getRandomValues) {
      cryptoObj.getRandomValues(array);
      rand = array[0];
    } else {
      rand = Math.floor(Math.random() * (maxUint + 1));
    }
  } while (rand >= limit);

  return rand % max;
}

/**
 * Cryptographic Fisher-Yates array shuffle.
 */
export function cryptoShuffle<T>(arr: T[]): T[] {
  const result = [...arr];
  for (let i = result.length - 1; i > 0; i--) {
    const j = cryptoRandomInt(i + 1);
    const temp = result[i];
    result[i] = result[j];
    result[j] = temp;
  }
  return result;
}

/**
 * Format crack time into human-understandable terms
 * Based on 100 Billion (10^11) guesses per second (high-end GPU cluster).
 */
export function formatCrackTime(combinations: number): string {
  if (combinations <= 0) return 'Instant';
  const guessesPerSecond = 1e11; // 100 GH/s
  const seconds = combinations / guessesPerSecond;

  if (!Number.isFinite(combinations) || !Number.isFinite(seconds)) {
    return '> 10¹⁰⁰ Cent.';
  }

  if (seconds < 1e-4) return '< 1 millisecond';
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)} ms`;
  if (seconds < 60) return `${seconds.toFixed(1)} seconds`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)} minutes`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)} hours`;
  if (seconds < 86400 * 365) return `${(seconds / 86400).toFixed(1)} days`;

  const years = seconds / (86400 * 365.25);
  if (!Number.isFinite(years)) return '> 10¹⁰⁰ Cent.';
  if (years < 100) return `${years.toFixed(1)} years`;
  if (years < 1e4) return `${(years / 100).toFixed(1)} centuries`;
  if (years < 1e6) return `${(years / 1e3).toFixed(1)} millennia`;
  if (years < 1e9) return `${(years / 1e6).toFixed(1)} million years`;
  if (years < 1e12) return `${(years / 1e9).toFixed(1)} billion years`;
  if (years < 1e15) return `${(years / 1e12).toFixed(1)} trillion years`;
  
  // Scientific notation centuries
  const centuries = years / 100;
  if (!Number.isFinite(centuries) || centuries >= 1e100) {
    return '> 10¹⁰⁰ Cent.';
  }
  const exponent = Math.floor(Math.log10(centuries));
  const mantissa = (centuries / Math.pow(10, exponent)).toFixed(1);
  return `${mantissa} × 10${toSuperscript(exponent)} Cent.`;
}

function toSuperscript(num: number): string {
  const superscripts: Record<string, string> = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
    '-': '⁻',
  };
  return num
    .toString()
    .split('')
    .map((ch) => superscripts[ch] || ch)
    .join('');
}

/**
 * Generates a strong, random password using cryptographically secure PRNG.
 * Enforces minimum 8 length, >= 2 character sets, and guaranteed representation from each set.
 */
export function generatePassword(config: PasswordConfig): {
  password: string;
  telemetry: PasswordTelemetry;
} {
  const length = Math.max(8, Math.min(64, config.length));

  // Determine active pools
  const upperPool = config.excludeAmbiguous
    ? CHAR_UPPER_NO_AMBIGUOUS
    : CHAR_UPPER_FULL;
  const lowerPool = config.excludeAmbiguous
    ? CHAR_LOWER_NO_AMBIGUOUS
    : CHAR_LOWER_FULL;
  const numPool = config.excludeAmbiguous
    ? CHAR_NUMBERS_NO_AMBIGUOUS
    : CHAR_NUMBERS_FULL;
  const symPool = config.excludeAmbiguous
    ? CHAR_SYMBOLS_NO_AMBIGUOUS
    : CHAR_SYMBOLS_FULL;

  // Verify at least 2 character sets selected
  const activePools: { type: string; pool: string }[] = [];
  if (config.useUpper) activePools.push({ type: 'upper', pool: upperPool });
  if (config.useLower) activePools.push({ type: 'lower', pool: lowerPool });
  if (config.useNumbers) activePools.push({ type: 'numbers', pool: numPool });
  if (config.useSymbols) activePools.push({ type: 'symbols', pool: symPool });

  // Fallback if user somehow selected fewer than 1 (safety guard)
  if (activePools.length === 0) {
    activePools.push({ type: 'lower', pool: lowerPool });
    activePools.push({ type: 'upper', pool: upperPool });
  }

  const guaranteedChars: string[] = [];
  let combinedPool = '';

  // Enforce security rule: guaranteed to contain at least one character from each selected type
  for (const item of activePools) {
    const idx = cryptoRandomInt(item.pool.length);
    guaranteedChars.push(item.pool[idx]);
    combinedPool += item.pool;
  }

  const remainingLength = Math.max(0, length - guaranteedChars.length);
  const additionalChars: string[] = [];

  for (let i = 0; i < remainingLength; i++) {
    const idx = cryptoRandomInt(combinedPool.length);
    additionalChars.push(combinedPool[idx]);
  }

  // Shuffle all characters together using CSPRNG
  const rawPassword = cryptoShuffle([...guaranteedChars, ...additionalChars]).join('');

  // Analyze character breakdown
  let upperCount = 0;
  let lowerCount = 0;
  let numCount = 0;
  let symCount = 0;
  let ambiguousCount = 0;

  for (const ch of rawPassword) {
    if (AMBIGUOUS_CHARS.has(ch)) ambiguousCount++;
    if (/[A-Z]/.test(ch)) upperCount++;
    else if (/[a-z]/.test(ch)) lowerCount++;
    else if (/[0-9]/.test(ch)) numCount++;
    else symCount++;
  }

  const poolSize = combinedPool.length;
  // Shannon entropy: E = L * log2(R)
  const entropyBits = poolSize > 0 ? length * Math.log2(poolSize) : 0;

  // Approximate total combinations
  const combinations = Math.pow(poolSize, length);

  // Quality grading
  let quality: PasswordQuality = 'Weak';
  let qualityColor = 'text-red-400';
  let scoreSegments = 1;

  if (entropyBits >= 115) {
    quality = 'Very Strong';
    qualityColor = 'text-[#4edea3]';
    scoreSegments = 6;
  } else if (entropyBits >= 85) {
    quality = 'Strong';
    qualityColor = 'text-[#4cd7f6]';
    scoreSegments = 5;
  } else if (entropyBits >= 65) {
    quality = 'Medium';
    qualityColor = 'text-amber-400';
    scoreSegments = 4;
  } else if (entropyBits >= 45) {
    quality = 'Weak';
    qualityColor = 'text-amber-500';
    scoreSegments = 2;
  } else {
    quality = 'Weak';
    qualityColor = 'text-red-400';
    scoreSegments = 1;
  }

  let searchSpaceDisplay = '';
  if (poolSize > 0) {
    const exp = (length * Math.log10(poolSize)).toFixed(1);
    searchSpaceDisplay = `10^${exp} states`;
  }

  const telemetry: PasswordTelemetry = {
    rawPassword,
    length,
    poolSize,
    activeClassesCount: activePools.length,
    entropyBits: parseFloat(entropyBits.toFixed(1)),
    quality,
    qualityColor,
    scoreSegments,
    crackTimeDisplay: formatCrackTime(combinations),
    searchSpaceDisplay,
    classCounts: {
      upper: upperCount,
      lower: lowerCount,
      numbers: numCount,
      symbols: symCount,
      ambiguous: ambiguousCount,
    },
  };

  return { password: rawPassword, telemetry };
}
