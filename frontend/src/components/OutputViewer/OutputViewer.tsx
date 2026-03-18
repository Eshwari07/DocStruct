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
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <FormatToggle />
          {showLongWarning && (
            <div className="text-xs text-amber-200 bg-amber-400/10 border border-amber-300/20 px-3 py-1 rounded-full whitespace-nowrap">
              Long document: may take longer to process.
            </div>
          )}
        </div>
        <DownloadBar markdownText={markdownText} />
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto">
        {outputFormat === "markdown" ? (
          <MarkdownView markdown={markdownText} />
        ) : (
          <JsonView documentTree={documentTree} />
        )}
      </div>

      {/* Download UI moved to the top bar */}
    </div>
  );
}

