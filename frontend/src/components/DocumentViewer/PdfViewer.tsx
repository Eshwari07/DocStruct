import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { useDocStructStore } from "../../store/useDocStructStore";
import type { DocNode } from "../../types/docstruct";
import { findDeepestNodeForPage, findNodeById } from "../../utils/treeHelpers";

try {
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();
} catch {
  pdfjs.GlobalWorkerOptions.workerSrc =
    `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
}

interface PdfViewerProps {
  fileUrl: string;
}

export function PdfViewer({ fileUrl }: PdfViewerProps) {
  const {
    documentTree,
    currentPage,
    totalPages,
    progressPage,
    elapsedSeconds,
    setCurrentPage,
    selectedNodeId,
    setSelectedNode,
    setJobProgress
  } = useDocStructStore();

  const [zoom, setZoom] = useState(1.2);
  const [pdfNumPages, setPdfNumPages] = useState(0);
  // Used to create accurate-ish overall scroll height when we window render pages.
  const [pageHeightEstimate, setPageHeightEstimate] = useState(900);
  const currentPageWrapperRef = useRef<HTMLDivElement | null>(null);

  const windowRadius = 2; // render currentPage +/- 2
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const skipNextPdfScrollIntoViewRef = useRef(false);
  const currentPageRef = useRef(currentPage);
  const scrollRafRef = useRef<number | null>(null);

  useEffect(() => {
    currentPageRef.current = currentPage;
  }, [currentPage]);
  const pageHighlightNode: DocNode | null = useMemo(() => {
    if (!documentTree || !selectedNodeId) return null;
    return findNodeById(documentTree, selectedNodeId);
  }, [documentTree, selectedNodeId]);

  const isTargetPage = useMemo(() => {
    if (!pageHighlightNode?.pages) return false;
    return (
      currentPage === pageHighlightNode.pages.physical_start
    );
  }, [pageHighlightNode, currentPage]);

  // When user changes page, highlight the deepest node whose page range contains it.
  const selectedNodeIdRef = useRef(selectedNodeId);
  useEffect(() => {
    selectedNodeIdRef.current = selectedNodeId;
  }, [selectedNodeId]);

  useEffect(() => {
    if (!documentTree) return;
    const node = findDeepestNodeForPage(documentTree.nodes, currentPage);
    const nodeId = node?.id ?? null;

    if (nodeId !== selectedNodeIdRef.current) {
      setSelectedNode(nodeId);
    }

    if (nodeId) {
      document
        .getElementById(`node-${nodeId}`)
        ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // Keep the left preview in sync with the current page.
    // (The right panel element is already handled above.)
    if (pdfNumPages > 0 && !skipNextPdfScrollIntoViewRef.current) {
      document
        .getElementById(`pdf-page-${currentPage}`)
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      // Reset the skip flag once we've reacted to the update.
      skipNextPdfScrollIntoViewRef.current = false;
    }
  }, [currentPage, documentTree, pdfNumPages]); // selectedNodeId intentionally excluded

  useLayoutEffect(() => {
    // Measure wrapper height for a better placeholder estimate.
    if (!currentPageWrapperRef.current) return;
    const h = currentPageWrapperRef.current.getBoundingClientRect().height;
    if (h > 100) setPageHeightEstimate(h);
  }, [currentPage, zoom, pdfNumPages]);

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

      <div
        ref={scrollContainerRef}
        onScroll={() => {
          // Debounce via rAF: we only update currentPage at most once per frame.
          if (!scrollContainerRef.current) return;
          if (scrollRafRef.current != null) return;
          scrollRafRef.current = window.requestAnimationFrame(() => {
            scrollRafRef.current = null;
            const el = scrollContainerRef.current;
            if (!el) return;
            if (pdfNumPages <= 0) return;

            // Avoid division by zero.
            const estimate = Math.max(100, pageHeightEstimate);
            const approxPage = Math.floor(el.scrollTop / estimate) + 1;
            const nextPage = Math.min(pdfNumPages, Math.max(1, approxPage));

            if (nextPage !== currentPageRef.current) {
              // Prevent the "scrollIntoView" effect from fighting the user's scroll.
              skipNextPdfScrollIntoViewRef.current = true;
              setCurrentPage(nextPage);
            }
          });
        }}
        className="flex-1 overflow-y-auto overflow-x-auto bg-slate-950"
      >
        {isTargetPage && <div className="h-1 bg-amber-500/80" />}

        <Document
          file={fileUrl}
          onLoadSuccess={({ numPages }) => {
            setPdfNumPages(numPages);
            if (numPages > 0) {
              // Only update totalPages — do NOT reset progressPage/elapsed
              if (numPages !== totalPages) {
                setJobProgress(progressPage, numPages, elapsedSeconds);
              }
              if (currentPage > numPages) setCurrentPage(numPages);
            }
          }}
          onLoadError={(err) => console.error("Failed to load PDF", err)}
          loading={<div className="p-6 text-sm text-slate-400">Loading PDF…</div>}
          error={
            <div className="p-6 text-sm text-red-400">
              Failed to load PDF. Try re-uploading.
            </div>
          }
        >
          {(() => {
            const start = Math.max(1, currentPage - windowRadius);
            const end = Math.min(pdfNumPages, currentPage + windowRadius);
            const topSpacer = Math.max(0, (start - 1) * pageHeightEstimate);
            const bottomSpacer = Math.max(
              0,
              (pdfNumPages - end) * pageHeightEstimate
            );

            return (
              <div className="flex flex-col items-center pb-4">
                {topSpacer > 0 && (
                  <div style={{ height: topSpacer }} aria-hidden="true" />
                )}

                {Array.from({ length: end - start + 1 }, (_, idx) => start + idx).map(
                  (pageNumber) => (
                    <div
                      key={pageNumber}
                      id={`pdf-page-${pageNumber}`}
                      ref={pageNumber === currentPage ? currentPageWrapperRef : null}
                      className="w-full flex justify-center py-4"
                    >
                      <Page
                        pageNumber={pageNumber}
                        scale={zoom}
                        renderAnnotationLayer={true}
                        renderTextLayer={true}
                      />
                    </div>
                  )
                )}

                {bottomSpacer > 0 && (
                  <div style={{ height: bottomSpacer }} aria-hidden="true" />
                )}
              </div>
            );
          })()}
        </Document>
      </div>
    </div>
  );
}
