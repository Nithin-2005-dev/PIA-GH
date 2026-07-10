import { create } from 'zustand';

export interface WorkspaceConfig {
  repository: string;
  dataset: string;
  branch: string;
  commitWindow: number;
  provider: string;
  benchmarkProfile: string;
}

interface WorkspaceState {
  workspace: WorkspaceConfig;
  updateWorkspace: (updates: Partial<WorkspaceConfig>) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  workspace: {
    repository: 'facebook/react',
    dataset: 'v1',
    branch: 'main',
    commitWindow: 100,
    provider: 'sqlite',
    benchmarkProfile: 'default'
  },
  updateWorkspace: (updates) => set((state) => ({ 
    workspace: { ...state.workspace, ...updates } 
  })),
}));
