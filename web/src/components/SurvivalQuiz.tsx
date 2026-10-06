import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Check,
  ChevronLeft,
  ChevronRight,
  Clock,
  Play,
  RotateCcw,
  Skull,
  Sparkles,
  Trophy,
  X,
} from "lucide-react";
import type { Persona, PersonasFile } from "../types";
import { fireConfetti } from "./Celebration";

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
    // private mode: the quiz just won't survive a reload
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
    <div className="border border-line bg-white px-3 py-2">
      <div className="micro-label text-faint">{label}</div>
      <div className="mt-0.5 text-base font-medium text-ink">{value}</div>
    </div>
  );
}

function outcomeLabel(value: 0 | 1): string {
  return value === 1 ? "Survived" : "Perished";
}

const TOP_SCORE_RATIO = 0.8;

type ScoreBand = "high" | "middle" | "low";

function scoreBand(correct: number, total: number): ScoreBand {
  if (total > 0 && correct / total >= TOP_SCORE_RATIO) return "high";
  if (total > 0 && correct / total >= 0.5) return "middle";
  return "low";
}

const SCORE_COPY: Record<ScoreBand, { headline: string; note: string }> = {
  high: {
    headline: "Outstanding. Your gut read the 1912 patterns well.",
    note:
      "You caught the same signals the model learns: women and children first, and first class first. The fairness question is why survival depended on them.",
  },
  middle: {
    headline: "Solid effort. You caught some of the patterns.",
    note:
      "Your gut found some signals, like women and children first, and missed others. The model learns the same signals from 891 records. The fairness question is why survival depended on them.",
  },
  low: {
    headline: "Tricky, right? The Titanic did not follow simple rules.",
    note:
      "Even the model misses some passengers. The strongest signal in the data was women and children first. The fairness question is why survival depended on sex and class at all.",
  },
};

function modelComparison(
  score: number,
  modelHits: number,
  total: number,
): string {
  if (score > modelHits) {
    return `The workshop model got ${modelHits} / ${total} on these same passengers. You beat the model.`;
  }
  if (score === modelHits) {
    return `The workshop model also got ${modelHits} / ${total} on these same passengers. You matched the model.`;
  }
  return `The workshop model got ${modelHits} / ${total} on these same passengers. It had 891 records to learn from, so it had a head start.`;
}

/**
 * End-of-run carousel: one card per passenger, marking each call right or
 * wrong and comparing it with the model's guess.
 */
