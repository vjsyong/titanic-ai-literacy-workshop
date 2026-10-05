import { useEffect, useState } from "react";
import type { PersonasFile, PredictResponse, WorkshopState } from "./types";

/**
 * Live workshop state: an initial fetch plus a Server-Sent Events stream
 * that pushes fresh state the moment a gate is saved.
 */
export function useWorkshopState() {
  const [state, setState] = useState<WorkshopState | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let active = true;

    fetch("/api/state")
      .then((response) => response.json())
      .then((data: WorkshopState) => {
        if (active) setState(data);
      })
      .catch(() => {});

    const source = new EventSource("/api/events");
    source.onopen = () => setConnected(true);
    source.onmessage = (event) => {
      try {
        setState(JSON.parse(event.data) as WorkshopState);
        setConnected(true);
      } catch {
        // ignore malformed frames
      }
    };
    source.onerror = () => setConnected(false);

    return () => {
      active = false;
      source.close();
    };
  }, []);

  return { state, connected };
}

export async function predict(
  values: Record<string, string | number>,
): Promise<PredictResponse> {
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ values }),
    });
    return (await response.json()) as PredictResponse;
  } catch {
    return { ok: false, error: "The workshop server is not answering." };
  }
}

/** The quiz roster (personas.json), fetched once for the front-page game. */
export function usePersonas() {
  const [data, setData] = useState<PersonasFile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetch("/api/personas")
      .then((response) => response.json())
      .then((payload: PersonasFile) => {
        if (active) setData(payload);
      })
      .catch(() => {
        if (active) setData(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return { data, loading };
}
