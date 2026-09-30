import { useEffect, useState } from "react";
import { Loader2, Lock, Sparkles } from "lucide-react";
import type {
  DashboardState,
  InputSpecItem,
  PredictResponse,
} from "../types";
import { predict } from "../api";
import { ChartBlock } from "./ChartBlock";

function Control({
  item,
  value,
  onChange,
}: {
  item: InputSpecItem;
  value: string | number;
  onChange: (value: string | number) => void;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-3">
        <label className="text-sm font-medium text-slate-600">{item.label}</label>
        {item.kind === "slider" && (
          <span className="text-xs font-semibold tabular-nums text-indigo-600">
            {value}
          </span>
        )}
      </div>
      {item.kind === "radio" ? (
        <div className="flex flex-wrap gap-1.5">
          {(item.choices ?? []).map((choice) => (
            <button
              key={String(choice)}
              onClick={() => onChange(choice)}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                value === choice
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {String(choice)}
            </button>
          ))}
        </div>
      ) : (
        <input
          type="range"
          min={item.min}
          max={item.max}
          step={item.step ?? 1}
          value={Number(value)}
          onChange={(event) => onChange(Number(event.target.value))}
        />
      )}
    </div>
  );
}

function VerdictCard({ response }: { response: PredictResponse }) {
  const probability =
    typeof response.probability === "number" ? response.probability : null;

  return (
    <div className="animate-rise mt-4 rounded-2xl border border-indigo-100 bg-indigo-50/50 p-5">
      <div className="flex flex-col items-center gap-5 sm:flex-row">
        {probability !== null && (
          <div className="w-56 shrink-0">
            <ChartBlock
              framed={false}
              heightClass="h-44 w-full"
              chart={{ kind: "gauge", value: probability * 100 }}
            />
          </div>
        )}
        <div className="text-center sm:text-left">
          {response.band && (
            <span className="inline-block rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-600 shadow-sm">
              {response.band}
            </span>
          )}
          <p className="mt-2 text-sm leading-relaxed text-slate-700">
            {response.text}
          </p>
        </div>
      </div>
    </div>
  );
}

export function PredictPanel({ dashboard }: { dashboard: DashboardState }) {
  const spec = dashboard.input_spec ?? [];
  const specJson = JSON.stringify(spec);

  const [values, setValues] = useState<Record<string, string | number>>({});
  const [response, setResponse] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const initial: Record<string, string | number> = {};
    for (const item of spec) initial[item.label] = item.value;
    setValues(initial);
    setResponse(null);
  }, [specJson]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!dashboard.predict_ready) {
    return (
      <div className="flex items-center gap-3 rounded-2xl border border-dashed border-slate-200 bg-white/60 px-4 py-6 text-slate-400">
        <Lock className="h-4 w-4 shrink-0" />
        <span className="text-sm font-medium">
          {spec.length > 0
            ? "The form is designed — the prediction wiring comes with checkpoint 3."
            : "The live passenger form appears after checkpoint 3 — keep going!"}
        </span>
      </div>
    );
  }

  const run = async () => {
    setLoading(true);
    const result = await predict(values);
    setResponse(result);
    setLoading(false);
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-indigo-500" />
        <h3 className="text-lg font-bold text-slate-800">
          Try your own imaginary passenger
        </h3>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {spec.map((item) => (
          <Control
            key={item.label}
            item={item}
            value={values[item.label] ?? item.value}
            onChange={(value) =>
              setValues((previous) => ({ ...previous, [item.label]: value }))
            }
          />
        ))}
      </div>

      <button
        onClick={run}
        disabled={loading}
        className="mt-5 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:opacity-60"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {loading ? "Asking the model…" : "Predict survival"}
      </button>

      {response && !response.ok && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          {response.error}
        </div>
      )}

      {response?.ok && <VerdictCard response={response} />}
    </div>
  );
}
