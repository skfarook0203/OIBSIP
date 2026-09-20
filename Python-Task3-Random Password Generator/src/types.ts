export interface PasswordConfig {
  length: number;
  useUpper: boolean;
  useLower: boolean;
  useNumbers: boolean;
  useSymbols: boolean;
  excludeAmbiguous: boolean;
  autoCopy: boolean;
}

export type PasswordQuality = 'Weak' | 'Medium' | 'Strong' | 'Very Strong';

export interface PasswordTelemetry {
  rawPassword: string;
  length: number;
  poolSize: number;
  activeClassesCount: number;
  entropyBits: number;
  quality: PasswordQuality;
  qualityColor: string;
  scoreSegments: number; // 1 to 6
  crackTimeDisplay: string;
  searchSpaceDisplay: string;
  classCounts: {
    upper: number;
    lower: number;
    numbers: number;
    symbols: number;
    ambiguous: number;
  };
}

export interface HistoryEntry {
  id: string;
  password: string;
  length: number;
  entropyBits: number;
  quality: PasswordQuality;
  timestamp: number;
}

export type NavNodeId =
  | 'tkinter-gui'
  | 'internship-docs'
  | 'cli-terminal';
