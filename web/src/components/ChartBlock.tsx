import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import type { ChartPayload } from "../types";

type Row = Record<string, unknown>;
type Option = Record<string, unknown>;

interface CommonOption {
  [key: string]: unknown;
  color: string[];
  animationDuration: number;
  animationEasing: string;
  textStyle: Record<string, unknown>;
  legend: Record<string, unknown>;
  tooltip: Record<string, unknown>;
}

export const PALETTE = [
  "#4f46e5",
  "#14b8a6",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#0ea5e9",
  "#84cc16",
  "#f43f5e",
];

const INK = "#1e293b";
const MUTED = "#64748b";
const GRID = "#e2e8f0";

const PERSON_ICON =
  "path://M12 4.5a3.75 3.75 0 1 1 0 7.5 3.75 3.75 0 0 1 0-7.5zm0 9c4.14 0 7.5 2.02 7.5 4.5V20a1 1 0 0 1-1 1h-13a1 1 0 0 1-1-1v-2c0-2.48 3.36-4.5 7.5-4.5z";

function rowsOf(chart: ChartPayload): Row[] {
  return chart.data ?? [];
}

function num(value: unknown): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function categories(chart: ChartPayload, key: string): string[] {
  const seen: string[] = [];
  for (const row of rowsOf(chart)) {
    const label = String(row[key]);
    if (!seen.includes(label)) seen.push(label);
  }
  return seen;
}

function seriesNames(chart: ChartPayload): string[] {
  if (chart.series?.length) return chart.series;
  if (Array.isArray(chart.y)) return chart.y;
  if (chart.y) return [chart.y];
  return [];
}

function firstKey(chart: ChartPayload): string {
  const first = rowsOf(chart)[0];
  return first ? Object.keys(first)[0] : "";
}

function commonOption(hasLegend: boolean): CommonOption {
  return {
    color: PALETTE,
    animationDuration: 700,
    animationEasing: "cubicOut",
    textStyle: { fontFamily: "inherit" },
    legend: hasLegend
      ? {
          bottom: 0,
          icon: "roundRect",
          itemWidth: 12,
          itemHeight: 8,
          textStyle: { color: MUTED },
        }
      : { show: false },
    tooltip: {
      confine: true,
      backgroundColor: "rgba(15, 23, 42, 0.92)",
      borderWidth: 0,
      textStyle: { color: "#f8fafc", fontSize: 12 },
    },
  };
}

function axesFor(
  chart: ChartPayload,
  cats: string[],
  horizontal: boolean,
  extraBottom: number,
  valueMax?: number,
): Option {
  const categoryAxis = {
    type: "category",
    data: cats,
    axisLabel: { color: MUTED, rotate: !horizontal && cats.length > 8 ? 30 : 0 },
    axisLine: { lineStyle: { color: GRID } },
    axisTick: { show: false },
  };
  const valueAxis: Record<string, unknown> = {
    type: "value",
    name: horizontal ? chart.x_label : chart.y_label,
    nameTextStyle: { color: MUTED, padding: [0, 0, 0, 4] },
    axisLabel: { color: MUTED },
    splitLine: { lineStyle: { color: GRID } },
  };
  if (valueMax !== undefined) valueAxis.max = valueMax;

  const grid = {
    left: 8,
    right: 16,
    top: 28,
    bottom: 8 + extraBottom,
    containLabel: true,
  };

  return horizontal
    ? { xAxis: valueAxis, yAxis: categoryAxis, grid }
    : { xAxis: categoryAxis, yAxis: valueAxis, grid };
}

