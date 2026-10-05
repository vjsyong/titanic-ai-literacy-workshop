import { Fragment } from "react";
import {
  BrainCircuit,
  Cog,
  FileCode2,
  FileText,
  ListChecks,
  MessageSquare,
  MonitorPlay,
  Ruler,
  Save,
  SlidersHorizontal,
  TerminalSquare,
  Users,
} from "lucide-react";

// ---------------------------------------------------------------------------
// "Under the hood" explainer graphics.
//
// Each checkpoint gets a small animated flow: input icon -> operation ->
// output, with packets travelling along the arrows so students can literally
// watch the data being ported from one form into the next.
// ---------------------------------------------------------------------------

type Kind =
  | "chat"
  | "code"
  | "run"
  | "monitor"
  | "file"
  | "table"
  | "holes"
  | "words"
  | "numbers"
  | "checklist"
  | "split"
  | "scale"
  | "brain"
  | "chart"
  | "scatter"
  | "donut"
  | "gauge"
  | "save"
  | "form"
  | "people";

interface Node {
  kind: Kind;
  label: string;
  caption?: string;
}

const FLOWS: Record<string, { title: string; nodes: Node[] }> = {
  "eda:0": {
    title: "Proof of connection",
    nodes: [
      { kind: "chat", label: "Your greeting", caption: "you say hello" },
      { kind: "code", label: "01_eda.py", caption: "PAIRED = True" },
      { kind: "run", label: "python runs", caption: "no errors" },
      { kind: "monitor", label: "Page unlocks", caption: "checkpoint 1" },
    ],
  },
  "eda:1": {
    title: "A file becomes a table",
    nodes: [
      { kind: "file", label: "titanic.csv", caption: "the raw file" },
      { kind: "table", label: "DataFrame", caption: "891 rows × 12" },
      { kind: "holes", label: "Missing values", caption: "Age 177 · Cabin 687" },
    ],
  },
  "eda:2": {
    title: "Counting who lived",
    nodes: [
      { kind: "table", label: "Every passenger", caption: "all 891" },
      { kind: "chart", label: "Split by outcome", caption: "died vs lived" },
      { kind: "donut", label: "38% survived", caption: "342 people" },
      { kind: "people", label: "By sex", caption: "women 74% · men 19%" },
    ],
  },
  "eda:3": {
    title: "Wealth and age as patterns",
    nodes: [
      { kind: "table", label: "Every passenger" },
      { kind: "chart", label: "By ticket class", caption: "1st 63% · 3rd 24%" },
      { kind: "scatter", label: "Age vs survival", caption: "a design choice" },
    ],
  },
  "train:1": {
    title: "Words become numbers",
    nodes: [
      { kind: "words", label: "female / male", caption: "words" },
      { kind: "numbers", label: "0 / 1", caption: "digits" },
      { kind: "checklist", label: "Pick the clues", caption: "drop Name, ID" },
      { kind: "table", label: "X and y", caption: "features + target" },
    ],
  },
  "train:2": {
    title: "A fair exam, then one scale",
    nodes: [
      { kind: "table", label: "All passengers" },
      { kind: "split", label: "80 / 20", caption: "study vs exam" },
      { kind: "scale", label: "StandardScaler", caption: "fit on train only" },
    ],
  },
  "train:3": {
    title: "Learning the pattern",
    nodes: [
      { kind: "table", label: "Scaled training set" },
      { kind: "brain", label: "LogisticRegression", caption: "learns the pattern" },
      { kind: "gauge", label: "Test accuracy", caption: "~80%" },
    ],
  },
  "train:4": {
    title: "Open the box, then freeze it",
    nodes: [
      { kind: "brain", label: "Trained model" },
      { kind: "chart", label: "Coefficients", caption: "what it leaned on" },
      { kind: "save", label: "titanic_model.pkl", caption: "brains on disk" },
    ],
  },
  "dashboard:1": {
    title: "Waking the saved brain",
    nodes: [
      { kind: "save", label: "titanic_model.pkl", caption: "from Step 2" },
      { kind: "brain", label: "Awake model", caption: "predicts on demand" },
      { kind: "form", label: "Passenger form", caption: "radios + sliders" },
    ],
  },
  "dashboard:2": {
    title: "The pipeline on every click",
    nodes: [
      { kind: "form", label: "female", caption: "form words" },
      { kind: "numbers", label: "0", caption: "encode" },
      { kind: "scale", label: "Scaled", caption: "same scaler" },
      { kind: "gauge", label: "Verdict", caption: "chance + kind words" },
    ],
  },
  "dashboard:3": {
    title: "Stress-testing the mirror",
    nodes: [
      { kind: "people", label: "Imaginary passengers", caption: "vary one thing" },
      { kind: "brain", label: "The model", caption: "1912 patterns" },
      { kind: "chart", label: "Verdicts", caption: "table + probabilities" },
    ],
  },
};

