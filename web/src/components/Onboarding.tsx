import { useEffect, useRef } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Compass,
  Database,
  Ship,
  Sparkles,
} from "lucide-react";
import type { PersonasFile } from "../types";
import { ProcessDiagram } from "./ProcessDiagram";
import { SetupGuide } from "./SetupGuide";
import { SurvivalQuiz } from "./SurvivalQuiz";

const STAGES = [
  {
    icon: Database,
    tag: "Stage 1",
    title: "Meet the data",
    body: "Open the real 1912 passenger list, spot its gaps, and find the patterns that decided who lived.",
  },
  {
    icon: BrainCircuit,
    tag: "Stage 2",
    title: "Train the model",
    body: "Turn those patterns into a simple model that guesses survival — then open the box and see what it learned.",
  },
  {
    icon: Compass,
    tag: "Stage 3",
    title: "Build the app",
    body: "Wire a live form that predicts any imaginary passenger, and end by interrogating whether the model is fair.",
  },
];

/**
 * The front page: frames the end state, shows the side-by-side setup, explains
 * the loop behind the workshop, and hooks students with the survival game
 * before they ever unlock a checkpoint.
 */
export function Onboarding({
  personas,
  onStart,
}: {
  personas: PersonasFile | null;
  onStart: () => void;
}) {
  const quizRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-4 px-4 pb-24 pt-6">
      <section className="border border-line bg-white p-6 sm:p-8">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center bg-black text-white">
            <Ship className="h-6 w-6" />
          </span>
          <span className="micro-label text-acc">
            Titanic AI Literacy Workshop
          </span>
        </div>
        <h1 className="mt-5 max-w-3xl text-3xl font-bold leading-tight tracking-tight text-ink sm:text-4xl">
          By the end of this session you will have built your own
          survival-predicting app.
        </h1>
        <p className="mt-3 max-w-3xl text-base leading-relaxed text-dim">
          You will meet 891 real passengers from 1912, train an AI model on
          their lives, and ship a web app that predicts any passenger you
          invent. No prior coding — you direct the AI, it does the typing.
        </p>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            onClick={onStart}
            className="inline-flex h-11 items-center gap-2 bg-black px-6 font-semibold text-white transition hover:bg-[#27272a]"
          >
            Start the workshop
            <ArrowRight className="h-5 w-5" />
          </button>
          <button
            onClick={() =>
              quizRef.current?.scrollIntoView({ behavior: "smooth" })
            }
            className="inline-flex h-11 items-center gap-2 border border-line bg-white px-5 font-semibold text-ink transition hover:border-black"
          >
            <Sparkles className="h-4 w-4 text-acc" />
            Try the survival challenge first
          </button>
        </div>
      </section>

      <div ref={quizRef}>
        {personas ? (
          <SurvivalQuiz data={personas} />
        ) : (
          <div className="border border-dashed border-line2 bg-white/60 p-5 text-sm text-faint">
            Loading the survival challenge…
          </div>
        )}
      </div>

      <section className="grid gap-3 md:grid-cols-3">
        {STAGES.map((stage) => {
          const Icon = stage.icon;
          return (
            <div key={stage.title} className="border border-line bg-white p-5">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center bg-tint-acc text-acc">
                  <Icon className="h-4.5 w-4.5" />
                </span>
                <span className="micro-label text-dim">{stage.tag}</span>
              </div>
              <div className="mt-3 font-semibold tracking-tight text-ink">
                {stage.title}
              </div>
              <p className="mt-1.5 text-sm leading-relaxed text-dim">
                {stage.body}
              </p>
            </div>
          );
        })}
      </section>

      <SetupGuide />
      <ProcessDiagram />

      <section className="flex flex-col items-start justify-between gap-4 border border-acc bg-tint-acc p-6 sm:flex-row sm:items-center">
        <div>
          <div className="text-lg font-bold tracking-tight text-ink">
            Ready? The AI is waiting at the other window.
          </div>
          <p className="mt-1 text-sm text-dim">
            Copy each prompt from this page straight into the OpenCode chat —
            never retype it.
          </p>
        </div>
        <button
          onClick={onStart}
          className="inline-flex h-11 shrink-0 items-center gap-2 bg-black px-6 font-semibold text-white transition hover:bg-[#27272a]"
        >
          Start the workshop
          <ArrowRight className="h-5 w-5" />
        </button>
      </section>
    </div>
  );
}
