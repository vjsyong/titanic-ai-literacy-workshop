import { useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  Lightbulb,
  Lock,
  PenLine,
  Unlock,
} from "lucide-react";
import type { StepState } from "../types";
import { ResultBlocks } from "./ResultBlocks";

// ---------------------------------------------------------------------------
// Attempt-to-unlock: the reference prompt stays hidden until the student has
// written their own request. The unlock persists per step in localStorage.
// ---------------------------------------------------------------------------

const UNLOCK_KEY = "titanic-unlocked-references";
const MIN_WORDS = 6;
const MIN_CHARS = 30;

function readUnlocks(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(UNLOCK_KEY) ?? "{}") as Record<
      string,
      boolean
    >;
  } catch {
    return {};
  }
}

function persistUnlock(key: string) {
  try {
    const all = readUnlocks();
    all[key] = true;
    localStorage.setItem(UNLOCK_KEY, JSON.stringify(all));
  } catch {
    // private mode etc. — the unlock just won't survive a reload
  }
}

function isMeaningful(draft: string): boolean {
  const trimmed = draft.trim();
  const words = trimmed.split(/\s+/).filter(Boolean).length;
  return trimmed.length >= MIN_CHARS && words >= MIN_WORDS;
}

function ReferencePanel({ reference }: { reference: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(reference);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard unavailable (rare on localhost)
    }
  };

  return (
    <div className="border border-dashed border-line2 bg-[#fcfcfc] p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="micro-label text-dim">Reference prompt</span>
        <button
          onClick={copy}
          className="inline-flex h-7 items-center gap-1.5 border border-line bg-white px-2.5 text-xs font-medium hover:border-black"
        >
          {copied ? (
            <Check className="h-3.5 w-3.5 text-ok" />
          ) : (
            <Copy className="h-3.5 w-3.5" />
          )}
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <p className="mt-2 text-sm italic leading-relaxed text-ink">
        “{reference}”
      </p>
      <p className="mt-2 text-xs text-dim">
        Yours counts too — send whichever you prefer (or your own words).
      </p>
    </div>
  );
}

function PromptWorkshop({
  step,
  scriptId,
}: {
  step: StepState;
  scriptId: string;
}) {
  const storageKey = `${scriptId}:${step.number}`;
  const [draft, setDraft] = useState("");
  const [unlocked, setUnlocked] = useState(
    () => readUnlocks()[storageKey] === true,
  );

  const meaningful = isMeaningful(draft);
  const attempted = draft.trim().length > 0;

  const unlock = () => {
    if (!meaningful) return;
    persistUnlock(storageKey);
    setUnlocked(true);
  };

  return (
    <div className="mt-4">
      {/* Directional mission — never the verbatim prompt. */}
      <div className="border border-acc bg-tint-acc p-4">
        <div className="micro-label flex items-center gap-1.5 text-acc">
          <Lightbulb className="h-3.5 w-3.5" />
          Your mission
        </div>
        <p className="mt-1.5 text-sm leading-relaxed text-ink">
          {step.prompt}
        </p>
      </div>

      {unlocked ? (
        <div className="mt-3">
          <ReferencePanel reference={step.reference} />
        </div>
      ) : (
        <div className="mt-3">
          <div className="micro-label flex items-center gap-1.5 text-dim">
            <PenLine className="h-3.5 w-3.5" />
            Try it yourself first — write your own request
          </div>
          <textarea
            className="draft mt-2 min-h-[76px] w-full border border-line bg-white p-3 outline-none focus:border-black focus:shadow-[0_0_0_3px_rgba(0,112,243,0.35)]"
            placeholder={
              "What would YOU ask the assistant? e.g. “Look at the passenger list and …”"
            }
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
          />
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={unlock}
              disabled={!meaningful}
              className="h-9 bg-black px-4 text-sm font-semibold text-white transition hover:bg-[#333] disabled:cursor-not-allowed disabled:opacity-45"
            >
              <span className="inline-flex items-center gap-1.5">
                <Unlock className="h-3.5 w-3.5" />
                Unlock the reference prompt
              </span>
            </button>
            <span className="text-xs text-faint">
              {meaningful
                ? "Nice — that's a real request. Compare it with the reference."
                : attempted
                  ? "Almost — say what the assistant should do, with what, and how to show it (6+ words)."
                  : "Write at least a sentence — the assistant needs direction, not magic."}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function ErrorNote({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-2 border border-warn bg-tint-warn p-3 text-sm text-warn">
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

export function StepCard({
  step,
  total,
  scriptId,
}: {
  step: StepState;
  total: number;
  scriptId: string;
}) {
  if (step.status === "locked") {
    return (
      <div className="flex items-center gap-3 border border-dashed border-line2 bg-white/60 px-4 py-3 text-faint">
        <Lock className="h-4 w-4" />
        <span className="text-sm font-medium">
          Step {step.number} of {total} — {step.title}
        </span>
        <span className="micro-label ml-auto text-faint">locked</span>
      </div>
    );
  }

  if (step.status === "current") {
    return (
      <div className="animate-soft-pulse border-2 border-acc bg-white p-5">
        <div className="micro-label mb-1 flex items-center gap-2 text-acc">
          <Unlock className="h-4 w-4" />
          Checkpoint {step.number} of {total} — your turn
        </div>
        <h3 className="text-lg font-bold tracking-tight text-ink">
          {step.title}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-dim">{step.story}</p>
        <PromptWorkshop step={step} scriptId={scriptId} />
      </div>
    );
  }

  return (
    <div className="border border-line bg-white p-5">
      <div className="mb-2 flex items-center gap-2">
        <CheckCircle2 className="h-5 w-5 text-ok" />
        <h3 className="font-semibold tracking-tight text-ink">
          Step {step.number} of {total} — {step.title}
        </h3>
      </div>
      {step.error ? (
        <ErrorNote text={step.error} />
      ) : step.result ? (
        <ResultBlocks result={step.result} />
      ) : (
        <p className="text-sm text-faint">No output for this step.</p>
      )}
    </div>
  );
}
