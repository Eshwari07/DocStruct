import type { JobStatus } from "../../types/docstruct";
import { useDocStructStore } from "../../store/useDocStructStore";

interface TopBarProps {
  jobStatus: JobStatus;
  onChooseFile: (file: File) => void;
}

export function TopBar({ jobStatus, onChooseFile }: TopBarProps) {
  const { extractionStats, documentTree } = useDocStructStore();

  const inputAccept = [
    ".pdf",
    ".docx",
    ".doc",
    ".html",
    ".htm",
    ".md",
    ".markdown",
    ".epub",
    ".pptx",
    ".ppt",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif"
  ].join(",");

  return (
    <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-600 flex items-center justify-center text-xs font-semibold">
          DS
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-tight">DocStruct</h1>
          <p className="text-xs text-slate-400">Local document structure extraction</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex flex-col items-end">
          <span className="text-xs text-slate-400">Status</span>
          <span className="text-xs font-medium text-slate-200">
            {jobStatus === "idle" ? "Ready" : jobStatus}
          </span>
        </div>

        <label className="inline-flex items-center gap-2 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm font-medium text-slate-100 shadow-sm hover:bg-slate-800 cursor-pointer transition">
          <span>{jobStatus === "idle" ? "Upload" : "Upload new"}</span>
          <input
            type="file"
            className="hidden"
            accept={inputAccept}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onChooseFile(file);
              // Allow selecting the same file again.
              event.currentTarget.value = "";
            }}
          />
        </label>
      </div>
    </header>
  );
}
