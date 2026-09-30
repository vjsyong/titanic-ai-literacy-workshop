import { useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  Lock,
  Unlock,
} from "lucide-react";
import type { StepState } from "../types";
import { ResultBlocks } from "./ResultBlocks";

function PromptCard({ prompt }: { prompt: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard unavailable (rare on localhost)
    }
  };

  return (
    <div className="mt-4 rounded-xl border border-indigo-100 bg-indigo-50/70 p-4">
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-indigo-500">
        What to ask your AI Teaching Assistant
      </div>
      <p className="text-sm italic leading-relaxed text-slate-700">“{prompt}”</p>
      <button
        onClick={copy}
        className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-indigo-500"
      >
        {copied ? (
          <Check className="h-3.5 w-3.5" />
        ) : (
          <Copy className="h-3.5 w-3.5" />
        )}
        {copied ? "Copied!" : "Copy prompt"}
      </button>
    </div>
  );
}

function ErrorNote({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
      <div>
        <div className="font-semibold">This checkpoint hit a problem.</div>
        <div className="mt-0.5 font-mono text-xs">{text}</div>
        <div className="mt-1 text-xs">
          Ask your AI Teaching Assistant to fix it inside this gate.
        </div>
      </div>
    </div>
  );
}

export function StepCard({ step, total }: { step: StepState; total: number }) {
  if (step.status === "locked") {
    return (
      <div className="flex items-center gap-3 rounded-2xl border border-dashed border-slate-200 bg-white/60 px-4 py-3 text-slate-400">
        <Lock className="h-4 w-4" />
        <span className="text-sm font-medium">
          Step {step.number} of {total} — {step.title}
        </span>
        <span className="ml-auto text-xs">locked</span>
      </div>
    );
  }

  if (step.status === "current") {
    return (
      <div className="animate-soft-pulse rounded-2xl border-2 border-indigo-200 bg-white p-5 shadow-sm">
        <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-indigo-600">
          <Unlock className="h-4 w-4" />
          Checkpoint {step.number} of {total} — your turn
        </div>
        <h3 className="text-lg font-bold text-slate-800">{step.title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          {step.story}
        </p>
        <PromptCard prompt={step.prompt} />
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <CheckCircle2 className="h-5 w-5 text-emerald-500" />
        <h3 className="font-semibold text-slate-800">
          Step {step.number} of {total} — {step.title}
        </h3>
      </div>
      {step.error ? (
        <ErrorNote text={step.error} />
      ) : step.result ? (
        <ResultBlocks result={step.result} />
      ) : (
        <p className="text-sm text-slate-400">No output for this step.</p>
      )}
    </div>
  );
}
