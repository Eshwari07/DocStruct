import { useEffect, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { validateFile } from "./utils/fileHelpers";
import { useDocStructStore } from "./store/useDocStructStore";
import { useExtraction } from "./hooks/useExtraction";
import { TopBar } from "./components/TopBar/TopBar";
import { UploadZone } from "./components/UploadZone/UploadZone";
import { DocumentViewer } from "./components/DocumentViewer/DocumentViewer";
import { OutputViewer } from "./components/OutputViewer/OutputViewer";
import { StatusBar } from "./components/StatusBar/StatusBar";

function App() {
  const { startExtraction, cancelJob } = useExtraction();
  const {
    jobStatus,
    errorMessage,
    documentTree,
    progressPage,
    totalPages,
    elapsedSeconds,
    setErrorMessage,
    reset
  } = useDocStructStore();

  const [isNarrow, setIsNarrow] = useState(false);
  useEffect(() => {
    const media = window.matchMedia("(max-width: 900px)");
    const update = () => setIsNarrow(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  const handleChooseFile = (file: File) => {
    const err = validateFile(file);
    if (err) {
      setErrorMessage(err);
      reset();
      return;
    }
    setErrorMessage(null);
    void startExtraction(file);
  };

  const showUploadOverlay = jobStatus === "idle" && !documentTree && !errorMessage;
  const showProgress = jobStatus === "processing";
  const pct = totalPages > 0 ? (progressPage / totalPages) * 100 : 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <TopBar jobStatus={jobStatus} onChooseFile={handleChooseFile} />

      {showProgress && (
        <div className="px-6 pt-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-3">
            <div className="text-xs text-slate-300">
              Processing…{" "}
              <span className="text-slate-100 font-semibold">
                {progressPage} / {totalPages || "?"} pages
              </span>{" "}
              <span className="text-slate-400">({elapsedSeconds.toFixed(1)}s)</span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-purple-500"
                style={{ width: `${Math.min(100, pct)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {jobStatus === "error" && errorMessage && (
        <div className="px-6 pt-4">
          <div className="rounded-xl border border-red-400/30 bg-red-500/10 p-4">
            <div className="text-sm font-semibold text-red-200">Extraction failed</div>
            <div className="text-xs text-red-200/90 mt-1">{errorMessage}</div>
            <div className="flex gap-2 mt-3">
              <button
                className="px-3 py-1.5 rounded-md border border-red-400/40 bg-red-500/20 hover:bg-red-500/30 text-xs text-red-100"
                onClick={() => reset()}
              >
                Try again
              </button>
              <button
                className="px-3 py-1.5 rounded-md border border-slate-700 bg-slate-900/30 hover:bg-slate-900 text-xs"
                onClick={() => void cancelJob()}
              >
                Cancel job
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 px-6 py-4 min-h-0">
        <PanelGroup
          direction={isNarrow ? "vertical" : "horizontal"}
          className="h-full min-h-0 rounded-xl border border-slate-800 overflow-hidden"
          autoSaveId="docstruct-layout"
        >
          <Panel defaultSize={50} minSize={25}>
            <div className="h-full min-h-0 overflow-auto bg-slate-950/20">
              <DocumentViewer />
            </div>
          </Panel>

          <PanelResizeHandle className="w-1 bg-slate-800 hover:bg-purple-400/60 transition-colors cursor-col-resize" />

          <Panel defaultSize={50} minSize={25}>
            <div className="h-full min-h-0 overflow-auto bg-slate-950/20">
              <OutputViewer />
            </div>
          </Panel>
        </PanelGroup>
      </div>

      <StatusBar jobStatus={jobStatus} />

      <UploadZone
        visible={showUploadOverlay}
        onFileSelected={(file) => handleChooseFile(file)}
        errorMessage={errorMessage}
      />
    </div>
  );
}

export default App;

