import { useEffect, useMemo, useRef, useState } from "react";
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
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const baseFilename = useMemo(() => {
    if (!documentTree) return "docstruct";
    const name = documentTree.source_file || "docstruct";
    return name.replace(/\.[^.]*$/, "");
  }, [documentTree]);

  const jsonText = useMemo(() => {
    if (!documentTree) return "";
    return JSON.stringify({ document: documentTree }, null, 2);
  }, [documentTree]);

  useEffect(() => {
    if (!open) return;
    const onMouseDown = (e: MouseEvent) => {
      if (!rootRef.current) return;
      const target = e.target as Node | null;
      if (target && !rootRef.current.contains(target)) setOpen(false);
    };

    document.addEventListener("mousedown", onMouseDown);
    return () => document.removeEventListener("mousedown", onMouseDown);
  }, [open]);

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800 transition"
      >
        Download <span className="text-[10px] opacity-70 ml-1">v</span>
      </button>

      {open && (
        <div className="absolute right-0 mt-2 min-w-[170px] rounded-md border border-slate-700 bg-slate-900 shadow-lg z-20 overflow-hidden">
          <button
            type="button"
            onClick={() => {
              downloadText(
                `${baseFilename}.docstruct.json`,
                jsonText
              );
              setOpen(false);
            }}
            className="w-full text-left px-3 py-2 text-xs text-slate-100 hover:bg-slate-800 transition"
          >
            Download JSON
          </button>
          <button
            type="button"
            onClick={() => {
              downloadText(`${baseFilename}.docstruct.md`, markdownText);
              setOpen(false);
            }}
            className="w-full text-left px-3 py-2 text-xs text-slate-100 hover:bg-slate-800 transition"
          >
            Download MD
          </button>
        </div>
      )}
    </div>
  );
}

