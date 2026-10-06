import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";
import type {
  MetricBlock,
  Result,
  ResultBlock,
  TableBlock,
} from "../types";
import { ChartBlock } from "./ChartBlock";

// ---------------------------------------------------------------------------
// Markdown
// ---------------------------------------------------------------------------

const markdownComponents: Components = {
  p: (props) => <p className="my-1.5 leading-relaxed" {...props} />,
  strong: (props) => (
    <strong className="font-semibold text-ink" {...props} />
  ),
  ul: (props) => <ul className="my-2 list-disc space-y-1 pl-5" {...props} />,
  ol: (props) => <ol className="my-2 list-decimal space-y-1 pl-5" {...props} />,
  code: (props) => (
    <code
      className="border border-line bg-card2 px-1 py-0.5 font-mono text-[0.85em]"
      {...props}
    />
  ),
  blockquote: (props) => (
    <blockquote
      className="my-2 border-l-[3px] border-line pl-3 text-dim"
      {...props}
    />
  ),
  a: (props) => (
    <a className="text-acc underline" target="_blank" {...props} />
  ),
  h1: (props) => <h1 className="mt-3 mb-1 text-xl font-bold" {...props} />,
  h2: (props) => <h2 className="mt-3 mb-1 text-lg font-bold" {...props} />,
  h3: (props) => <h3 className="mt-3 mb-1 text-base font-semibold" {...props} />,
  table: (props) => (
    <div className="my-3 overflow-x-auto border border-line">
      <table
        className="w-full border-collapse text-sm"
        {...props}
      />
    </div>
  ),
  th: (props) => (
    <th
      className="micro-label border-b border-line bg-[#fbfbfb] px-3 py-2 text-left text-dim"
      {...props}
    />
  ),
  td: (props) => <td className="border-b border-line px-3 py-2" {...props} />,
};

function Markdown({ text }: { text: string }) {
  return (
    <div className="text-[0.95rem] text-ink">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
        {text}
      </ReactMarkdown>
    </div>
  );
}

export { Markdown };

// ---------------------------------------------------------------------------
// Data table
// ---------------------------------------------------------------------------

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "-";
  if (typeof value === "number") {
    return Number.isInteger(value)
      ? value.toLocaleString()
      : value.toLocaleString(undefined, { maximumFractionDigits: 3 });
  }
  if (typeof value === "boolean") return value ? "yes" : "no";
  return String(value);
}

function DataTable({ columns, rows, total_rows, truncated }: TableBlock) {
  const numericColumns = columns.map((_, index) => {
    const values = rows.map((row) => row[index]);
    const numeric = values.filter((value) => typeof value === "number").length;
    return values.length > 0 && numeric / values.length > 0.6;
  });

  return (
    <div className="border border-line bg-white">
      <div className="max-h-96 overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="sticky top-0 z-10">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className="micro-label border-b border-line bg-[#fbfbfb] px-3 py-2 text-left text-dim"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={rowIndex % 2 === 0 ? "bg-white" : "bg-[#fcfcfc]"}
              >
                {row.map((value, columnIndex) => (
                  <td
                    key={columnIndex}
                    className={`border-b border-line px-3 py-1.5 text-ink ${
                      numericColumns[columnIndex]
                        ? "text-right font-mono text-[0.84rem] tabular-nums"
                        : ""
                    }`}
                  >
                    {formatCell(value)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {truncated && (
        <div className="border-t border-line bg-tint-warn px-3 py-1.5 text-xs text-warn">
          Showing the first {rows.length} of {total_rows.toLocaleString()} rows.
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Metric ring (animated headline number)
// ---------------------------------------------------------------------------

function useCountUp(target: number, duration = 1000) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let frame = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(target * eased);
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return value;
}

function MetricCard({ value, label, format }: MetricBlock) {
  const isPercent = format === "percent" || format === "probability";
  const scaled = isPercent ? value * 100 : value;
  const animated = useCountUp(scaled);

  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const fraction = Math.min(Math.max(value, 0), 1);
  const strokeColor =
    fraction > 0.75 ? "#067a46" : fraction > 0.5 ? "#0070f3" : "#b25e09";

  return (
    <div className="flex items-center gap-5 border border-line bg-white p-5">
      <svg width="104" height="104" viewBox="0 0 104 104" className="shrink-0">
        <circle
          cx="52"
          cy="52"
          r={radius}
          fill="none"
          stroke="#f0f0f0"
          strokeWidth="10"
        />
        <circle
          cx="52"
          cy="52"
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - fraction)}
          transform="rotate(-90 52 52)"
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(.22,1,.36,1)" }}
        />
        <text
          x="52"
          y="58"
          textAnchor="middle"
          className="fill-ink font-mono text-lg font-bold tabular-nums"
        >
          {animated.toFixed(isPercent ? 1 : 2)}
          {isPercent ? "%" : ""}
        </text>
      </svg>
      <div>
        <div className="text-base font-semibold text-ink">{label}</div>
        <div className="text-sm text-dim">the number the class earned</div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Dispatch
// ---------------------------------------------------------------------------

function SingleBlock({ block }: { block: ResultBlock }) {
  switch (block.type) {
    case "markdown":
      return <Markdown text={block.text} />;
    case "table":
      return <DataTable {...block} />;
    case "chart":
      return <ChartBlock chart={block.chart} />;
    case "metric":
      return <MetricCard {...block} />;
    default:
      return null;
  }
}

export function ResultBlocks({ result }: { result: Result }) {
  return (
    <div className="space-y-3">
      {result.blocks.map((block, index) => (
        <div
          key={index}
          className="animate-rise"
          style={{ animationDelay: `${Math.min(index * 60, 240)}ms` }}
        >
          <SingleBlock block={block} />
        </div>
      ))}
    </div>
  );
}

export { MetricCard };
