import { auth } from "@clerk/nextjs/server";
import { createUploadthing, type FileRouter, UploadThingError } from "uploadthing/server";

const f = createUploadthing();

export const uploadRouter = {
  creativeImage: f({
    image: {
      maxFileSize: "8MB",
      maxFileCount: 1,
      minFileCount: 1
    }
  })
    .middleware(async () => {
      const { userId } = await auth();
      if (!userId) throw new UploadThingError("Unauthorized");
      return { userId };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      return {
        uploadedBy: metadata.userId,
        url: file.ufsUrl,
        name: file.name,
        size: file.size,
        type: file.type
      };
    })
} satisfies FileRouter;

export type UploadRouter = typeof uploadRouter;
