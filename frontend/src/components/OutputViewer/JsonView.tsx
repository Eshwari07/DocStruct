import { useEffect, useMemo, useRef, useState } from "react";
import { FixedSizeList } from "react-window";
import type { DocNode, DocumentTree } from "../../types/docstruct";
import { useDocStructStore } from "../../store/useDocStructStore";
import { flattenVisibleNodes } from "../../utils/treeHelpers";
import { NodeCard } from "./NodeCard";

function collectExpandableIds(nodes: DocNode[]): string[] {
  const ids: string[] = [];
  const visit = (n: DocNode) => {
    if (n.children.length > 0) ids.push(n.id);
    n.children.forEach(visit);
  };
  nodes.forEach(visit);
  return ids;
}

export function JsonView({ documentTree }: { documentTree: DocumentTree }) {
  const { expandedNodeIds, expandAll, collapseAll, toggleExpanded } = useDocStructStore();
  const selectedNodeId = useDocStructStore((s) => s.selectedNodeId);

  const [rawMode, setRawMode] = useState(false);

  const visibleNodes = useMemo(() => {
    if (rawMode) return [];
    return flattenVisibleNodes(documentTree.nodes, expandedNodeIds);
  }, [documentTree.nodes, expandedNodeIds, rawMode]);

  const shouldVirtualize = visibleNodes.length > 100;
  const rowHeight = 52;
  const listRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [listHeight, setListHeight] = useState(420);

  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    const ro = new ResizeObserver(() => {
      setListHeight(el.getBoundingClientRect().height);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    if (!shouldVirtualize) return;
    if (!selectedNodeId) return;
    const idx = visibleNodes.findIndex((n) => n.node.id === selectedNodeId);
    if (idx < 0) return;
    listRef.current?.scrollToItem(idx, "center");
  }, [selectedNodeId, shouldVirtualize, visibleNodes]);

  if (documentTree.nodes.length === 0) {
    return <div className="text-xs text-slate-400 p-3">No nodes extracted.</div>;
  }

  if (rawMode) {
    return (
      <div className="h-full overflow-auto p-4">
        <pre className="text-[11px] leading-relaxed text-slate-200 whitespace-pre-wrap">
          {JSON.stringify(documentTree, null, 2)}
        </pre>
      </div>
    );
  }

  const controls = (
    <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between gap-2">
      <div className="flex items-center gap-2">
        <button
          className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/30 hover:bg-slate-900 text-xs"
          onClick={expandAll}
        >
          Expand all
        </button>
        <button
          className="px-2 py-1 rounded-md border border-slate-700 bg-slate-900/30 hover:bg-slate-900 text-xs"
          onClick={collapseAll}
        >
          Collapse all
        </button>
      </div>
      <button
        className="text-xs text-slate-300 hover:text-slate-50 underline"
        onClick={() => setRawMode(true)}
      >
        Raw JSON
      </button>
    </div>
  );

  if (shouldVirtualize) {
    const Row = ({ index, style }: any) => {
      const item = visibleNodes[index];
      return (
        <div style={style}>
          <NodeCard node={item.node} />
        </div>
      );
    };

    return (
      <div className="h-full flex flex-col">
        {controls}
        <div ref={containerRef} className="flex-1">
          <FixedSizeList
            ref={listRef as any}
            height={listHeight}
            itemCount={visibleNodes.length}
            itemSize={rowHeight}
            width="100%"
          >
            {Row}
          </FixedSizeList>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {controls}
      <div className="flex-1 overflow-auto p-2 space-y-1">
        {visibleNodes.map((item) => (
          <NodeCard key={item.node.id} node={item.node} />
        ))}
      </div>
    </div>
  );
}

