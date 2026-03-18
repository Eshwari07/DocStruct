import axios from "axios";
import type {
  BackendExtractResponse,
  BackendJobStatusResponse,
  ExtractionResult
} from "../types/docstruct";

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  headers: {
    "X-Requested-With": "XMLHttpRequest"
  }
});

export async function uploadDocument(
  file: File,
  opts?: { ocr?: boolean; max_pages?: number | null }
): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  if (opts?.ocr != null) {
    formData.append("ocr", String(opts.ocr));
  }
  if (opts?.max_pages != null) {
    formData.append("max_pages", String(opts.max_pages));
  }

  const response = await client.post<BackendExtractResponse>("/extract", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });

  return response.data.job_id;
}

export async function pollStatus(jobId: string): Promise<BackendJobStatusResponse> {
  const response = await client.get<BackendJobStatusResponse>(
    `/status/${encodeURIComponent(jobId)}`
  );
  return response.data;
}

export async function getResult(jobId: string): Promise<ExtractionResult> {
  const response = await client.get<ExtractionResult>(
    `/result/${encodeURIComponent(jobId)}`
  );
  return response.data;
}

export function getFileUrl(jobId: string): string {
  return `${API_BASE_URL}/file/${encodeURIComponent(jobId)}`;
}

export function getAssetUrl(jobId: string, assetPath: string): string {
  const clean = assetPath.replace(/^\/+/, "");
  return `${API_BASE_URL}/asset/${encodeURIComponent(jobId)}/${clean}`;
}

export async function deleteJob(jobId: string): Promise<void> {
  await client.delete(`/job/${encodeURIComponent(jobId)}`);
}

