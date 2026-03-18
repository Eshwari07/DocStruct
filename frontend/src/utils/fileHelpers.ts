const ACCEPTED_FORMATS = [
  ".pdf",
  ".docx",
  ".doc",
  ".html",
  ".htm",
  ".md",
  ".markdown",
  ".epub",
  ".pptx",
  ".ppt",
  ".png",
  ".jpg",
  ".jpeg",
  ".tiff",
  ".tif"
];

const MAX_FILE_SIZE_MB = 500;

export function getFileExtension(name: string): string {
  const lastDot = name.lastIndexOf(".");
  if (lastDot === -1) return "";
  return name.slice(lastDot).toLowerCase();
}

export function isSupportedFile(file: File): boolean {
  const ext = getFileExtension(file.name);
  return ACCEPTED_FORMATS.includes(ext);
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = bytes / Math.pow(k, i);
  return `${value.toFixed(1)} ${units[i]}`;
}

export function validateFile(file: File): string | null {
  if (!isSupportedFile(file)) {
    return `Unsupported format: ${getFileExtension(file.name) || "<missing extension>"}. Accepted: ${ACCEPTED_FORMATS.join(
      ", "
    )}`;
  }

  const sizeMb = file.size / (1024 * 1024);
  if (sizeMb > MAX_FILE_SIZE_MB) {
    return `File too large: ${sizeMb.toFixed(1)}MB. Max: ${MAX_FILE_SIZE_MB}MB`;
  }

  return null;
}

