import { useEffect, useRef, useState } from "react";

const ACCEPTED_FORMATS = [
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
];

interface UploadZoneProps {
  visible: boolean;
  onFileSelected: (file: File) => void;
  errorMessage: string | null;
}

export function UploadZone({ visible, onFileSelected, errorMessage }: UploadZoneProps) {
  const [isOver, setIsOver] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!visible) return;

    const onDragOver = (e: DragEvent) => {
      e.preventDefault();
      setIsOver(true);
    };

    const onDragLeave = (e: DragEvent) => {
      e.preventDefault();
      setIsOver(false);
    };

    const onDrop = (e: DragEvent) => {
      e.preventDefault();
      setIsOver(false);

      const file = e.dataTransfer?.files?.[0];
      if (!file) return;
      onFileSelected(file);
    };

    window.addEventListener("dragover", onDragOver);
    window.addEventListener("dragleave", onDragLeave);
    window.addEventListener("drop", onDrop);

    return () => {
      window.removeEventListener("dragover", onDragOver);
      window.removeEventListener("dragleave", onDragLeave);
      window.removeEventListener("drop", onDrop);
    };
  }, [visible, onFileSelected]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
        aria-hidden="true"
      />

      <div className="relative h-full w-full flex items-center justify-center p-6">
        <div
          className={`w-full max-w-2xl rounded-2xl border p-8 ${
            isOver ? "border-purple-400/60 bg-purple-500/5" : "border-slate-700 bg-slate-900/40"
          }`}
        >
          <h2 className="text-xl font-semibold">Drop a document to extract structure</h2>
          <p className="text-sm text-slate-400 mt-2">
            Runs locally (no cloud calls). Supported formats:{" "}
            <span className="text-slate-200">{ACCEPTED_FORMATS.join(", ")}</span>
          </p>

          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept={ACCEPTED_FORMATS.join(",")}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                onFileSelected(file);
              }
              // Allow selecting the same file again.
              event.currentTarget.value = "";
            }}
          />

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="inline-flex items-center rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm font-medium text-slate-100 shadow-sm hover:bg-slate-800 transition"
              onClick={() => inputRef.current?.click()}
            >
              Browse files
            </button>
            <span className="text-xs text-slate-400">
              or drop a file anywhere on this page
            </span>
          </div>

          {errorMessage && (
            <p className="mt-4 text-sm font-medium text-red-400">{errorMessage}</p>
          )}

          <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/30 p-4">
            <p className="text-xs text-slate-400">
              Tip: For best results, use PDFs with bookmarks/outline.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