function ResultCarousel({
  personas,
  answers,
}: {
  personas: Persona[];
  answers: Answer[];
}) {
  const [slide, setSlide] = useState(0);
  const total = personas.length;
  const clamp = (n: number) => Math.min(Math.max(n, 0), total - 1);
  const answerFor = (id: string) => answers.find((answer) => answer.id === id);

  return (
    <div className="mt-5">
      <div className="mb-2 flex items-center justify-between">
        <div className="micro-label text-dim">Your run, card by card</div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSlide((s) => clamp(s - 1))}
            disabled={slide === 0}
            aria-label="Previous passenger"
            className="inline-flex h-8 w-8 items-center justify-center border border-line bg-white text-ink transition hover:border-black disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="font-mono text-sm text-dim">
            {slide + 1} / {total}
          </span>
          <button
            onClick={() => setSlide((s) => clamp(s + 1))}
            disabled={slide === total - 1}
            aria-label="Next passenger"
            className="inline-flex h-8 w-8 items-center justify-center border border-line bg-white text-ink transition hover:border-black disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="overflow-hidden border border-line bg-white">
        <div
          className="flex transition-transform duration-300 ease-out"
          style={{ transform: `translateX(-${slide * 100}%)` }}
        >
          {personas.map((p) => {
            const answer = answerFor(p.id);
            const correct = answer?.correct ?? false;
            const timedOut = answer ? answer.guess === null : false;
            return (
              <div key={p.id} className="min-w-full">
                <div className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:gap-6 sm:p-5">
                  <div className="w-full border border-line sm:w-40 sm:shrink-0">
                    <Portrait persona={p} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-white ${
                          correct ? "bg-ok" : "bg-err"
                        }`}
                      >
                        {correct ? (
                          <Check className="h-3.5 w-3.5" />
                        ) : (
                          <X className="h-3.5 w-3.5" />
                        )}
                        {timedOut ? "Timed out" : correct ? "Correct" : "Missed"}
                      </span>
                      <span className="micro-label text-faint">{p.title}</span>
                    </div>
                    <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
                      <div className="border border-line bg-[#fcfcfc] px-3 py-2">
                        <div className="micro-label text-faint">Your call</div>
                        <div className="mt-0.5 font-semibold text-ink">
                          {answer && answer.guess !== null
                            ? outcomeLabel(answer.guess)
                            : "No guess"}
                        </div>
                      </div>
                      <div className="border border-line bg-[#fcfcfc] px-3 py-2">
                        <div className="micro-label text-faint">Actually</div>
                        <div className="mt-0.5 font-semibold text-ink">
                          {outcomeLabel(p.actual_survived)}
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-dim">
                      The model gave {Math.round(p.model_probability * 100)}% (
                      {outcomeLabel(p.model_prediction)}).{" "}
                      {p.match
                        ? "It read this one correctly."
                        : "It missed this one too."}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-2 flex flex-wrap justify-center gap-1.5">
        {personas.map((p, i) => {
          const answer = answerFor(p.id);
          const correct = answer?.correct ?? false;
          const active = i === slide;
          return (
            <button
              key={p.id}
              onClick={() => setSlide(i)}
              aria-label={`Go to ${p.title}`}
              className={`h-2.5 w-6 transition ${
                correct ? "bg-ok" : "bg-err"
              } ${
                active
                  ? "ring-2 ring-black ring-offset-1"
                  : "opacity-60 hover:opacity-100"
              }`}
            />
          );
        })}
      </div>
    </div>
  );
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
  // The clock never runs until the student presses Start, including after a
  // reload that resumes a saved run.
  const [started, setStarted] = useState(false);

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
    if (!started || phase !== "guess" || !persona) return;
    setSeconds(TIMER_SECONDS);
    const interval = window.setInterval(() => {
      setSeconds((value) => Math.max(0, value - 1));
    }, 1000);
    return () => window.clearInterval(interval);
  }, [started, phase, index, persona]);

  useEffect(() => {
    if (started && phase === "guess" && seconds === 0) reveal(null);
  }, [started, seconds, phase, reveal]);

  useEffect(() => {
    if (answers.length > 0) persist(answers);
  }, [answers]);

  const begin = () => {
    setSeconds(TIMER_SECONDS);
    setStarted(true);
  };

  const next = () => {
    phaseRef.current = "guess";
    if (index + 1 < personas.length) {
      setIndex(index + 1);
      setPhase("guess");
    } else {
      setPhase("done");
      if (
        personas.length > 0 &&
        correctCount / personas.length >= TOP_SCORE_RATIO
      ) {
        fireConfetti();
      }
    }
  };

  const restart = () => {
    persist([]);
    setAnswers([]);
    setIndex(0);
    phaseRef.current = "guess";
    setPhase("guess");
    setSeconds(TIMER_SECONDS);
    setStarted(false);
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
    const copy = SCORE_COPY[scoreBand(correctCount, total)];
    return (
      <div className="border border-acc bg-tint-acc p-6 sm:p-8">
        <div className="flex items-center gap-4">
          <Trophy className="h-10 w-10 text-warn" />
          <div>
            <div className="text-2xl font-bold tracking-tight text-ink">
              Your guess score: {correctCount} / {total}
            </div>
            <div className="text-base text-dim">
              {modelComparison(correctCount, modelHits, total)}
            </div>
          </div>
        </div>
        <p className="mt-4 text-base font-semibold text-ink">{copy.headline}</p>
        <p className="mt-1 text-base leading-relaxed text-ink">{copy.note}</p>
        <ResultCarousel personas={personas} answers={answers} />
        <button
          onClick={restart}
          className="mt-5 inline-flex h-11 items-center gap-2 border border-line bg-white px-5 text-base font-semibold text-ink transition hover:border-black"
        >
          <RotateCcw className="h-5 w-5" />
          Play again
        </button>
      </div>
    );
  }

  const revealed = phase === "reveal" && lastAnswer;
  const progress = ((index + (revealed ? 1 : 0)) / personas.length) * 100;
  const timeRatio = seconds / TIMER_SECONDS;

  return (
    <div className="border border-line bg-white p-6 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <Sparkles className="h-6 w-6 text-acc" />
          <h3 className="text-xl font-bold tracking-tight text-ink sm:text-2xl">
            Survival challenge
          </h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-sm text-dim">
            {index + 1} / {personas.length}
          </span>
          <span className="border border-line bg-white px-3 py-1.5 font-mono text-sm font-semibold text-ink">
            Score {correctCount}
          </span>
        </div>
      </div>
      <p className="mt-1.5 text-base leading-relaxed text-dim">
        Read the passenger, then call it: did this person survive the Titanic?
      </p>

      <div className="mt-4 h-1.5 w-full bg-card2">
        <div
          className="h-full bg-black transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-5 grid gap-5 sm:grid-cols-[280px_1fr] lg:grid-cols-[400px_1fr] lg:gap-7">
        <div className="border border-line">
          <Portrait persona={persona} />
        </div>
        <div>
          <div className="text-2xl font-bold tracking-tight text-ink sm:text-3xl">
            {persona.title}
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2.5 sm:grid-cols-3">
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
            started ? (
              <div className="mt-5">
                <div className="flex items-center gap-2.5 text-sm text-dim">
                  <Clock className="h-4 w-4" />
                  <span className="font-mono text-base font-semibold text-ink">
                    {seconds}s to decide
                  </span>
                  <div className="ml-2 h-2 flex-1 bg-card2">
                    <div
                      className={`h-full transition-all duration-1000 ease-linear ${
                        timeRatio < 0.34 ? "bg-err" : "bg-acc"
                      }`}
                      style={{ width: `${timeRatio * 100}%` }}
                    />
                  </div>
                </div>
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => reveal(1)}
                    className="inline-flex h-12 flex-1 items-center justify-center gap-2.5 bg-ok px-7 text-lg font-semibold text-white transition hover:brightness-95"
                  >
                    <Check className="h-5 w-5" />
                    Survived
                  </button>
                  <button
                    onClick={() => reveal(0)}
                    className="inline-flex h-12 flex-1 items-center justify-center gap-2.5 bg-err px-7 text-lg font-semibold text-white transition hover:brightness-95"
                  >
                    <Skull className="h-5 w-5" />
                    Perished
                  </button>
                </div>
              </div>
            ) : (
              <div className="mt-5 border border-dashed border-line2 bg-card2/50 p-5">
                <div className="text-base font-semibold text-ink">
                  Ready? The clock starts when you do.
                </div>
                <p className="mt-1 text-sm leading-relaxed text-dim">
                  You get {TIMER_SECONDS} seconds for each passenger. Call it
                  before the timer runs out.
                </p>
                <button
                  onClick={begin}
                  className="mt-4 inline-flex h-12 items-center gap-2.5 bg-black px-7 text-lg font-semibold text-white transition hover:bg-[#27272a]"
                >
                  <Play className="h-5 w-5" />
                  Start the challenge
                </button>
              </div>
            )
          ) : (
            <div className="mt-5">
              <div
                className={`flex flex-wrap items-center gap-2.5 border p-4 ${
                  lastAnswer?.correct
                    ? "border-ok bg-tint-ok"
                    : "border-warn bg-tint-warn"
                }`}
              >
                {lastAnswer?.correct ? (
                  <Check className="h-5 w-5 text-ok" />
                ) : (
                  <X className="h-5 w-5 text-warn" />
                )}
                <span className="text-base font-semibold text-ink">
                  {lastAnswer?.guess === null
                    ? "Time’s up, "
                    : lastAnswer?.correct
                      ? "You nailed it, "
                      : "Not this time, "}
                  this passenger <strong>{outcomeLabel(persona.actual_survived)}</strong>
                  .
                </span>
              </div>
              <div className="mt-3 text-base leading-relaxed text-dim">
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
                className="mt-4 inline-flex h-11 items-center gap-2 bg-black px-5 text-base font-semibold text-white transition hover:bg-[#333]"
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
