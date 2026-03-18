import type { JobStatus } from "../../types/docstruct";
import { useDocStructStore } from "../../store/useDocStructStore";

interface StatusBarProps {
  jobStatus: JobStatus;
}

export function StatusBar({ jobStatus }: StatusBarProps) {
  const { extractionStats, documentTree } = useDocStructStore();

  if (!extractionStats || !documentTree) {
    return (
      <div className="border-t border-slate-800 px-6 py-2 text-xs text-slate-400 flex items-center justify-between">
        <span>{jobStatus === "idle" ? "Waiting for upload…" : jobStatus}</span>
        <span className="hidden sm:block">Local pipeline</span>
      </div>
    );
  }

  return (
    <div className="border-t border-slate-800 px-6 py-2 text-xs text-slate-400 flex items-center justify-between">
      <span>
        Extracted {extractionStats.total_nodes} sections from {documentTree.source_file} ·{" "}
        {extractionStats.extraction_path} path · {extractionStats.total_pages} pages
      </span>
      <span className="hidden sm:block">
        {extractionStats.elapsed_seconds.toFixed(1)}s
      </span>
    </div>
  );
}
