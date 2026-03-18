interface GenericViewerProps {
  fileUrl: string;
  fileName?: string | null;
}

export function GenericViewer({ fileUrl, fileName }: GenericViewerProps) {
  return (
    <div className="h-full min-h-0 flex flex-col">
      <div className="text-xs text-slate-400 py-2">
        Viewer for this format is not implemented yet.
      </div>

      <div className="flex-1 min-h-0 overflow-auto rounded-xl border border-slate-800 bg-slate-950/20 p-4">
        <p className="text-sm text-slate-200 font-medium">
          {fileName ? `File: ${fileName}` : "Uploaded document"}
        </p>
        <p className="mt-2 text-xs text-slate-400">
          You can still preview/download the original file.
        </p>
        <div className="mt-4">
          <a
            href={fileUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800 transition"
          >
            Open original file
          </a>
        </div>
      </div>
    </div>
  );
}