function categoryChart(
  chart: ChartPayload,
  type: "bar" | "pictorial" | "line" | "area",
): Option {
  const rows = rowsOf(chart);
  if (!rows.length) return commonOption(false);

  const xKey = chart.x ?? firstKey(chart);
  const cats = categories(chart, xKey);
  const names = seriesNames(chart);
  const horizontal = !!chart.horizontal;
  const isLine = type === "line" || type === "area";
  const isPictorial = type === "pictorial";
  const diverging = !!chart.diverging;

  const valueAt = (category: string, name: string): number => {
    const row = rows.find((item) => String(item[xKey]) === category);
    return row ? num(row[name]) : 0;
  };

  const categoryTotals = cats.map((category) =>
    names.reduce((sum, name) => sum + valueAt(category, name), 0),
  );
  const maxTotal = Math.max(...categoryTotals, 1);

  const series = names.map((name, index) => {
    if (diverging && index === 0) {
      const values = cats.map((category) => valueAt(category, name));
      return {
        name,
        type: "bar",
        data: cats.map((category, position) => ({
          value: values[position],
          itemStyle: {
            color: values[position] >= 0 ? "#14b8a6" : "#ef4444",
            borderRadius: horizontal
              ? values[position] >= 0
                ? [0, 6, 6, 0]
                : [6, 0, 0, 6]
              : values[position] >= 0
                ? [6, 6, 0, 0]
                : [0, 0, 6, 6],
          },
        })),
        barMaxWidth: 22,
      };
    }

    const base: Option = {
      name,
      type: isLine ? "line" : isPictorial ? "pictorialBar" : "bar",
      data: cats.map((category) => valueAt(category, name)),
      itemStyle: isLine || isPictorial ? undefined : { color: PALETTE[index % PALETTE.length] },
      color: isLine ? PALETTE[index % PALETTE.length] : undefined,
      lineStyle: isLine ? { width: 3 } : undefined,
      smooth: isLine,
      symbolSize: isLine ? 7 : undefined,
      areaStyle: type === "area" ? { opacity: 0.18 } : undefined,
      barMaxWidth: !isLine && !isPictorial ? 34 : undefined,
      stack: chart.stacked ? "total" : undefined,
      emphasis: { focus: "series" },
      barCategoryGap: !isLine ? "25%" : undefined,
    };

    if (isPictorial) {
      return {
        ...base,
        type: "pictorialBar",
        symbol: PERSON_ICON,
        symbolRepeat: "fixed",
        symbolBoundingData: maxTotal,
        symbolPosition: "start",
        symbolClip: true,
        symbolMargin: 2,
        symbolSize: horizontal ? [15, 17] : [13, 15],
        itemStyle: { color: PALETTE[index % PALETTE.length] },
        barCategoryGap: "30%",
      };
    }

    if (!horizontal && !isLine && !chart.stacked && !diverging) {
      base.itemStyle = {
        color: PALETTE[index % PALETTE.length],
        borderRadius: [6, 6, 0, 0],
      };
    }
    return base;
  });

  const hasLegend = names.length > 1;
  return {
    ...commonOption(hasLegend),
    ...axesFor(
      chart,
      cats,
      horizontal,
      hasLegend ? 26 : 0,
      isPictorial ? Math.ceil(maxTotal * 1.08) : undefined,
    ),
    tooltip: { ...commonOption(hasLegend).tooltip, trigger: "axis" },
    series,
  };
}

