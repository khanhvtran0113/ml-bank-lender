import { useQuery } from "@tanstack/react-query";
import { MockBackend } from "../MockBackend";

export const useLendee = (lendee_name: string) =>
  useQuery({
    queryKey: ["lendee", lendee_name],
    queryFn: async () => {
      const mockBackend = new MockBackend();
      try {
        return await mockBackend.lendees(lendee_name);
      } catch (e: any) {
        console.warn(e);
      }
    },
    staleTime: Infinity,
    retry: true,
  });
