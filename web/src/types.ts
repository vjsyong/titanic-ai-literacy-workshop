export type StepStatus = "done" | "current" | "locked";

export interface MarkdownBlock {
  type: "markdown";
  text: string;
}

export interface TableBlock {
  type: "table";
  columns: string[];
  rows: unknown[][];
  total_rows: number;
  truncated: boolean;
}

export type ChartKind =
  | "bar"
  | "pictorial"
  | "line"
  | "area"
  | "scatter"
  | "pie"
  | "donut"
  | "histogram"
  | "gauge"
  | "heatmap";

export interface ChartPayload {
  kind: ChartKind;
  data?: Record<string, unknown>[];
  x?: string;
  y?: string | string[];
  color?: string;
  size?: string;
  series?: string[];
  title?: string;
  stacked?: boolean;
  horizontal?: boolean;
  diverging?: boolean;
  x_label?: string;
  y_label?: string;
  bins?: number;
  palette?: string[];
  value?: number;
}

export interface ChartBlock {
  type: "chart";
  chart: ChartPayload;
}

export interface MetricBlock {
  type: "metric";
  value: number;
  label: string;
  format?: "percent" | "number" | "probability";
}

export type ResultBlock = MarkdownBlock | TableBlock | ChartBlock | MetricBlock;

export interface Result {
  blocks: ResultBlock[];
}

export interface StepState {
  number: number;
  title: string;
  story: string;
  prompt: string;
  hints: string[];
  placeholder: string;
  guide: string;
  experiment: string;
  context: Result | null;
  reference: string;
  reference_alt: string;
  status: StepStatus;
  result: Result | null;
  error: string | null;
  code: string | null;
}

export interface ScriptState {
  id: string;
  title: string;
  intro: string;
  completed: number;
  total: number;
  steps: StepState[];
}

export interface InputSpecItem {
  label: string;
  kind: "radio" | "slider";
  choices?: (string | number)[];
  min?: number;
  max?: number;
  step?: number;
  value: string | number;
}

export interface DashboardState {
  input_spec: InputSpecItem[] | null;
  predict_ready: boolean;
  complete: boolean;
}

export interface WorkshopState {
  version: string;
  all_complete: boolean;
  scripts: ScriptState[];
  dashboard: DashboardState;
  import_errors: Record<string, string | null>;
}

export interface PredictResponse {
  ok: boolean;
  text?: string;
  probability?: number | null;
  band?: string | null;
  error?: string;
}

export interface RandomPassengerResponse {
  ok: boolean;
  values?: Record<string, string | number>;
  name?: string;
  actual_survived?: 0 | 1;
  model_probability?: number;
  model_prediction?: 0 | 1;
  match?: boolean;
  error?: string;
}

export interface Persona {
  id: string;
  title: string;
  sex: "male" | "female";
  age: number;
  portrait: string;
  pclass: number;
  sibsp: number;
  parch: number;
  fare: number;
  embarked: string;
  cabin: string | null;
  anchor_passenger_id: number;
  anchor_name: string;
  actual_survived: 0 | 1;
  model_probability: number;
  model_prediction: 0 | 1;
  match: boolean;
}

export interface PersonasFile {
  dataset: string;
  portrait_dir: string;
  classifier: {
    test_accuracy: number;
    persona_hits: number;
    model: string;
    features: string[];
    [key: string]: unknown;
  };
  personas: Persona[];
}
