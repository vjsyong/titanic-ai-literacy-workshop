import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Check,
  Clock,
  RotateCcw,
  Skull,
  Sparkles,
  Trophy,
  X,
} from "lucide-react";
import type { Persona, PersonasFile } from "../types";

const TIMER_SECONDS = 15;
const STORAGE_KEY = "titanic-quiz-v1";

interface Answer {
  id: string;
  guess: 0 | 1 | null;
  correct: boolean;
}

function readSaved(): Answer[] {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
    return Array.isArray(raw) ? (raw as Answer[]) : [];
  } catch {
    return [];
  }
}

function persist(answers: Answer[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
  } catch {
    // private mode — the quiz just won't survive a reload
  }
}

function Portrait({ persona }: { persona: Persona }) {
  const [broken, setBroken] = useState(false);
  const initials = persona.title
    .replace(/^The\s+/, "")
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  if (broken) {
    return (
      <div className="flex aspect-square w-full items-center justify-center bg-[#f0ece4] text-3xl font-bold text-[#8a7b63]">
        {initials}
      </div>
    );
  }
  return (
    <img
      src={`/${persona.portrait}`}
      alt={`Portrait of ${persona.title}`}
      loading="lazy"
      className="aspect-square w-full object-cover"
      onError={() => setBroken(true)}
    />
  );
}

function Attribute({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-line bg-white px-2.5 py-1.5">
      <div className="micro-label text-faint">{label}</div>
      <div className="mt-0.5 text-sm font-medium text-ink">{value}</div>
    </div>
  );
}

function outcomeLabel(value: 0 | 1): string {
  return value === 1 ? "Survived" : "Perished";
}

