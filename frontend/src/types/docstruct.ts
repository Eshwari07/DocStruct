export type SourceFormat = "pdf" | "docx" | "html" | "markdown" | "epub" | "pptx" | "image";
export type ExtractionPath = "fast" | "slow" | "mixed";

export type NodeType = "root" | "parent" | "child";
export type JobStatus = "idle" | "uploading" | "processing" | "complete" | "error";
export type OutputFormat = "json" | "markdown";

export interface PageRange {
  physical_start: number;
  physical_end: number;
  logical_start: string | null;
  logical_end: string | null;
}

export interface ImageRef {
  label: string;
  caption: string;
  path: string;
}

export interface DocNode {
  id: string;
  section_id: string;
  depth: number;
  node_type: NodeType;
  title: string;
  text: string;
  pages: PageRange | null;
  confidence: number;
  images: ImageRef[];
  children: DocNode[];
}

export interface DocumentTree {
  source_file: string;
  source_format: SourceFormat;
  total_pages: number;
  extracted_at: string;
  extraction_path: ExtractionPath;
  nodes: DocNode[];
}

export interface ExtractionStats {
  total_nodes: number;
  extraction_path: ExtractionPath;
  elapsed_seconds: number;
  total_pages: number;
}

export interface ExtractionResult {
  document: DocumentTree;
  markdown: string;
  stats: ExtractionStats;
}

export interface BackendExtractResponse {
  job_id: string;
  status: "processing";
  filename: string;
  file_size_bytes: number;
}

export interface BackendJobStatusResponse {
  job_id: string;
  status: "processing" | "complete" | "error";
  progress_page: number;
  total_pages: number;
  elapsed_seconds: number;
  error?: string;
}

