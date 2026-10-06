import { useEffect, useRef, useState } from "react";
import { Dices, Sparkles } from "lucide-react";
import type {
  InputSpecItem,
  PredictResponse,
  RandomPassengerResponse,
} from "../types";
import { demoPredict, loadRandomPassenger } from "../api";
import { Control, VerdictCard } from "./PredictPanel";

// Every column the dataset ships with, so students can invent any passenger
// they like. The cosmetic columns ride along without changing the score.
const CONTROLS: InputSpecItem[] = [
  { label: "Passenger class", kind: "radio", choices: [1, 2, 3], value: 3 },
  { label: "Sex", kind: "radio", choices: ["female", "male"], value: "female" },
  { label: "Age", kind: "slider", min: 0, max: 80, step: 1, value: 29 },
  {
    label: "Siblings / spouses",
    kind: "slider",
    min: 0,
    max: 8,
    step: 1,
    value: 0,
  },
  {
    label: "Parents / children",
    kind: "slider",
    min: 0,
    max: 6,
    step: 1,
    value: 0,
  },
  { label: "Fare", kind: "slider", min: 0, max: 512, step: 1, value: 32 },
  {
    label: "Boarded at",
    kind: "radio",
    choices: ["Southampton", "Cherbourg", "Queenstown"],
    value: "Southampton",
  },
];

const TEXT_FIELDS = [
  { label: "Ticket", placeholder: "e.g. PC 17599" },
  { label: "Cabin", placeholder: "e.g. C85" },
  { label: "Passenger ID", placeholder: "e.g. 42" },
];

const DEFAULTS: Record<string, string | number> = {
  Name: "",
  "Passenger class": 3,
  Sex: "female",
  Age: 29,
  "Siblings / spouses": 0,
  "Parents / children": 0,
  Fare: 32,
  "Boarded at": "Southampton",
  Ticket: "",
  Cabin: "",
  "Passenger ID": "",
};

function TextField({
  label,
  value,
  placeholder,
  onChange,
}: {
  label: string;
  value: string | number;
  placeholder: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label className="text-sm font-medium text-dim">{label}</label>
      <input
        value={String(value ?? "")}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1.5 h-9 w-full border border-line bg-white px-3 text-sm text-ink outline-none focus:border-black"
      />
    </div>
  );
}

/**
 * Front-page playground: a live predictor below the quiz. Every field from
 * the dataset is editable, and a random real passenger can be loaded to test
 * whether the model gets their fate right.
 */
export function FrontPredictor() {
  const [values, setValues] = useState<Record<string, string | number>>({
    ...DEFAULTS,
  });
  const [response, setResponse] = useState<PredictResponse | null>(null);
  const [random, setRandom] = useState<RandomPassengerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const timer = useRef<number | null>(null);
  const seq = useRef(0);

  // Live feedback: re-score shortly after any control settles (debounced so
  // dragging a slider stays smooth).
  useEffect(() => {
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      const id = ++seq.current;
      setLoading(true);
      demoPredict(values).then((result) => {
        if (seq.current !== id) return;
        setResponse(result);
        setLoading(false);
      });
    }, 350);
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [values]);

  const update = (label: string, value: string | number) => {
    setRandom(null);
    setValues((previous) => ({ ...previous, [label]: value }));
  };

  const loadRandom = async () => {
    setLoading(true);
    const result = await loadRandomPassenger();
    if (result.ok && result.values) {
      setValues({ ...DEFAULTS, ...result.values });
      setRandom(result);
    } else if (!result.ok) {
      setResponse({ ok: false, error: result.error });
    }
    setLoading(false);
  };

  return (
    <section className="border border-line bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-acc" />
          <h3 className="text-lg font-bold tracking-tight text-ink">
            Did this person survive on the Titanic?
          </h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="micro-label text-faint">
            {loading ? "thinking..." : "live"}
          </span>
          <button
            onClick={loadRandom}
            disabled={loading}
            className="inline-flex h-9 items-center gap-2 border border-line bg-white px-4 text-sm font-semibold text-ink transition hover:border-black disabled:opacity-60"
          >
            <Dices className="h-4 w-4 text-acc" />
            Load a random real passenger
          </button>
        </div>
      </div>
      <p className="mt-1.5 text-sm leading-relaxed text-dim">
        Drag the controls and watch the survival chance change. The model
        learns from class, sex, age, family, fare, and boarding port only.
        Names, tickets, cabins and IDs ride along: a model cannot learn from
        unique labels.
      </p>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <TextField
            label="Name"
            value={values["Name"] ?? ""}
            placeholder="Type any name you like"
            onChange={(value) => update("Name", value)}
          />
        </div>
        {CONTROLS.map((item) => (
          <Control
            key={item.label}
            item={item}
            value={values[item.label] ?? item.value}
            onChange={(value) => update(item.label, value)}
          />
        ))}
        {TEXT_FIELDS.map((field) => (
          <TextField
            key={field.label}
            label={field.label}
            value={values[field.label] ?? ""}
            placeholder={field.placeholder}
            onChange={(value) => update(field.label, value)}
          />
        ))}
      </div>

      {response?.ok && <VerdictCard response={response} />}
      {response && !response.ok && (
        <div className="mt-4 border border-warn bg-tint-warn p-3 text-sm text-warn">
          {response.error}
        </div>
      )}

      {random?.ok && (
        <div className="mt-4 border border-line bg-[#fcfcfc] p-4">
          <div className="micro-label text-dim">
            Real passenger from the 1912 list
          </div>
          <p className="mt-1.5 text-sm leading-relaxed text-ink">
            <strong>{random.name}</strong> actually{" "}
            {random.actual_survived ? "survived" : "perished"}. The model
            guessed {random.model_prediction ? "survived" : "perished"} (
            {Math.round((random.model_probability ?? 0) * 100)}%).{" "}
            {random.match ? "It got this one right." : "It missed this one."}
          </p>
        </div>
      )}
    </section>
  );
}
