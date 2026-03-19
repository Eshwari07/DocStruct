import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
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
    setJobProgress,
  } = useDocStructStore();

  const [zoom, setZoom] = useState(1.2);
  const [pdfNumPages, setPdfNumPages] = useState(0);

  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const pageRefsMap = useRef<Map<number, HTMLDivElement>>(new Map());
  const programmaticScrollRef = useRef(false);

  const currentPageRef = useRef(currentPage);
  useEffect(() => {
    currentPageRef.current = currentPage;
  }, [currentPage]);

  const selectedNodeIdRef = useRef(selectedNodeId);
  useEffect(() => {
    selectedNodeIdRef.current = selectedNodeId;
  }, [selectedNodeId]);

  // Track which page is most visible via IntersectionObserver
  const visiblePagesRef = useRef<Map<number, number>>(new Map());

  useEffect(() => {
    if (pdfNumPages === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const pageNum = Number((entry.target as HTMLElement).dataset.pageNum);
          if (!pageNum) continue;
          if (entry.isIntersecting) {
            visiblePagesRef.current.set(pageNum, entry.intersectionRatio);
          } else {
            visiblePagesRef.current.delete(pageNum);
          }
        }

        if (programmaticScrollRef.current) return;

        // Pick the page with the highest intersection ratio
        let bestPage = currentPageRef.current;
        let bestRatio = 0;
        for (const [pg, ratio] of visiblePagesRef.current) {
          if (ratio > bestRatio) {
            bestRatio = ratio;
            bestPage = pg;
          }
        }
        if (bestPage !== currentPageRef.current) {
          setCurrentPage(bestPage);
        }
      },
      {
        root: scrollContainerRef.current,
        threshold: [0, 0.25, 0.5, 0.75, 1.0],
      }
    );

    for (const [, el] of pageRefsMap.current) {
      observer.observe(el);
    }

    return () => observer.disconnect();
  }, [pdfNumPages, setCurrentPage]);

  // When currentPage changes via buttons or right-panel click, scroll the
  // PDF container to bring that page into view.
  const prevPageForScroll = useRef(currentPage);
  useEffect(() => {
    if (pdfNumPages === 0) return;
    if (currentPage === prevPageForScroll.current) return;
    prevPageForScroll.current = currentPage;

    const el = pageRefsMap.current.get(currentPage);
    if (!el) return;

    programmaticScrollRef.current = true;
    el.scrollIntoView({ behavior: "smooth", block: "start" });

    // Release the flag after the smooth scroll settles
    const timer = window.setTimeout(() => {
      programmaticScrollRef.current = false;
    }, 600);
    return () => window.clearTimeout(timer);
  }, [currentPage, pdfNumPages]);

  // Sync right panel: when the visible page changes, highlight the matching node.
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
  }, [currentPage, documentTree, setSelectedNode]);

  const pageHighlightNode: DocNode | null = useMemo(() => {
    if (!documentTree || !selectedNodeId) return null;
    return findNodeById(documentTree, selectedNodeId);
  }, [documentTree, selectedNodeId]);

  const isTargetPage = useMemo(() => {
    if (!pageHighlightNode?.pages) return false;
    return currentPage === pageHighlightNode.pages.physical_start;
  }, [pageHighlightNode, currentPage]);

  const setPageRef = useCallback(
    (pageNumber: number) => (el: HTMLDivElement | null) => {
      if (el) {
        pageRefsMap.current.set(pageNumber, el);
      } else {
        pageRefsMap.current.delete(pageNumber);
      }
    },
    []
  );

  const canPrev = currentPage > 1;
  const canNext = currentPage < totalPages;

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="text-xs text-slate-300">
          Page{" "}
          <span className="font-semibold text-slate-100">{currentPage}</span> /{" "}
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
            <span className="text-xs text-slate-300 w-12 text-center">
              {Math.round(zoom * 100)}%
            </span>
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

      {/* Scrollable PDF container — all pages rendered */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto overflow-x-auto bg-slate-950"
      >
        {isTargetPage && <div className="h-1 bg-amber-500/80" />}

        <Document
          file={fileUrl}
          onLoadSuccess={({ numPages }) => {
            setPdfNumPages(numPages);
            if (numPages > 0) {
              if (numPages !== totalPages) {
                setJobProgress(progressPage, numPages, elapsedSeconds);
              }
              if (currentPage > numPages) setCurrentPage(numPages);
            }
          }}
          onLoadError={(err) => console.error("Failed to load PDF", err)}
          loading={
            <div className="p-6 text-sm text-slate-400">Loading PDF…</div>
          }
          error={
            <div className="p-6 text-sm text-red-400">
              Failed to load PDF. Try re-uploading.
            </div>
          }
        >
          <div className="flex flex-col items-center pb-4">
            {Array.from({ length: pdfNumPages }, (_, i) => i + 1).map(
              (pageNumber) => (
                <div
                  key={pageNumber}
                  ref={setPageRef(pageNumber)}
                  data-page-num={pageNumber}
                  id={`pdf-page-${pageNumber}`}
                  className="w-full flex justify-center py-3"
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
          </div>
        </Document>
      </div>
    </div>
  );
}
