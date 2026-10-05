import {
  ArrowRight,
  FileCode2,
  MessageSquare,
  RefreshCw,
  TerminalSquare,
} from "lucide-react";

const STEPS = [
  {
    icon: MessageSquare,
    title: "You ask",
    body: "You type a plain-English request in the OpenCode chat — no code, no syntax.",
  },
  {
    icon: FileCode2,
    title: "The AI writes one gate",
    body: "It edits exactly one checkpoint inside 01/02/03 and nothing else.",
  },
  {
    icon: TerminalSquare,
    title: "It checks its work",
    body: "It runs python on the script and fixes any error before moving on.",
  },
  {
    icon: RefreshCw,
    title: "This page updates itself",
    body: "The server notices the saved file within a second and shows the result.",
  },
];

/** Demystifies the loop that powers the whole workshop. */
export function ProcessDiagram() {
  return (
    <div className="border border-line bg-white p-5">
      <div className="micro-label text-dim">What happens under the hood</div>
      <p className="mt-1 text-sm leading-relaxed text-dim">
        Every checkpoint follows the same four moves. Nothing is magic — and
        you never type code yourself.
      </p>
      <ol className="mt-4 grid gap-3 md:grid-cols-4">
        {STEPS.map((step, index) => {
          const Icon = step.icon;
          return (
            <li
              key={step.title}
              className="relative border border-line bg-[#fcfcfc] p-4"
            >
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center bg-black text-white">
                  <Icon className="h-4 w-4" />
                </span>
                <span className="micro-label text-faint">
                  Step {index + 1}
                </span>
              </div>
              <div className="mt-3 text-sm font-semibold text-ink">
                {step.title}
              </div>
              <p className="mt-1 text-xs leading-relaxed text-dim">
                {step.body}
              </p>
              {index < STEPS.length - 1 && (
                <ArrowRight className="absolute -right-2.5 top-1/2 hidden h-5 w-5 -translate-y-1/2 bg-white text-line2 md:block" />
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
