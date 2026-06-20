"use client";

import { useTransition } from "react";
import { Trash2 } from "lucide-react";
import { deleteProjectAction } from "../actions";

export function DeleteProjectForm({ projectId }: { projectId: string }) {
  const [isPending, startTransition] = useTransition();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (window.confirm("Are you sure you want to delete this project? This action cannot be undone.")) {
      const formData = new FormData(e.currentTarget);
      startTransition(() => {
        deleteProjectAction(formData);
      });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="hidden" name="projectId" value={projectId} />
      <button
        type="submit"
        disabled={isPending}
        className="inline-flex h-[48px] w-full items-center justify-center rounded-pill bg-destructive/10 px-6 font-[500] text-destructive transition-colors hover:bg-destructive/20 disabled:pointer-events-none disabled:opacity-50"
      >
        <Trash2 className="mr-2 h-5 w-5" />
        {isPending ? "Deleting..." : "Delete Project"}
      </button>
    </form>
  );
}