function scatterChart(chart: ChartPayload): Option {
  const rows = rowsOf(chart);
  const xKey = chart.x ?? firstKey(chart);
  const yKey = Array.isArray(chart.y) ? chart.y[0] : (chart.y ?? "");
  const colorKey = chart.color;
  const sizeKey = chart.size;

  const groups = colorKey
    ? [...new Set(rows.map((row) => String(row[colorKey])))]
    : ["Points"];

  const series = groups.map((group, index) => ({
    name: group,
    type: "scatter",
    data: rows
      .filter((row) => !colorKey || String(row[colorKey]) === group)
      .map((row) => [
        num(row[xKey]),
        num(row[yKey]),
        sizeKey ? Math.max(num(row[sizeKey]), 1) : 1,
      ]),
    symbolSize: sizeKey
      ? (value: number[]) => Math.min(8 + Math.sqrt(value[2]) * 2.2, 34)
      : 11,
    itemStyle: {
      opacity: 0.72,
      color: colorKey ? PALETTE[index % PALETTE.length] : PALETTE[0],
    },
    emphasis: { focus: "series" },
  }));

  return {
    ...commonOption(groups.length > 1),
    grid: { left: 8, right: 20, top: 28, bottom: 44, containLabel: true },
    tooltip: { ...commonOption(groups.length > 1).tooltip, trigger: "item" },
    xAxis: {
      type: "value",
      name: chart.x_label ?? xKey,
      nameTextStyle: { color: MUTED },
      axisLabel: { color: MUTED },
      splitLine: { lineStyle: { color: GRID } },
      scale: true,
    },
    yAxis: {
      type: "value",
      name: chart.y_label ?? yKey,
      nameTextStyle: { color: MUTED },
      axisLabel: { color: MUTED },
      splitLine: { lineStyle: { color: GRID } },
      scale: true,
    },
    dataZoom: [
      { type: "inside" },
      {
        type: "slider",
        height: 16,
        bottom: 0,
        borderColor: GRID,
        fillerColor: "rgba(79, 70, 229, 0.12)",
        handleStyle: { color: "#6366f1" },
      },
    ],
    series,
  };
}

function pieChart(chart: ChartPayload): Option {
  const rows = rowsOf(chart);
  const nameKey = chart.x ?? firstKey(chart);
  const valueKey = Array.isArray(chart.y) ? chart.y[0] : (chart.y ?? "value");

  return {
    ...commonOption(false),
    tooltip: { ...commonOption(false).tooltip, trigger: "item" },
    series: [
      {
        type: "pie",
        radius: chart.kind === "donut" ? ["42%", "70%"] : ["0%", "68%"],
        center: ["50%", "52%"],
        data: rows.map((row) => ({
          name: String(row[nameKey]),
          value: num(row[valueKey]),
        })),
        itemStyle: { borderRadius: 8, borderColor: "#fff", borderWidth: 2 },
        label: { color: INK, formatter: "{b}\n{d}%" },
        animationType: "scale",
        animationEasing: "cubicOut",
      },
    ],
  };
}

function histogramChart(chart: ChartPayload): Option {
  const rows = rowsOf(chart);
  const key = chart.x ?? (Array.isArray(chart.y) ? chart.y[0] : (chart.y ?? firstKey(chart)));
  const values = rows.map((row) => num(row[key])).filter((value) => Number.isFinite(value));

  if (!values.length) return commonOption(false);

  const min = Math.min(...values);
  const max = Math.max(...values);
  const binCount = Math.max(chart.bins ?? 10, 2);
  const width = (max - min) / binCount || 1;
  const counts = new Array<number>(binCount).fill(0);
  for (const value of values) {
    const index = Math.min(Math.floor((value - min) / width), binCount - 1);
    counts[index] += 1;
  }
  const labels = counts.map(
    (_, index) =>
      `${(min + index * width).toFixed(1)}–${(min + (index + 1) * width).toFixed(1)}`,
  );

  return {
    ...commonOption(false),
    ...axesFor({ ...chart, y_label: chart.y_label ?? "Count" }, labels, false, 0),
    tooltip: { ...commonOption(false).tooltip, trigger: "axis" },
    series: [
      {
        type: "bar",
        data: counts.map((count, index) => ({
          value: count,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: PALETTE[index % PALETTE.length] },
              { offset: 1, color: "rgba(79, 70, 229, 0.25)" },
            ]),
            borderRadius: [5, 5, 0, 0],
          },
        })),
        barMaxWidth: 44,
      },
    ],
  };
}

