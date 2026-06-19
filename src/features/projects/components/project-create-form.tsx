"use client";

import { createProjectAction } from "../actions";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { SubmitButton } from "./submit-button";
import { uploadFiles } from "@/lib/uploadthing";

export function ProjectCreateForm() {
  async function handleSubmit(formData: FormData) {
    const file = formData.get("file") as File | null;
    
    // In production, we must use UploadThing to store the image and get a CDN URL.
    if (file && file.size > 0) {
      try {
        const [res] = await uploadFiles("creativeImage", {
          files: [file],
        });
        formData.set("imageUrl", res.url);
        formData.delete("file");
      } catch (err) {
        alert("Image upload failed. Please try again.");
        return;
      }
    }
    
    await createProjectAction(formData);
  }

  return (
    <form action={handleSubmit} className="grid gap-7">
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
