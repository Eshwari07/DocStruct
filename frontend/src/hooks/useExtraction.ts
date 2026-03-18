import { useCallback, useEffect, useRef } from "react";
import { deleteJob, getResult, pollStatus, uploadDocument } from "../api/client";
import { useDocStructStore } from "../store/useDocStructStore";

const POLL_INTERVAL_MS = 500;

export function useExtraction() {
  const {
    jobId,
    setUploadedFile,
    setJobId,
    setJobStatus,
    setResult,
    setErrorMessage,
    setJobProgress,
    reset,
  } = useDocStructStore();

  const activeJobRef = useRef<string | null>(null);
  const timeoutRef = useRef<number | null>(null);

  const pollUntilTerminal = useCallback(
    async (id: string) => {
      const status = await pollStatus(id);

      setJobProgress(
        status.progress_page,
        status.total_pages,
        status.elapsed_seconds
      );

      if (status.status === "processing") return false;

      if (status.status === "complete") {
        const res = await getResult(id);
        setResult(res.document, res.markdown, res.stats);
        setJobStatus("complete");
        setErrorMessage(null);
        return true;
      }

      // error
      setJobStatus("error");
      setErrorMessage(status.error ?? "Extraction failed.");
      return true;
    },
    [getResult, pollStatus, setErrorMessage, setJobStatus, setResult]
  );

  const startExtraction = useCallback(
    async (file: File) => {
      reset();
      setUploadedFile(file);
      setJobStatus("uploading");
      activeJobRef.current = null;

      try {
        const id = await uploadDocument(file);
        activeJobRef.current = id;
        setJobId(id);
        setJobStatus("processing");

        const tick = async () => {
          if (activeJobRef.current !== id) return;
          const done = await pollUntilTerminal(id);
          if (!done) {
            timeoutRef.current = window.setTimeout(tick, POLL_INTERVAL_MS);
          }
        };

        timeoutRef.current = window.setTimeout(tick, POLL_INTERVAL_MS);
      } catch (e) {
        setJobStatus("error");
        setErrorMessage(e instanceof Error ? e.message : "Failed to start extraction");
      }
    },
    [pollUntilTerminal, reset, setErrorMessage, setJobId, setJobStatus, setResult, setUploadedFile]
  );

  const cancelJob = useCallback(async () => {
    if (!jobId) return;
    activeJobRef.current = null;
    if (timeoutRef.current != null) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = null;
    try {
      await deleteJob(jobId);
    } finally {
      reset();
    }
  }, [deleteJob, jobId, reset]);

  useEffect(() => {
    return () => {
      activeJobRef.current = null;
      if (timeoutRef.current != null) window.clearTimeout(timeoutRef.current);
    };
  }, []);

  return { startExtraction, cancelJob };
}

