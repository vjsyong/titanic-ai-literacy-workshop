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
        <label className="text-sm font-medium text-dim">{item.label}</label>
        {item.kind === "slider" && (
          <span className="font-mono text-xs font-semibold text-acc">
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
              className={`h-8 border px-3 text-sm font-medium transition ${
                value === choice
                  ? "border-black bg-black text-white"
                  : "border-line bg-white text-[#3f3f46] hover:border-black hover:text-black"
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
    <div className="animate-rise mt-4 border border-acc bg-tint-acc p-5">
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
            <span className="micro-label inline-block border border-acc bg-white px-2 py-1 text-acc">
              {response.band}
            </span>
          )}
          <p className="mt-2 text-sm leading-relaxed text-ink">
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
      <div className="flex items-center gap-3 border border-dashed border-line2 bg-white/60 px-4 py-6 text-faint">
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
    <div className="border border-line bg-white p-5">
      <div className="mb-4 flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-acc" />
        <h3 className="text-lg font-bold tracking-tight text-ink">
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
        className="mt-5 inline-flex h-9 items-center gap-2 bg-black px-4 text-sm font-semibold text-white transition hover:bg-[#333] disabled:opacity-60"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {loading ? "Asking the model…" : "Predict survival"}
      </button>

      {response && !response.ok && (
        <div className="mt-4 border border-warn bg-tint-warn p-3 text-sm text-warn">
          {response.error}
        </div>
      )}

      {response?.ok && <VerdictCard response={response} />}
    </div>
  );
}
