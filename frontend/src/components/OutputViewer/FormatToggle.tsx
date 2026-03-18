import { useDocStructStore } from "../../store/useDocStructStore";

export function FormatToggle() {
  const { outputFormat, setOutputFormat } = useDocStructStore();

  return (
    <div className="flex rounded-full border border-slate-700 p-0.5 w-fit bg-slate-900/20">
      <button
        className={`px-4 py-1.5 rounded-full text-sm transition-colors ${
          outputFormat === "json"
            ? "bg-purple-600 text-white"
            : "text-slate-400 hover:text-slate-200"
        }`}
        onClick={() => setOutputFormat("json")}
      >
        JSON
      </button>
      <button
        className={`px-4 py-1.5 rounded-full text-sm transition-colors ${
          outputFormat === "markdown"
            ? "bg-purple-600 text-white"
            : "text-slate-400 hover:text-slate-200"
        }`}
        onClick={() => setOutputFormat("markdown")}
      >
        Markdown
      </button>
    </div>
  );
}
