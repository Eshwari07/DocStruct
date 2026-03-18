import type { DocNode, DocumentTree } from "../types/docstruct";

export interface FlattenedNode {
  node: DocNode;
  depth: number;
}

export function flattenVisibleNodes(
  nodes: DocNode[],
  expanded: Set<string>
): FlattenedNode[] {
  const result: FlattenedNode[] = [];

  const walk = (node: DocNode, depth: number) => {
    result.push({ node, depth });
    if (node.children.length === 0) return;
    if (!expanded.has(node.id)) return;
    node.children.forEach((child) => walk(child, depth + 1));
  };

  nodes.forEach((n) => walk(n, n.depth));
  return result;
}

export function findNodeById(
  tree: DocumentTree | null,
  id: string | null
): DocNode | null {
  if (!tree || !id) return null;

  let found: DocNode | null = null;

  const visit = (node: DocNode) => {
    if (found) return;
    if (node.id === id) {
      found = node;
      return;
    }
    node.children.forEach(visit);
  };

  tree.nodes.forEach(visit);
  return found;
}

export function findNodeBySectionId(
  tree: DocumentTree | null,
  sectionId: string | null
): DocNode | null {
  if (!tree || !sectionId) return null;

  let found: DocNode | null = null;

  const visit = (node: DocNode) => {
    if (found) return;
    if (node.section_id === sectionId) {
      found = node;
      return;
    }
    node.children.forEach(visit);
  };

  tree.nodes.forEach(visit);
  return found;
}

export function getPrimaryPageForNode(node: DocNode | null): number | null {
  if (!node?.pages) return null;
  return node.pages.physical_start;
}

export function findDeepestNodeForPage(
  nodes: DocNode[],
  page: number | null
): DocNode | null {
  if (!nodes || page == null) return null;

  let best: DocNode | null = null;

  const walk = (node: DocNode) => {
    if (node.pages) {
      const { physical_start, physical_end } = node.pages;
      if (physical_start <= page && page <= physical_end) {
        if (!best || node.depth > best.depth) best = node;
      }
    }
    node.children.forEach(walk);
  };

  nodes.forEach(walk);
  return best;
}
