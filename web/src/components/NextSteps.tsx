import { useState } from "react";
import { ExternalLink, ImageOff, Lightbulb, Rocket } from "lucide-react";

const DATASETS = [
  {
    id: "iris",
    name: "Iris Flowers",
    image: "/next/iris.jpg",
    imageHint: "web/public/next/iris.jpg",
    url: "https://archive.ics.uci.edu/dataset/53/iris",
    what: "150 iris flowers measured in 1936: sepal length, sepal width, petal length, petal width, and the species. Three species, 50 flowers each. The friendliest dataset in data science.",
    ideas: [
      "Guess the species from the four measurements.",
      "Draw scatter plots to find which species separate cleanly.",
      "Start here if you want a quick win.",
    ],
  },
  {
    id: "wine",
    name: "Wine Quality",
    image: "/next/wine.jpg",
    imageHint: "web/public/next/wine.jpg",
    url: "https://archive.ics.uci.edu/dataset/186/wine-quality",
    what: "Chemical test results for thousands of Portuguese wines: acidity, sugar, alcohol, pH and more, plus a quality score from human tasters. Red and white wines come as separate files.",
    ideas: [
      "Predict the quality score from the chemistry. It is a number from 0 to 10, so this is regression.",
      "Find which chemicals matter most to the tasters.",
      "Try telling red wine from white with the same features.",
    ],
  },
  {
    id: "boston",
    name: "Boston Housing",
    image: "/next/boston.jpg",
    imageHint: "web/public/next/boston.jpg",
    url: "https://archive.ics.uci.edu/dataset/2/boston-housing",
    what: "1970s census data for 506 Boston neighbourhoods: crime rate, average rooms, tax rate, distance to jobs and more, with the median home value as the target.",
    ideas: [
      "Predict home values. Another regression problem.",
      "Spot which neighbourhood facts move the price the most.",
      "Study the fairness angle: one column encodes race, which makes this a famous case study in using data carefully.",
    ],
  },
];

function DatasetImage({
  src,
  hint,
  name,
}: {
  src: string;
  hint: string;
  name: string;
}) {
  const [missing, setMissing] = useState(false);

  if (missing) {
    return (
      <div className="flex aspect-square w-full flex-col items-center justify-center gap-1.5 border border-dashed border-line2 bg-[#fafafa] p-4 text-center">
        <ImageOff className="h-6 w-6 text-faint" />
        <div className="text-sm font-semibold text-dim">Image placeholder</div>
        <p className="max-w-[14rem] text-xs leading-relaxed text-faint">
          Instructor: drop a square image at{" "}
          <code className="border border-line bg-white px-1 font-mono">
            {hint}
          </code>{" "}
          and it appears here.
        </p>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={`${name} dataset illustration`}
      className="aspect-square w-full border border-line object-cover"
      onError={() => setMissing(true)}
    />
  );
}

/**
 * Stage 4: a static next-steps page. Points students at other classic
 * datasets and repeats the loop they already know.
 */
export function NextSteps() {
  return (
    <section className="animate-rise space-y-4">
      <div className="border border-acc bg-tint-acc p-6 sm:p-8">
        <div className="micro-label flex items-center gap-1.5 text-acc">
          <Rocket className="h-3.5 w-3.5" />
          Stage 4: next steps
        </div>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-ink sm:text-3xl">
          You have the whole loop. Now point it at anything.
        </h2>
        <p className="mt-2 max-w-3xl text-base leading-relaxed text-ink">
          You loaded a messy table, turned words into numbers, trained a model,
          tested it on passengers it had never seen, and put it behind a live
          form. That same loop works on any dataset. Pick one below, open a
          fresh chat with your AI assistant, and run it again.
        </p>
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          <div className="flex items-start gap-2 border border-acc/30 bg-white/70 px-3 py-2 text-sm text-ink">
            <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-acc" />
            The loop you now own: meet the data, choose features and target,
            train, test on unseen rows, then build something people can use.
          </div>
          <div className="flex items-start gap-2 border border-acc/30 bg-white/70 px-3 py-2 text-sm text-ink">
            <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-acc" />
            Keep asking why: a model can score well and still be unfair or
            useless. That question is the real skill.
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {DATASETS.map((dataset) => (
          <article
            key={dataset.id}
            className="flex flex-col border border-line bg-white p-5"
          >
            <DatasetImage
              src={dataset.image}
              hint={dataset.imageHint}
              name={dataset.name}
            />
            <h3 className="mt-4 text-lg font-bold tracking-tight text-ink">
              {dataset.name}
            </h3>
            <p className="mt-1.5 text-sm leading-relaxed text-dim">
              {dataset.what}
            </p>
            <div className="micro-label mt-3 text-faint">What you can do</div>
            <ul className="mt-1 list-disc space-y-1 pl-5 text-sm leading-relaxed text-[#3f3f46]">
              {dataset.ideas.map((idea) => (
                <li key={idea}>{idea}</li>
              ))}
            </ul>
            <a
              href={dataset.url}
              target="_blank"
              rel="noreferrer"
              className="mt-4 inline-flex h-9 w-fit items-center gap-2 border border-line bg-white px-4 text-sm font-semibold text-ink transition hover:border-black"
            >
              <ExternalLink className="h-4 w-4 text-acc" />
              Open the dataset
            </a>
          </article>
        ))}
      </div>

      <div className="flex flex-col items-start justify-between gap-4 border border-line bg-white p-6 sm:flex-row sm:items-center">
        <div>
          <div className="text-lg font-bold tracking-tight text-ink">
            Your turn: pick a dataset and run the loop again.
          </div>
          <p className="mt-1 text-sm text-dim">
            Start a new chat with your AI assistant, describe the dataset, and
            ask for the first look. The rest of the loop will feel familiar.
          </p>
        </div>
        <a
          href="https://archive.ics.uci.edu/datasets"
          target="_blank"
          rel="noreferrer"
          className="inline-flex h-11 shrink-0 items-center gap-2 bg-black px-6 font-semibold text-white transition hover:bg-[#27272a]"
        >
          Browse more datasets
          <ExternalLink className="h-5 w-5" />
        </a>
      </div>
    </section>
  );
}
