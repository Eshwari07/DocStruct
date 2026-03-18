import { create } from "zustand";
import type {
  DocumentTree,
  ExtractionResult,
  ExtractionStats,
  JobStatus,
  OutputFormat,
} from "../types/docstruct";

export interface DocStructState {
  // Upload state
  uploadedFile: File | null;
  jobId: string | null;
  jobStatus: JobStatus;
  errorMessage: string | null;

  // Extraction result
  documentTree: DocumentTree | null;
  markdownOutput: string | null;
  extractionStats: ExtractionStats | null;

  // Viewer state
  currentPage: number;
  totalPages: number;
  progressPage: number;
  elapsedSeconds: number;
  selectedNodeId: string | null;
  outputFormat: OutputFormat;
  expandedNodeIds: Set<string>;

  // Actions
  setUploadedFile: (file: File) => void;
  setJobId: (id: string) => void;
  setJobStatus: (status: JobStatus) => void;
  setErrorMessage: (message: string | null) => void;
  setResult: (tree: DocumentTree, markdown: string, stats: ExtractionStats) => void;
  setCurrentPage: (page: number) => void;
  setJobProgress: (progressPage: number, totalPages: number, elapsedSeconds: number) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setOutputFormat: (format: OutputFormat) => void;
  toggleExpanded: (nodeId: string) => void;
  expandAll: () => void;
  collapseAll: () => void;
  reset: () => void;
}

export const useDocStructStore = create<DocStructState>((set) => ({
  uploadedFile: null,
  jobId: null,
  jobStatus: "idle",
  errorMessage: null,

  documentTree: null,
  markdownOutput: null,
  extractionStats: null,

  currentPage: 1,
  totalPages: 1,
  progressPage: 0,
  elapsedSeconds: 0,
  selectedNodeId: null,
  outputFormat: "json",
  expandedNodeIds: new Set<string>(),

  setUploadedFile: (file) => set({ uploadedFile: file }),
  setJobId: (id) => set({ jobId: id }),
  setJobStatus: (status) => set({ jobStatus: status }),
  setErrorMessage: (message) => set({ errorMessage: message }),
  setResult: (tree, markdown, stats) =>
    set(() => {
      const expandedNodeIds = new Set<string>();
      const walk = (n: any) => {
        if (n.children && n.children.length > 0 && n.depth <= 2) {
          expandedNodeIds.add(n.id);
        }
        if (n.children && n.children.length) n.children.forEach(walk);
      };
      tree.nodes.forEach(walk);

      return {
        documentTree: tree,
        markdownOutput: markdown,
        extractionStats: stats,
        totalPages: stats.total_pages,
        currentPage: 1,
        expandedNodeIds,
      };
    }),
  setCurrentPage: (page) => set({ currentPage: page }),
  setJobProgress: (progressPage, totalPages, elapsedSeconds) =>
    set((state) => ({
      progressPage,
      totalPages: totalPages > 0 ? totalPages : state.totalPages,
      elapsedSeconds,
    })),
  setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),
  setOutputFormat: (format) => set({ outputFormat: format }),
  toggleExpanded: (nodeId) =>
    set((state) => {
      const next = new Set(state.expandedNodeIds);
      if (next.has(nodeId)) next.delete(nodeId);
      else next.add(nodeId);
      return { expandedNodeIds: next };
    }),
  expandAll: () =>
    set((state) => {
      const next = new Set<string>();
      const walk = (n: any) => {
        if (n.children && n.children.length) {
          next.add(n.id);
          n.children.forEach(walk);
        }
      };
      state.documentTree?.nodes.forEach(walk);
      return { expandedNodeIds: next };
    }),
  collapseAll: () => set({ expandedNodeIds: new Set<string>() }),
  reset: () =>
    set({
      uploadedFile: null,
      jobId: null,
      jobStatus: "idle",
      errorMessage: null,
      documentTree: null,
      markdownOutput: null,
      extractionStats: null,
      currentPage: 1,
      totalPages: 1,
      progressPage: 0,
      elapsedSeconds: 0,
      selectedNodeId: null,
      outputFormat: "json",
      expandedNodeIds: new Set<string>(),
    }),
}));

