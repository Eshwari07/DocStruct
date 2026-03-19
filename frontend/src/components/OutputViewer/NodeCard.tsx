import type { DocNode } from "../../types/docstruct";
import { useDocStructStore } from "../../store/useDocStructStore";
import { getAssetUrl } from "../../api/client";

function confidenceClass(confidence: number) {
  if (confidence >= 0.8) return "bg-emerald-500/15 text-emerald-200 border-emerald-500/30";
  if (confidence >= 0.5) return "bg-amber-500/15 text-amber-200 border-amber-500/30";
  return "bg-rose-500/15 text-rose-200 border-rose-500/30";
}

export function NodeCard({ node }: { node: DocNode }) {
  const { selectedNodeId, setSelectedNode, setCurrentPage } = useDocStructStore();
  const jobId = useDocStructStore((s) => s.jobId);

  const hasChildren = node.children.length > 0;
  const isSelected = node.id === selectedNodeId;

  const isExpanded = useDocStructStore((s) => s.expandedNodeIds.has(node.id));
  const toggleExpanded = useDocStructStore((s) => s.toggleExpanded);

  const indent = 8 + node.depth * 12;
  const pageLabel = node.pages
    ? `p.${node.pages.physical_start}-${node.pages.physical_end}`
    : null;
  const snippet = (node.text || "").trim().replace(/\s+/g, " ").slice(0, 120);

  const tableCount = node.tables?.length ?? 0;
  const imageCount = node.images?.length ?? 0;

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
              {tableCount > 0 && (
                <span className="inline-flex items-center rounded-full bg-blue-500/15 border border-blue-500/30 px-1.5 py-0.5 text-[10px] font-medium text-blue-200 whitespace-nowrap">
                  {tableCount} table{tableCount > 1 ? "s" : ""}
                </span>
              )}
              {imageCount > 0 && (
                <span className="inline-flex items-center rounded-full bg-violet-500/15 border border-violet-500/30 px-1.5 py-0.5 text-[10px] font-medium text-violet-200 whitespace-nowrap">
                  {imageCount} img{imageCount > 1 ? "s" : ""}
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

      {/* Inline table previews when selected */}
      {isSelected && tableCount > 0 && (
        <div style={{ paddingLeft: indent + 32 }} className="space-y-3 pb-2">
          {node.tables.map((tbl) => (
            <div
              key={tbl.table_id}
              className="rounded-lg border border-slate-700 overflow-hidden"
            >
              <div className="px-3 py-1.5 bg-slate-800/60 text-[11px] text-slate-300 flex items-center gap-2">
                <span className="font-medium text-slate-100">
                  {tbl.caption || `Table ${tbl.table_id}`}
                </span>
                <span className="text-slate-500">p.{tbl.page}</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px] border-collapse">
                  <thead className="bg-slate-800/40">
                    <tr>
                      {tbl.headers.map((h, i) => (
                        <th
                          key={i}
                          className="px-2 py-1.5 text-left font-semibold text-slate-200 border-b border-slate-700 whitespace-nowrap"
                        >
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/30">
                    {tbl.rows.slice(0, 8).map((row, ri) => (
                      <tr key={ri} className="hover:bg-slate-800/30">
                        {row.map((cell, ci) => (
                          <td
                            key={ci}
                            className="px-2 py-1 text-slate-300 whitespace-nowrap"
                          >
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                    {tbl.rows.length > 8 && (
                      <tr>
                        <td
                          colSpan={tbl.headers.length}
                          className="px-2 py-1 text-center text-slate-500 text-[10px] italic"
                        >
                          … {tbl.rows.length - 8} more rows
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Inline image thumbnails when selected */}
      {isSelected && imageCount > 0 && (
        <div
          style={{ paddingLeft: indent + 32 }}
          className="flex flex-wrap gap-2 pb-2"
        >
          {node.images.map((img, idx) => {
            const src =
              jobId && img.path.startsWith("assets/")
                ? getAssetUrl(jobId, img.path)
                : img.path;
            return (
              <div key={idx} className="flex flex-col items-center gap-1">
                <img
                  src={src}
                  alt={img.label || img.caption || "image"}
                  className="max-h-24 max-w-[160px] rounded border border-slate-700 object-contain bg-white"
                />
                {(img.label || img.caption) && (
                  <span className="text-[10px] text-slate-400 max-w-[160px] truncate">
                    {img.label || img.caption}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
