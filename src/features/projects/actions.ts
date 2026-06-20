"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ZodError } from "zod";
import { requireUser } from "@/lib/auth";
import { createProjectSchema } from "@/lib/schemas";
import { createProject, runPipeline } from "@/lib/backend";

export async function createProjectAction(formData: FormData) {
  await requireUser();
  let parsed;
  try {
    parsed = createProjectSchema.parse({
      title: formData.get("title"),
      prompt: formData.get("prompt") ?? undefined,
      imageUrl: formData.get("imageUrl") || undefined
    });
  } catch (error) {
    if (error instanceof ZodError) {
      throw new Error(error.issues[0]?.message ?? "Project details are invalid.");
    }
    throw error;
  }

  const file = formData.get("file");
  if (file instanceof File && file.size > 0) {
    throw new Error("Direct file uploads are disabled in production. Please check your network connection and try again.");
  }
  if (!parsed.imageUrl) {
    throw new Error("Upload an image or provide a remote image URL.");
  }

  const backendForm = new FormData();
  backendForm.set("title", parsed.title);
  if (parsed.prompt) backendForm.set("prompt", parsed.prompt);
  if (parsed.imageUrl) backendForm.set("imageUrl", parsed.imageUrl);
  const project = await createProject(backendForm);

  revalidatePath("/dashboard");
  redirect(`/projects/${project.id}`);
}

export async function runPipelineAction(formData: FormData) {
  await requireUser();
  const projectId = String(formData.get("projectId") ?? "");
  const format = String(formData.get("format") ?? "reel");
  await runPipeline(projectId, format);
  revalidatePath(`/projects/${projectId}`);
  redirect(`/projects/${projectId}`);
}
