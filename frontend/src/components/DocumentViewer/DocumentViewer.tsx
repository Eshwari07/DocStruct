import { useMemo } from "react";
import { useDocStructStore } from "../../store/useDocStructStore";
import { getFileUrl } from "../../api/client";
import type { SourceFormat } from "../../types/docstruct";
import { PdfViewer } from "./PdfViewer";
import { HtmlViewer } from "./HtmlViewer";
import { GenericViewer } from "./GenericViewer";

export function DocumentViewer() {
  const { jobId, documentTree, uploadedFile } = useDocStructStore();

  const sourceFormat: SourceFormat | null = documentTree?.source_format ?? null;
  const fileUrl = useMemo(() => {
    if (!jobId) return null;
    return getFileUrl(jobId);
  }, [jobId]);

  if (!jobId || !documentTree || !fileUrl) {
    return (
      <div className="h-full flex flex-col justify-center items-center text-sm text-slate-400">
        Upload a document to preview it here.
      </div>
    );
  }

  if (sourceFormat === "pdf") {
    return <PdfViewer fileUrl={fileUrl} />;
  }

  if (sourceFormat === "html") {
    return <HtmlViewer fileUrl={fileUrl} />;
  }

  return <GenericViewer fileUrl={fileUrl} fileName={uploadedFile?.name ?? null} />;
}
