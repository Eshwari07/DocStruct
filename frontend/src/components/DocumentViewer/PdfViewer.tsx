import { useEffect, useMemo, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { useDocStructStore } from "../../store/useDocStructStore";
import type { DocNode } from "../../types/docstruct";
import { findDeepestNodeForPage, findNodeById, getPrimaryPageForNode } from "../../utils/treeHelpers";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

interface PdfViewerProps {
  fileUrl: string;
}

export function PdfViewer({ fileUrl }: PdfViewerProps) {
  const { documentTree, currentPage, totalPages, setCurrentPage, selectedNodeId, setSelectedNode, setJobProgress } =
    useDocStructStore();

  const [zoom, setZoom] = useState(1.2);
  const pageHighlightNode: DocNode | null = useMemo(() => {
    if (!documentTree || !selectedNodeId) return null;
    return findNodeById(documentTree, selectedNodeId);
  }, [documentTree, selectedNodeId]);

  const isTargetPage = useMemo(() => {
    if (!pageHighlightNode?.pages) return false;
    return (
      pageHighlightNode.pages.physical_start <= currentPage &&
      currentPage <= pageHighlightNode.pages.physical_end
    );
  }, [pageHighlightNode, currentPage]);

  // When user changes page, highlight the deepest node whose page range contains it.
  useEffect(() => {
    if (!documentTree) return;
    const node = findDeepestNodeForPage(documentTree.nodes, currentPage);
    const nodeId = node?.id ?? null;
    if (nodeId !== selectedNodeId) setSelectedNode(nodeId);

    if (nodeId) {
      const el = document.getElementById(`node-${nodeId}`);
      el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, documentTree, selectedNodeId]);

  const canPrev = currentPage > 1;
  const canNext = currentPage < totalPages;

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="text-xs text-slate-300">
          Page <span className="font-semibold text-slate-100">{currentPage}</span> /{" "}
          <span className="font-semibold text-slate-100">{totalPages}</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/40 hover:bg-slate-900 text-xs disabled:opacity-40"
            disabled={!canPrev}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Prev
          </button>
          <button
            className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/40 hover:bg-slate-900 text-xs disabled:opacity-40"
            disabled={!canNext}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </button>

          <div className="flex items-center gap-1 ml-2">
            <button
              className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/40 hover:bg-slate-900 text-xs"
              onClick={() => setZoom((z) => Math.max(0.6, +(z - 0.1).toFixed(2)))}
            >
              −
            </button>
            <span className="text-xs text-slate-300 w-12 text-center">{Math.round(zoom * 100)}%</span>
            <button
              className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/40 hover:bg-slate-900 text-xs"
              onClick={() => setZoom((z) => Math.min(2.5, +(z + 0.1).toFixed(2)))}
            >
              +
            </button>
            <button
              className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/40 hover:bg-slate-900 text-xs"
              onClick={() => setZoom(1.2)}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto bg-slate-950">
        {isTargetPage && <div className="h-1 bg-amber-500/80" />}

        <Document
          file={fileUrl}
          onLoadSuccess={({ numPages }) => {
            // Keep store aligned with actual PDF pages.
            if (numPages > 0) {
              setJobProgress(0, numPages, 0);
              if (currentPage > numPages) setCurrentPage(numPages);
            }
          }}
          onLoadError={(err) => {
            // Keep this visible in the UI; react-pdf errors are otherwise opaque.
            // eslint-disable-next-line no-console
            console.error("Failed to load PDF", err);
          }}
          loading={<div className="p-6 text-sm text-slate-400">Loading PDF…</div>}
          error={
            <div className="p-6 text-sm text-red-400">
              Failed to load PDF. If this persists, try re-uploading the file.
            </div>
          }
        >
          <div className="flex justify-center py-4">
            <Page pageNumber={currentPage} scale={zoom} />
          </div>
        </Document>
      </div>
    </div>
  );
}
