interface HtmlViewerProps {
  fileUrl: string;
}

export function HtmlViewer({ fileUrl }: HtmlViewerProps) {
  return (
    <div className="h-full min-h-0 flex flex-col">
      <div className="text-xs text-slate-400 py-2">
        Rendering HTML in an iframe.
      </div>
      <div className="flex-1 min-h-0 overflow-hidden rounded-xl border border-slate-800 bg-slate-950/20">
        <iframe
          title="Document HTML preview"
          src={fileUrl}
          className="w-full h-full"
        />
      </div>
    </div>
  );
}

