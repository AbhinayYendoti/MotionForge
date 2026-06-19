import { runPipelineAction } from "../actions";
import { SubmitButton } from "./submit-button";

export function RunPipelineForm({ projectId }: { projectId: string }) {
  return (
    <form action={runPipelineAction} className="flex flex-col gap-3 sm:flex-row">
      <input type="hidden" name="projectId" value={projectId} />
      <select
        name="format"
        className="focus-ring min-h-12 rounded-pill border border-border bg-card px-6 text-[16px] font-[450] text-foreground"
        defaultValue="reel"
      >
        <option value="reel">1080x1920 Reel</option>
        <option value="landscape">1920x1080 Landscape</option>
        <option value="square">1080x1080 Square</option>
      </select>
      <SubmitButton size="lg">Run pipeline</SubmitButton>
    </form>
  );
}
