import { useDocStructStore } from "../../store/useDocStructStore";
import { DownloadBar } from "./DownloadBar";
import { FormatToggle } from "./FormatToggle";
import { JsonView } from "./JsonView";
import { MarkdownView } from "./MarkdownView";

export function OutputViewer() {
  const {
    documentTree,
    markdownOutput,
    outputFormat,
    extractionStats
  } = useDocStructStore();

  const markdownText = markdownOutput ?? "";

  if (!documentTree) {
    return (
      <div className="h-full flex flex-col p-4 text-sm text-slate-400">
        Upload a document to see extracted sections here.
      </div>
    );
  }

  const showLongWarning = (extractionStats?.total_pages ?? 0) > 200;

  return (
    <div className="h-full flex flex-col min-h-0">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <FormatToggle />
        {showLongWarning && (
          <div className="text-xs text-amber-200 bg-amber-400/10 border border-amber-300/20 px-3 py-1 rounded-full">
            Long document: may take longer to process.
          </div>
        )}
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        {outputFormat === "markdown" ? (
          <MarkdownView markdown={markdownText} />
        ) : (
          <JsonView documentTree={documentTree} />
        )}
      </div>

      <div className="border-t border-slate-800 px-4 py-3 bg-slate-950/40">
        <DownloadBar markdownText={markdownText} />
      </div>
    </div>
  );
}