// ---------------------------------------------------------------------------
// Mini visuals (hand-drawn so each node reads as a real object)
// ---------------------------------------------------------------------------

function MiniVisual({ kind }: { kind: Kind }) {
  const svg = "h-7 w-7 text-acc";

  switch (kind) {
    case "table":
      return (
        <svg viewBox="0 0 32 32" className={svg}>
          <rect x="3" y="5" width="26" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <line x1="3" y1="12" x2="29" y2="12" stroke="currentColor" strokeWidth="1.2" />
          <line x1="3" y1="19" x2="29" y2="19" stroke="currentColor" strokeWidth="1.2" />
          <line x1="12" y1="5" x2="12" y2="27" stroke="currentColor" strokeWidth="1.2" />
          <line x1="22" y1="5" x2="22" y2="27" stroke="currentColor" strokeWidth="1.2" />
        </svg>
      );
    case "holes":
      return (
        <svg viewBox="0 0 32 32" className="h-7 w-7 text-err">
          <rect x="3" y="5" width="26" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <line x1="3" y1="12" x2="29" y2="12" stroke="currentColor" strokeWidth="1.2" />
          <line x1="3" y1="19" x2="29" y2="19" stroke="currentColor" strokeWidth="1.2" />
          <line x1="12" y1="5" x2="12" y2="27" stroke="currentColor" strokeWidth="1.2" />
          <line x1="22" y1="5" x2="22" y2="27" stroke="currentColor" strokeWidth="1.2" />
          <rect x="13" y="20" width="8" height="6" fill="currentColor" />
          <rect x="23" y="6" width="5" height="5" fill="currentColor" opacity="0.7" />
        </svg>
      );
    case "chart":
      return (
        <svg viewBox="0 0 32 32" className={svg}>
          <rect x="4" y="16" width="5" height="12" fill="currentColor" />
          <rect x="12" y="9" width="5" height="19" fill="currentColor" />
          <rect x="20" y="13" width="5" height="15" fill="currentColor" />
          <line x1="2" y1="28" x2="30" y2="28" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      );
    case "scatter":
      return (
        <svg viewBox="0 0 32 32" className={svg}>
          <line x1="3" y1="28" x2="30" y2="28" stroke="currentColor" strokeWidth="1.4" />
          <line x1="3" y1="4" x2="3" y2="28" stroke="currentColor" strokeWidth="1.4" />
          <circle cx="9" cy="22" r="2" fill="currentColor" opacity="0.6" />
          <circle cx="15" cy="17" r="2" fill="currentColor" opacity="0.6" />
          <circle cx="13" cy="10" r="2" fill="currentColor" />
          <circle cx="22" cy="20" r="2" fill="currentColor" opacity="0.6" />
          <circle cx="25" cy="13" r="2" fill="currentColor" />
        </svg>
      );
    case "donut":
      return (
        <svg viewBox="0 0 32 32" className={svg}>
          <circle cx="16" cy="16" r="10" fill="none" stroke="currentColor" strokeWidth="5" opacity="0.25" />
          <circle
            cx="16" cy="16" r="10" fill="none" stroke="currentColor" strokeWidth="5"
            strokeDasharray="38 63" transform="rotate(-90 16 16)"
          />
        </svg>
      );
    case "gauge":
      return (
        <svg viewBox="0 0 32 32" className={svg}>
          <path d="M4 24 A12 12 0 0 1 28 24" fill="none" stroke="currentColor" strokeWidth="4" opacity="0.25" />
          <path d="M4 24 A12 12 0 0 1 19 13" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
          <circle cx="16" cy="24" r="2" fill="currentColor" />
        </svg>
      );
    case "split":
      return (
        <svg viewBox="0 0 32 32" className={svg}>
          <rect x="3" y="6" width="22" height="8" fill="currentColor" />
          <rect x="3" y="18" width="6" height="8" fill="currentColor" opacity="0.45" />
          <text x="12" y="25" fontSize="7" fill="currentColor" fontFamily="monospace">20%</text>
        </svg>
      );
    case "words":
      return <span className="font-serif text-lg italic leading-none text-acc">abc</span>;
    case "numbers":
      return <span className="font-mono text-base font-bold leading-none text-acc">0 1</span>;
    default:
      return null;
  }
}