export function SurvivalQuiz({ data }: { data: PersonasFile }) {
  const personas = useMemo(() => data.personas ?? [], [data]);

  const saved = useMemo(() => readSaved(), []);
  const [answers, setAnswers] = useState<Answer[]>(saved);
  const [index, setIndex] = useState(() =>
    Math.min(saved.length, personas.length),
  );
  const [phase, setPhase] = useState<"guess" | "reveal" | "done">(() =>
    saved.length >= personas.length && personas.length > 0 ? "done" : "guess",
  );
  const [seconds, setSeconds] = useState(TIMER_SECONDS);

  const persona = personas[index];
  const lastAnswer = answers[answers.length - 1];
  const correctCount = answers.filter((answer) => answer.correct).length;

  // A ref guard keeps reveal() idempotent even under React StrictMode's
  // double-invoked effects (which would otherwise score a passenger twice).
  const phaseRef = useRef(phase);
  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  const reveal = useCallback(
    (guess: 0 | 1 | null) => {
      if (phaseRef.current !== "guess") return;
      phaseRef.current = "reveal";
      setPhase("reveal");
      setAnswers((previous) => [
        ...previous,
        {
          id: persona.id,
          guess,
          correct: guess !== null && guess === persona.actual_survived,
        },
      ]);
    },
    [persona],
  );

  useEffect(() => {
    if (phase !== "guess" || !persona) return;
    setSeconds(TIMER_SECONDS);
    const interval = window.setInterval(() => {
      setSeconds((value) => Math.max(0, value - 1));
    }, 1000);
    return () => window.clearInterval(interval);
  }, [phase, index, persona]);

  useEffect(() => {
    if (phase === "guess" && seconds === 0) reveal(null);
  }, [seconds, phase, reveal]);

  useEffect(() => {
    if (answers.length > 0) persist(answers);
  }, [answers]);

  const next = () => {
    phaseRef.current = "guess";
    if (index + 1 < personas.length) {
      setIndex(index + 1);
      setPhase("guess");
    } else {
      setPhase("done");
    }
  };

  const restart = () => {
    persist([]);
    setAnswers([]);
    setIndex(0);
    phaseRef.current = "guess";
    setPhase("guess");
    setSeconds(TIMER_SECONDS);
  };

  if (personas.length === 0) {
    return (
      <div className="border border-dashed border-line2 bg-white/60 p-5 text-sm text-faint">
        The quiz roster (personas.json) is not available yet.
      </div>
    );
  }

  if (phase === "done") {
    const total = personas.length;
    const modelHits = data.classifier.persona_hits;
    return (
      <div className="border border-acc bg-tint-acc p-6">
        <div className="flex items-center gap-3">
          <Trophy className="h-7 w-7 text-warn" />
          <div>
            <div className="text-lg font-bold tracking-tight text-ink">
              Your guess score: {correctCount} / {total}
            </div>
            <div className="text-sm text-dim">
              The workshop model got {modelHits} / {total} on these same
              passengers — you were both working from the same 1912 patterns.
            </div>
          </div>
        </div>
        <p className="mt-3 text-sm leading-relaxed text-ink">
          Notice how often “women and children first” steered your gut. That is
          the exact signal the model learns — and the fairness question the
          workshop ends on.
        </p>
        <button
          onClick={restart}
          className="mt-4 inline-flex h-9 items-center gap-2 border border-line bg-white px-4 text-sm font-semibold text-ink transition hover:border-black"
        >
          <RotateCcw className="h-4 w-4" />
          Play again
        </button>
      </div>
    );
  }

  const revealed = phase === "reveal" && lastAnswer;
  const progress = ((index + (revealed ? 1 : 0)) / personas.length) * 100;
  const timeRatio = seconds / TIMER_SECONDS;

  return (
    <div className="border border-line bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-acc" />
          <h3 className="text-lg font-bold tracking-tight text-ink">
            Survival challenge
          </h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs text-dim">
            {index + 1} / {personas.length}
          </span>
          <span className="border border-line bg-white px-2 py-1 font-mono text-xs font-semibold text-ink">
            Score {correctCount}
          </span>
        </div>
      </div>
      <p className="mt-1 text-sm leading-relaxed text-dim">
        Read the passenger, then call it: did this person survive the Titanic?
      </p>

      <div className="mt-3 h-1 w-full bg-card2">
        <div
          className="h-full bg-black transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-[180px_1fr]">
        <div className="border border-line">
          <Portrait persona={persona} />
        </div>
        <div>
          <div className="text-lg font-bold tracking-tight text-ink">
            {persona.title}
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
            <Attribute label="Sex" value={persona.sex} />
            <Attribute label="Age" value={String(persona.age)} />
            <Attribute label="Ticket class" value={`${persona.pclass}`} />
            <Attribute
              label="Family aboard"
              value={`${persona.sibsp} sib/spouse · ${persona.parch} par/child`}
            />
            <Attribute label="Fare" value={`£${persona.fare}`} />
            <Attribute label="Boarded" value={persona.embarked} />
          </div>

          {phase === "guess" ? (
            <div className="mt-4">
              <div className="flex items-center gap-2 text-xs text-dim">
                <Clock className="h-3.5 w-3.5" />
                <span className="font-mono">
                  {seconds}s to decide
                </span>
                <div className="ml-2 h-1.5 flex-1 bg-card2">
                  <div
                    className={`h-full transition-all duration-1000 ease-linear ${
                      timeRatio < 0.34 ? "bg-err" : "bg-acc"
                    }`}
                    style={{ width: `${timeRatio * 100}%` }}
                  />
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-3">
                <button
                  onClick={() => reveal(1)}
                  className="inline-flex h-10 items-center gap-2 bg-ok px-5 font-semibold text-white transition hover:brightness-95"
                >
                  <Check className="h-4 w-4" />
                  Survived
                </button>
                <button
                  onClick={() => reveal(0)}
                  className="inline-flex h-10 items-center gap-2 bg-black px-5 font-semibold text-white transition hover:bg-[#333]"
                >
                  <Skull className="h-4 w-4" />
                  Perished
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-4">
              <div
                className={`flex flex-wrap items-center gap-2 border p-3 ${
                  lastAnswer?.correct
                    ? "border-ok bg-tint-ok"
                    : "border-warn bg-tint-warn"
                }`}
              >
                {lastAnswer?.correct ? (
                  <Check className="h-4 w-4 text-ok" />
                ) : (
                  <X className="h-4 w-4 text-warn" />
                )}
                <span className="text-sm font-semibold text-ink">
                  {lastAnswer?.guess === null
                    ? "Time’s up — "
                    : lastAnswer?.correct
                      ? "You nailed it — "
                      : "Not this time — "}
                  this passenger <strong>{outcomeLabel(persona.actual_survived)}</strong>
                  .
                </span>
              </div>
              <div className="mt-2 text-sm text-dim">
                The model gave them a{" "}
                <strong className="font-mono text-ink">
                  {Math.round(persona.model_probability * 100)}%
                </strong>{" "}
                survival chance ({outcomeLabel(persona.model_prediction)}).{" "}
                {persona.match
                  ? "It read this one correctly."
                  : "Even the model missed this one."}
              </div>
              <button
                onClick={next}
                className="mt-3 inline-flex h-9 items-center gap-2 bg-black px-4 text-sm font-semibold text-white transition hover:bg-[#333]"
              >
                {index + 1 < personas.length ? "Next passenger" : "See your score"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
