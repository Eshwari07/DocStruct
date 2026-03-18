import type { DocNode } from "../../types/docstruct";
import { useDocStructStore } from "../../store/useDocStructStore";

function confidenceClass(confidence: number) {
  if (confidence >= 0.8) return "bg-emerald-500/15 text-emerald-200 border-emerald-500/30";
  if (confidence >= 0.5) return "bg-amber-500/15 text-amber-200 border-amber-500/30";
  return "bg-rose-500/15 text-rose-200 border-rose-500/30";
}

export function NodeCard({ node }: { node: DocNode }) {
  const { selectedNodeId, setSelectedNode, setCurrentPage } = useDocStructStore();

  const hasChildren = node.children.length > 0;
  const isSelected = node.id === selectedNodeId;

  const isExpanded = useDocStructStore((s) => s.expandedNodeIds.has(node.id));
  const toggleExpanded = useDocStructStore((s) => s.toggleExpanded);

  const indent = 8 + node.depth * 12;
  const pageLabel = node.pages
    ? `p.${node.pages.physical_start}-${node.pages.physical_end}`
    : null;
  const snippet = (node.text || "").trim().replace(/\s+/g, " ").slice(0, 120);

  return (
    <div className="space-y-1">
      <div
        style={{ paddingLeft: indent }}
        className={`flex items-center gap-2 py-1.5 px-2 rounded-md border transition ${
          isSelected
            ? "bg-slate-800/90 border-slate-700"
            : "bg-transparent border-transparent hover:bg-slate-800/40"
        }`}
      >
        {hasChildren ? (
          <button
            type="button"
            aria-label={isExpanded ? "Collapse node" : "Expand node"}
            onClick={(e) => {
              e.stopPropagation();
              toggleExpanded(node.id);
            }}
            className="w-6 h-6 rounded flex items-center justify-center hover:bg-slate-800/60 transition"
          >
            <span
              className={`inline-block transform transition ${
                isExpanded ? "rotate-90" : "rotate-0"
              }`}
            >
              {"›"}
            </span>
          </button>
        ) : (
          <div className="w-6 h-6" />
        )}

        <button
          type="button"
          onClick={() => {
            setSelectedNode(node.id);
            if (node.pages) setCurrentPage(node.pages.physical_start);
          }}
          className="flex-1 min-w-0 text-left"
        >
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2 min-w-0">
            <span className="truncate text-xs font-medium text-slate-100">
              {node.title || node.text || "(untitled)"}
            </span>
            {pageLabel && (
              <span className="text-[11px] text-slate-400 whitespace-nowrap">
                {pageLabel}
              </span>
            )}
            </div>
            {snippet && node.title ? (
              <div className="truncate text-[11px] text-slate-400">{snippet}</div>
            ) : null}
          </div>
        </button>

        <span
          className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold ${confidenceClass(
            node.confidence
          )}`}
          title={`Confidence: ${node.confidence}`}
        >
          {Math.round(node.confidence * 100)}%
        </span>
      </div>

      {/* Children are rendered by the parent list (flattened visible nodes). */}
    </div>
  );
}