function NodeIcon({ kind }: { kind: Kind }) {
  const custom = MiniVisual({ kind });
  if (custom) return custom;

  const iconProps = { className: "h-6 w-6 text-acc" };
  switch (kind) {
    case "chat":
      return <MessageSquare {...iconProps} />;
    case "code":
      return <FileCode2 {...iconProps} />;
    case "run":
      return <TerminalSquare {...iconProps} />;
    case "monitor":
      return <MonitorPlay {...iconProps} />;
    case "file":
      return <FileText {...iconProps} />;
    case "checklist":
      return <ListChecks {...iconProps} />;
    case "scale":
      return <Ruler {...iconProps} />;
    case "brain":
      return <BrainCircuit {...iconProps} />;
    case "save":
      return <Save {...iconProps} />;
    case "form":
      return <SlidersHorizontal {...iconProps} />;
    case "people":
      return <Users {...iconProps} />;
    default:
      return <Cog {...iconProps} />;
  }
}

function Connector({ index }: { index: number }) {
  return (
    <div className="behind-arrow" aria-hidden="true">
      <span className="behind-line" />
      <span className="behind-dot" style={{ animationDelay: `${index * 0.22}s` }} />
    </div>
  );
}

/**
 * A compact, animated diagram of the transformation a checkpoint performs.
 * Renders on the current and completed cards; nothing on locked ones.
 */
export function BehindTheScenes({
  scriptId,
  number,
  dimmed = false,
}: {
  scriptId: string;
  number: number;
  dimmed?: boolean;
}) {
  const flow = FLOWS[`${scriptId}:${number}`];
  if (!flow) return null;

  return (
    <div
      className={`border border-line bg-[#fcfcfc] p-3 ${
        dimmed ? "opacity-80" : ""
      }`}
    >
      <div className="micro-label mb-2 flex items-center gap-1.5 text-dim">
        <Cog className="h-3.5 w-3.5" />
        What's happening under the hood — {flow.title}
      </div>
      <div className="behind-flow flex items-center overflow-x-auto pb-1">
        {flow.nodes.map((node, index) => (
          <Fragment key={`${node.label}-${index}`}>
            {index > 0 && <Connector index={index} />}
            <div className="behind-node flex w-[6.4rem] shrink-0 flex-col items-center px-1 text-center">
              <div className="flex h-12 w-12 items-center justify-center border border-line bg-white">
                <NodeIcon kind={node.kind} />
              </div>
              <div className="mt-1 text-[0.72rem] font-semibold leading-tight text-ink">
                {node.label}
              </div>
              {node.caption && (
                <div className="text-[0.63rem] leading-tight text-faint">
                  {node.caption}
                </div>
              )}
            </div>
          </Fragment>
        ))}
      </div>
    </div>
  );
}
