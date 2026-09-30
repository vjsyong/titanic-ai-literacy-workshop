import { useState } from "react";
import { Trophy } from "lucide-react";
import { useWorkshopState } from "./api";
import type { DashboardState, ScriptState } from "./types";
import { Header } from "./components/Header";
import { TabBar } from "./components/TabBar";
import { StepCard } from "./components/StepCard";
import { PredictPanel } from "./components/PredictPanel";
import { ErrorBanner } from "./components/ErrorBanner";
import { useCompletionCelebration } from "./components/Celebration";

function ScriptPanel({
  script,
  dashboard,
  allComplete,
}: {
  script: ScriptState;
  dashboard: DashboardState;
  allComplete: boolean;
}) {
  return (
    <section className="animate-rise space-y-3">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-xl font-bold tracking-tight text-slate-800">
          {script.title}
        </h2>
        <p className="mt-1 text-sm leading-relaxed text-slate-600">
          {script.intro}
        </p>
        <div className="mt-3 flex items-center gap-1.5">
          {Array.from({ length: script.total }).map((_, index) => (
            <span
              key={index}
              className={`h-2.5 w-2.5 rounded-full ${
                index < script.completed ? "bg-teal-500" : "bg-slate-200"
              }`}
            />
          ))}
          <span className="ml-2 text-xs font-medium text-slate-500">
            {script.completed} of {script.total} checkpoints completed
          </span>
        </div>
      </div>

      {script.steps.map((step) => (
        <StepCard key={step.number} step={step} total={script.total} />
      ))}

      {script.id === "dashboard" && <PredictPanel dashboard={dashboard} />}

      {allComplete && (
        <div className="animate-rise flex items-center gap-4 rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 to-teal-50 p-5 shadow-sm">
          <Trophy className="h-8 w-8 shrink-0 text-amber-500" />
          <div>
            <div className="text-lg font-bold text-slate-800">
              Workshop complete!
            </div>
            <div className="text-sm text-slate-600">
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
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-slate-500">
        <div className="text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
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
    <div className="min-h-screen bg-slate-50">
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
          />
        )}
        <footer className="pt-6 text-center text-xs text-slate-400">
          Titanic AI Literacy Workshop — the page refreshes by itself whenever
          a checkpoint is saved
        </footer>
      </main>
    </div>
  );
}
