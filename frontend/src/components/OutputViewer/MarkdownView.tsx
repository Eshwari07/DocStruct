import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useDocStructStore } from "../../store/useDocStructStore";
import { findNodeBySectionId } from "../../utils/treeHelpers";
import type { DocNode } from "../../types/docstruct";
import { getAssetUrl } from "../../api/client";

function childrenToText(children: unknown): string {
  if (typeof children === "string") return children;
  if (Array.isArray(children)) return children.map(childrenToText).join("");
  if (children && typeof children === "object" && "props" in children) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return childrenToText((children as any).props?.children);
  }
  return "";
}

function extractSectionIdFromHeadingText(text: string): string | null {
  // Backend headings start with: "{section_id} · {title}".
  const m = text.match(/^\s*([0-9]+(?:\.[0-9]+)*)/);
  return m ? m[1] : null;
}

function Heading({
  level,
  children
}: {
  level: 1 | 2 | 3 | 4 | 5 | 6;
  children: React.ReactNode;
}) {
  const { documentTree, setSelectedNode, setCurrentPage } =
    useDocStructStore();

  const text = childrenToText(children);
  const sectionId = extractSectionIdFromHeadingText(text);

  const className =
    level === 1
      ? "text-2xl font-medium mt-6 mb-2 text-slate-200"
      : level === 2
        ? "text-xl font-medium mt-5 mb-2 text-slate-200"
        : "text-lg font-medium mt-4 mb-1.5 text-slate-200";

  const onClick = () => {
    if (!documentTree || !sectionId) return;
    const node: DocNode | null = findNodeBySectionId(documentTree, sectionId);
    if (!node) return;
    setSelectedNode(node.id);
    if (node.pages) setCurrentPage(node.pages.physical_start);
  };

  const Tag = `h${level}` as keyof JSX.IntrinsicElements;

  return (
    <Tag className={className} style={{ cursor: "pointer" }} onClick={onClick}>
      {children}
    </Tag>
  );
}

export function MarkdownView({ markdown }: { markdown: string }) {
  const jobId = useDocStructStore((s) => s.jobId);
  return (
    <div className="h-full overflow-auto p-4">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <Heading level={1}>{children}</Heading>,
          h2: ({ children }) => <Heading level={2}>{children}</Heading>,
          h3: ({ children }) => <Heading level={3}>{children}</Heading>,
          h4: ({ children }) => <Heading level={4}>{children}</Heading>,
          h5: ({ children }) => <Heading level={5}>{children}</Heading>,
          h6: ({ children }) => <Heading level={6}>{children}</Heading>,
          img: ({ src, alt }) => {
            const s = typeof src === "string" ? src : "";
            const resolved =
              jobId && s.startsWith("assets/") ? getAssetUrl(jobId, s) : s;
            // eslint-disable-next-line jsx-a11y/alt-text
            return (
              <img
                src={resolved}
                alt={alt ?? ""}
                className="max-w-full rounded-lg border border-slate-800"
              />
            );
          }
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}

