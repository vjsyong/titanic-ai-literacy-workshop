import { useState } from "react";
import { ArrowRight, Trophy } from "lucide-react";
import { useWorkshopState } from "./api";
import type { DashboardState, ScriptState } from "./types";
import { Header } from "./components/Header";
import { TabBar } from "./components/TabBar";
import { StepCard } from "./components/StepCard";
import { PredictPanel } from "./components/PredictPanel";
import { ErrorBanner } from "./components/ErrorBanner";
import { useCompletionCelebration } from "./components/Celebration";

function StageCompleteBanner({
  script,
  nextTitle,
  onNextStage,
}: {
  script: ScriptState;
  nextTitle?: string;
  onNextStage?: () => void;
}) {
  const stageComplete = script.total > 0 && script.completed >= script.total;
  if (!(stageComplete && nextTitle && onNextStage)) return null;

  return (
    <div className="animate-rise flex flex-col gap-3 border border-ok bg-tint-ok p-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="text-lg font-bold tracking-tight text-ink">
          Stage complete — nice work!
        </div>
        <div className="text-sm text-dim">
          All {script.total} checkpoints are done. Ready for “{nextTitle}”?
        </div>
      </div>
      <button
        onClick={onNextStage}
        className="flex h-11 shrink-0 items-center gap-2 bg-black px-6 font-semibold text-white transition hover:bg-[#27272a]"
      >
        Continue to {nextTitle}
        <ArrowRight className="h-5 w-5" />
      </button>
    </div>
  );
}

function ScriptPanel({
  script,
  dashboard,
  allComplete,
  nextTitle,
  onNextStage,
}: {
  script: ScriptState;
  dashboard: DashboardState;
  allComplete: boolean;
  nextTitle?: string;
  onNextStage?: () => void;
}) {
  return (
    <section className="animate-rise space-y-3">
      <div className="border border-line bg-white p-5">
        <h2 className="text-[1.06rem] font-semibold tracking-tight text-ink">
          {script.title}
        </h2>
        <p className="mt-1 text-sm leading-relaxed text-dim">{script.intro}</p>
        <div className="mt-3 flex items-center gap-1.5">
          {Array.from({ length: script.total }).map((_, index) => (
            <span
              key={index}
              className={`h-2 w-2 ${
                index < script.completed ? "bg-black" : "bg-card2"
              }`}
            />
          ))}
          <span className="ml-2 font-mono text-xs text-dim">
            {script.completed} of {script.total} checkpoints completed
          </span>
        </div>
      </div>

      <StageCompleteBanner
        script={script}
        nextTitle={nextTitle}
        onNextStage={onNextStage}
      />

      {script.steps.map((step) => (
        <StepCard
          key={step.number}
          step={step}
          total={script.total}
          scriptId={script.id}
        />
      ))}

      {script.id === "dashboard" && <PredictPanel dashboard={dashboard} />}

      {/* Students read top-down: repeat the continue button at the bottom
          so it waits for them where they finished scrolling. */}
      <StageCompleteBanner
        script={script}
        nextTitle={nextTitle}
        onNextStage={onNextStage}
      />

      {allComplete && (
        <div className="animate-rise flex items-center gap-4 border border-ok bg-tint-ok p-5">
          <Trophy className="h-8 w-8 shrink-0 text-warn" />
          <div>
            <div className="text-lg font-bold tracking-tight text-ink">
              Workshop complete!
            </div>
            <div className="text-sm text-dim">
              You explored the data, trained a model, and interrogated it. Go
              build something of your own.
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default function App() {
  const { state, connected } = useWorkshopState();
  const [active, setActive] = useState(0);

  useCompletionCelebration(state?.all_complete ?? false);

  if (!state) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg text-dim">
        <div className="text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin border-2 border-line2 border-t-black" />
          Connecting to the workshop server…
        </div>
      </div>
    );
  }

  const done = state.scripts.reduce((sum, script) => sum + script.completed, 0);
  const total = state.scripts.reduce((sum, script) => sum + script.total, 0);
  const activeIndex = Math.min(active, Math.max(state.scripts.length - 1, 0));
  const activeScript = state.scripts[activeIndex];

  return (
    <div className="min-h-screen bg-bg">
      <Header done={done} total={total} connected={connected} />
      <main className="mx-auto max-w-6xl space-y-4 px-4 pb-24 pt-6">
        <ErrorBanner errors={state.import_errors} />
        <TabBar
          scripts={state.scripts}
          active={activeIndex}
          onChange={setActive}
        />
        {activeScript && (
          <ScriptPanel
            script={activeScript}
            dashboard={state.dashboard}
            allComplete={state.all_complete}
            nextTitle={state.scripts[activeIndex + 1]?.title}
            onNextStage={
              activeIndex + 1 < state.scripts.length
                ? () => {
                    setActive(activeIndex + 1);
                    window.scrollTo({ top: 0 });
                  }
                : undefined
            }
          />
        )}
        <footer className="pt-6 text-center text-xs text-faint">
          Titanic AI Literacy Workshop — the page refreshes by itself whenever
          a checkpoint is saved
        </footer>
      </main>
    </div>
  );
}
