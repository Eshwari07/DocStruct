import { useMemo, useState } from "react";
import { useDocStructStore } from "../../store/useDocStructStore";

interface DownloadBarProps {
  markdownText: string;
}

function downloadText(filename: string, text: string) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function DownloadBar({ markdownText }: DownloadBarProps) {
  const { documentTree } = useDocStructStore();
  const [toast, setToast] = useState<string | null>(null);

  const baseFilename = useMemo(() => {
    if (!documentTree) return "docstruct";
    const name = documentTree.source_file || "docstruct";
    return name.replace(/\.[^.]*$/, "");
  }, [documentTree]);

  const jsonText = useMemo(() => {
    if (!documentTree) return "";
    return JSON.stringify({ document: documentTree }, null, 2);
  }, [documentTree]);

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setToast("Copied to clipboard");
      window.setTimeout(() => setToast(null), 2000);
    } catch {
      setToast("Copy failed");
      window.setTimeout(() => setToast(null), 2000);
    }
  };

  return (
    <div className="flex items-center justify-between gap-3 flex-wrap">
      <div className="flex items-center gap-2 flex-wrap">
      <button
        type="button"
        onClick={() => downloadText(`${baseFilename}.docstruct.json`, jsonText)}
        className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800 transition"
      >
        Download JSON
      </button>
      <button
        type="button"
        onClick={() => downloadText(`${baseFilename}.docstruct.md`, markdownText)}
        className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800 transition"
      >
        Download MD
      </button>
      <button
        type="button"
        onClick={() => void copy(jsonText)}
        className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800 transition"
      >
        Copy JSON
      </button>
      <button
        type="button"
        onClick={() => void copy(markdownText)}
        className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800 transition"
      >
        Copy MD
      </button>
      </div>

      {toast && (
        <div className="fixed bottom-4 right-4 bg-gray-900 text-white text-sm px-4 py-2 rounded-lg shadow-lg z-50">
          {toast}
        </div>
      )}
    </div>
  );
}

