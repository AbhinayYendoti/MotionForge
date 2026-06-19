import { z } from "zod";

const MAX_PROMPT_WORDS = 3000;

function wordCount(value: string) {
  return value.trim().split(/\s+/).filter(Boolean).length;
}

export const projectIdSchema = z.object({
  projectId: z.string().min(8)
});

export const createProjectSchema = z.object({
  title: z.string().min(2).max(120),
  prompt: z
    .string()
    .refine((value) => wordCount(value) <= MAX_PROMPT_WORDS, `Prompt must be ${MAX_PROMPT_WORDS} words or fewer.`)
    .optional()
    .or(z.literal("")),
  imageUrl: z.string().url().optional()
});

export const renderFormatSchema = z.enum(["reel", "landscape", "square"]);
