import { createProjectAction } from "../actions";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { SubmitButton } from "./submit-button";

export function ProjectCreateForm() {
  return (
    <form action={createProjectAction} className="grid gap-7">
      <div>
        <label className="eyebrow mb-3 block" htmlFor="title">
          Project title
        </label>
        <Input id="title" name="title" required placeholder="Luxury watch reel" />
      </div>
      <div>
        <label className="eyebrow mb-3 block" htmlFor="prompt">
          Creative direction
        </label>
        <Textarea id="prompt" name="prompt" placeholder="Create a cinematic product showcase with a confident CTA." />
      </div>
      <div>
        <label className="eyebrow mb-3 block" htmlFor="file">
          Image upload
        </label>
        <Input id="file" name="file" type="file" accept="image/png,image/jpeg,image/webp" required className="py-2" />
      </div>
      <SubmitButton size="lg">Create project</SubmitButton>
    </form>
  );
}
