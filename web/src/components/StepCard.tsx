import { useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronRight,
  ClipboardPaste,
  Compass,
  Copy,
  FileCode2,
  Lightbulb,
  Lock,
  Repeat,
  Unlock,
} from "lucide-react";
import type { StepState } from "../types";
import { ResultBlocks, Markdown } from "./ResultBlocks";
import { BehindTheScenes } from "./BehindTheScenes";

// ---------------------------------------------------------------------------
// Click-to-unlock: the reference prompt opens with one click. The unlock
// persists per step in localStorage.
// ---------------------------------------------------------------------------

const UNLOCK_KEY = "titanic-unlocked-references";

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
    // private mode etc.: the unlock just won't survive a reload
  }
}

function ReferencePanel({
  reference,
  alt,
}: {
  reference: string;
  alt?: string;
}) {
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
      {alt && (
        <div className="mt-3 border-t border-line pt-3">
          <span className="micro-label text-dim">Another way to ask</span>
          <p className="mt-1.5 text-sm italic leading-relaxed text-dim">
            “{alt}”
          </p>
        </div>
      )}
      <p className="mt-2 text-xs text-dim">
        Copy this prompt and paste it straight into the OpenCode chat window
        (the other side of your screen). Don't retype it. The page updates
        itself when the checkpoint is done.
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
  const [unlocked, setUnlocked] = useState(
    () => readUnlocks()[storageKey] === true,
  );

  const unlock = () => {
    persistUnlock(storageKey);
    setUnlocked(true);
  };

  return (
    <div className="mt-4">
      {/* Directional mission: never the verbatim prompt. */}
      <div className="border border-acc bg-tint-acc p-4">
        <div className="micro-label flex items-center gap-1.5 text-acc">
          <Lightbulb className="h-3.5 w-3.5" />
          Your mission
        </div>
        <p className="mt-1.5 text-sm leading-relaxed text-ink">
          {step.prompt}
        </p>
        {step.hints.length > 0 && (
          <div className="mt-2.5 border-t border-acc/20 pt-2.5">
            <div className="micro-label text-dim">Stuck? Think about…</div>
            <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm leading-relaxed text-[#3f3f46]">
              {step.hints.map((hint, index) => (
                <li key={index}>{hint}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="mt-3 flex items-start gap-2 border border-line bg-card2 px-3 py-2 text-xs leading-relaxed text-dim">
        <ClipboardPaste className="mt-0.5 h-3.5 w-3.5 shrink-0 text-acc" />
        <span>
          Read the mission, then{" "}
          <strong className="font-semibold text-ink">
            copy the prompt and paste it into the OpenCode chat
          </strong>
          . Don't type it out by hand. Your assistant does the work; you
          supply the intent.
        </span>
      </div>

      {unlocked ? (
        <div className="mt-3">
          <ReferencePanel reference={step.reference} alt={step.reference_alt} />
        </div>
      ) : (
        <div className="mt-3">
          <button
            onClick={unlock}
            className="h-9 bg-black px-4 text-sm font-semibold text-white transition hover:bg-[#333]"
          >
            <span className="inline-flex items-center gap-1.5">
              <Unlock className="h-3.5 w-3.5" />
              Unlock the reference prompt
            </span>
          </button>
        </div>
      )}
    </div>
  );
}

function CodeReveal({ code }: { code: string | null }) {
  if (!code) return null;

  return (
    <details className="group mt-3 border border-line bg-[#fcfcfc]">
      <summary className="flex cursor-pointer list-none select-none items-center gap-1.5 px-3 py-2 text-xs font-semibold text-dim transition hover:text-ink">
        <ChevronRight className="h-3.5 w-3.5 transition-transform group-open:rotate-90" />
        <FileCode2 className="h-3.5 w-3.5 text-acc" />
        See the code
        <span className="ml-auto font-normal text-faint">
          written by the AI assistant
        </span>
      </summary>
      <pre className="max-h-96 overflow-auto border-t border-line bg-white p-3 font-mono text-[0.72rem] leading-relaxed text-ink">
        <code>{code}</code>
      </pre>
    </details>
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
          Step {step.number} of {total}: {step.title}
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
          Checkpoint {step.number} of {total}: your turn
        </div>
        <h3 className="text-lg font-bold tracking-tight text-ink">
          {step.title}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-dim">{step.story}</p>
        {step.context && (
          <div className="mt-3">
            <div className="micro-label mb-1.5 text-dim">
              The raw material you're deciding about
            </div>
            <ResultBlocks result={step.context} />
          </div>
        )}
        <div className="mt-3">
          <BehindTheScenes scriptId={scriptId} number={step.number} />
        </div>
        <CodeReveal code={step.code} />
        <PromptWorkshop step={step} scriptId={scriptId} />
      </div>
    );
  }

  return (
    <div className="border border-line bg-white p-5">
      <div className="mb-2 flex items-center gap-2">
        <CheckCircle2 className="h-5 w-5 text-ok" />
        <h3 className="font-semibold tracking-tight text-ink">
          Step {step.number} of {total}: {step.title}
        </h3>
      </div>
      <div className="mb-3">
        <BehindTheScenes
          scriptId={scriptId}
          number={step.number}
          dimmed
        />
      </div>
      <CodeReveal code={step.code} />
      {step.error ? (
        <ErrorNote text={step.error} />
      ) : step.result ? (
        <ResultBlocks result={step.result} />
      ) : (
        <p className="text-sm text-faint">No output for this step.</p>
      )}
      {step.guide && !step.error && (
        <div className="mt-4 border border-ok bg-tint-ok p-4">
          <div className="micro-label flex items-center gap-1.5 text-ok">
            <Compass className="h-3.5 w-3.5" />
            What to notice: teacher's debrief
          </div>
          <div className="mt-1.5">
            <Markdown text={step.guide} />
          </div>
          {step.experiment && (
            <div className="mt-3 border-t border-ok/25 pt-3">
              <div className="micro-label flex items-center gap-1.5 text-ok">
                <Repeat className="h-3.5 w-3.5" />
                Try this next
              </div>
              <p className="mt-1.5 text-sm leading-relaxed text-ink">
                {step.experiment}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