function gaugeChart(chart: ChartPayload): Option {
  const value = Math.max(0, Math.min(100, num(chart.value)));
  const color = value < 33 ? "#f43f5e" : value < 66 ? "#f59e0b" : "#14b8a6";

  return {
    ...commonOption(false),
    series: [
      {
        type: "gauge",
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        progress: { show: true, width: 16, roundCap: true, itemStyle: { color } },
        axisLine: { lineStyle: { width: 16, color: [[1, "#eef2f7"]] } },
        pointer: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        anchor: { show: false },
        detail: {
          valueAnimation: true,
          formatter: (current: number) => `${Math.round(current)}%`,
          fontSize: 34,
          fontWeight: 700,
          color: INK,
          offsetCenter: [0, "-6%"],
        },
        title: { show: false },
        data: [{ value }],
      },
    ],
  };
}

function heatmapChart(chart: ChartPayload): Option {
  const rows = rowsOf(chart);
  const xKey = chart.x ?? "";
  const yKey = chart.y ? (Array.isArray(chart.y) ? chart.y[0] : chart.y) : "";
  const valueKey = chart.series?.[0] ?? "value";

  const xCats = categories(chart, xKey);
  const yCats = categories(chart, yKey);
  const data = rows.map((row) => [
    xCats.indexOf(String(row[xKey])),
    yCats.indexOf(String(row[yKey])),
    num(row[valueKey]),
  ]);
  const values = data.map((entry) => entry[2]);
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);

  return {
    ...commonOption(false),
    grid: { left: 8, right: 16, top: 16, bottom: 52, containLabel: true },
    tooltip: { ...commonOption(false).tooltip, trigger: "item" },
    xAxis: {
      type: "category",
      data: xCats,
      axisLabel: { color: MUTED },
      axisLine: { lineStyle: { color: GRID } },
      axisTick: { show: false },
    },
    yAxis: {
      type: "category",
      data: yCats,
      axisLabel: { color: MUTED },
      axisLine: { lineStyle: { color: GRID } },
      axisTick: { show: false },
    },
    visualMap: {
      min,
      max,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      itemWidth: 12,
      itemHeight: 90,
      textStyle: { color: MUTED },
      inRange: { color: ["#eef2ff", "#818cf8", "#4338ca"] },
    },
    series: [
      {
        type: "heatmap",
        data,
        label: { show: true, color: INK, fontSize: 11 },
        itemStyle: { borderRadius: 5, borderColor: "#fff", borderWidth: 2 },
        emphasis: {
          itemStyle: { shadowBlur: 8, shadowColor: "rgba(15, 23, 42, 0.25)" },
        },
      },
    ],
  };
}

export function buildChartOption(chart: ChartPayload): Option {
  switch (chart.kind) {
    case "bar":
      return categoryChart(chart, "bar");
    case "pictorial":
      return categoryChart(chart, "pictorial");
    case "line":
      return categoryChart(chart, "line");
    case "area":
      return categoryChart(chart, "area");
    case "scatter":
      return scatterChart(chart);
    case "pie":
    case "donut":
      return pieChart(chart);
    case "histogram":
      return histogramChart(chart);
    case "gauge":
      return gaugeChart(chart);
    case "heatmap":
      return heatmapChart(chart);
    default:
      return commonOption(false);
  }
}

export function ChartBlock({
  chart,
  framed = true,
  heightClass = "h-72 w-full sm:h-80",
}: {
  chart: ChartPayload;
  framed?: boolean;
  heightClass?: string;
}) {
  const container = useRef<HTMLDivElement>(null);
  const instance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!container.current) return;
    const chartInstance = echarts.init(container.current, undefined, {
      renderer: "canvas",
    });
    instance.current = chartInstance;
    const observer = new ResizeObserver(() => chartInstance.resize());
    observer.observe(container.current);
    return () => {
      observer.disconnect();
      chartInstance.dispose();
      instance.current = null;
    };
  }, []);

  useEffect(() => {
    instance.current?.setOption(buildChartOption(chart), true);
  }, [chart]);

  return (
    <div
      className={
        framed
          ? "rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
          : ""
      }
    >
      {chart.title && (
        <div className="mb-1 text-sm font-semibold text-slate-700">{chart.title}</div>
      )}
      <div ref={container} className={heightClass} />
    </div>
  );
}
