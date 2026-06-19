import { currentUser } from "@clerk/nextjs/server";

export async function requireUser() {
  const clerkUser = await currentUser();
  if (!clerkUser) {
    throw new Error("Authentication required.");
  }

  const email = clerkUser.emailAddresses.find((address) => address.id === clerkUser.primaryEmailAddressId)?.emailAddress;
  if (!email) {
    throw new Error("Your Clerk account needs a verified primary email address.");
  }

  return {
    id: clerkUser.id,
    email
  };
}
