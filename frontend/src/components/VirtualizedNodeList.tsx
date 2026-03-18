import type { CSSProperties } from "react";
import { FixedSizeList } from "react-window";
import type { FlattenedNode } from "../utils/treeHelpers";

interface VirtualizedNodeListProps {
  height: number;
  rowHeight: number;
  nodes: FlattenedNode[];
  selectedNodeId: string | null;
  onSelect: (id: string) => void;
}

export function VirtualizedNodeList({
  height,
  rowHeight,
  nodes,
  selectedNodeId,
  onSelect
}: VirtualizedNodeListProps) {
  const Row = ({ index, style }: any) => {
    const item = nodes[index];
    const node = item.node;
    const isSelected = node.id === selectedNodeId;

    const rowStyle: CSSProperties = {
      ...style,
      paddingLeft: 8 + item.depth * 12
    };

    return (
      <div
        style={rowStyle}
        className={`flex cursor-pointer items-center gap-2 border-b border-slate-800/40 px-2 py-1 text-xs transition-colors ${
          isSelected ? "bg-slate-800/80 text-slate-50" : "hover:bg-slate-800/40"
        }`}
        onClick={() => onSelect(node.id)}
      >
        <span className="truncate">
          {node.title || node.text?.slice(0, 80) || "(untitled)"}
        </span>
      </div>
    );
  };

  return (
    <FixedSizeList
      height={height}
      itemCount={nodes.length}
      itemSize={rowHeight}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}

