import { useQuery } from "@tanstack/react-query";
import * as chrono from "chrono-node";
import { getLendeeInfo } from "../util/backend";

export type Balance = {
  balance: number;
  date: Date;
};

export type BalanceJson = {
  balances: Balance[];
};

export type VerdictJson = {
  cons: string[];
  currency: string;
  pros: string[];
};

export type LendeeData = {
  balance_json: BalanceJson;
  name: string;
  verdict_json: VerdictJson;
};

export const useLendee = (lendee_name: string) =>
  useQuery({
    queryKey: ["lendee", lendee_name],
    queryFn: async () => {
      try {
        const response: any = await getLendeeInfo(lendee_name);
        return sanitizeLendeeData(response);
      } catch (e: any) {
        console.warn(e);
      }
    },
    staleTime: Infinity,
    retry: true,
  });

function isBalance(obj: any): obj is { balance: number; date: string } {
  return typeof obj.balance === "number" && typeof obj.date === "string";
}

function parseDate(date: string): Date | undefined {
  return chrono.parseDate(date) ?? undefined;
}

function filterInvalidBalances(obj: any): Balance[] {
  return Array.isArray(obj.balances)
    ? obj.balances
        .filter(isBalance)
        .map((b: { balance: number; date: string }) => ({
          ...b,
          date: parseDate(b.date),
        }))
        .filter(
          (b: { balance: number; date: Date | undefined }) => b.date != null
        )
    : [];
}

function filterInvalidVerdictEntries(obj: any, key: "pros" | "cons"): string[] {
  return Array.isArray(obj[key])
    ? obj[key].filter((item: any) => typeof item === "string")
    : [];
}

function sanitizeBalanceJson(obj: any): BalanceJson {
  return {
    balances: filterInvalidBalances(obj).sort(
      (a, b) => a.date.getTime() - b.date.getTime()
    ),
  };
}

function sanitizeVerdictJson(obj: any): VerdictJson {
  return {
    cons: filterInvalidVerdictEntries(obj, "cons"),
    currency: typeof obj.currency === "string" ? obj.currency : "Unknown",
    pros: filterInvalidVerdictEntries(obj, "pros"),
  };
}

function sanitizeLendeeData(obj: any): LendeeData {
  return {
    name: typeof obj.name === "string" ? obj.name : "Unknown",
    balance_json: sanitizeBalanceJson(obj.balance_json),
    verdict_json: sanitizeVerdictJson(obj.verdict_json),
  };
}
