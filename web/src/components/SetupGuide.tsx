import { useState } from "react";
import { ImageOff, MonitorPlay } from "lucide-react";

/**
 * Shows the instructor's side-by-side setup screenshot
 * (`web/public/onboarding/setup.png`). Until that file is dropped in, a
 * labelled dashed placeholder explains exactly what the picture should show.
 */
export function SetupGuide() {
  const [missing, setMissing] = useState(false);

  return (
    <div className="border border-line bg-white p-5">
      <div className="flex items-center gap-2">
        <MonitorPlay className="h-5 w-5 text-acc" />
        <h3 className="text-lg font-bold tracking-tight text-ink">
          Set yourself up
        </h3>
      </div>
      <p className="mt-1 text-sm leading-relaxed text-dim">
        Put the <strong className="font-semibold text-ink">OpenCode chat</strong>{" "}
        on one side of your screen and{" "}
        <strong className="font-semibold text-ink">this workshop page</strong> on
        the other, so you can copy a prompt, paste it into the chat, and watch
        the page change without switching windows.
      </p>

      {missing ? (
        <div className="mt-4 flex min-h-[180px] flex-col items-center justify-center gap-2 border border-dashed border-line2 bg-[#fafafa] p-6 text-center">
          <ImageOff className="h-6 w-6 text-faint" />
          <div className="text-sm font-semibold text-dim">
            Screenshot placeholder
          </div>
          <p className="max-w-md text-xs leading-relaxed text-faint">
            Instructor: drop a side-by-side picture at{" "}
            <code className="border border-line bg-white px-1 font-mono">
              web/public/onboarding/setup.png
            </code>{" "}
            and it appears here for students.
          </p>
        </div>
      ) : (
        <img
          src="/onboarding/setup.png"
          alt="OpenCode chat window beside the workshop page"
          className="mt-4 max-h-96 w-full border border-line object-contain"
          onError={() => setMissing(true)}
        />
      )}
    </div>
  );
}
