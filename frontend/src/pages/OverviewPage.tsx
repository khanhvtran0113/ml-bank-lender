import React from "react";
import { useLendee } from "../hooks/useLendee";
import { ProConCard } from "../components/ProConCard";
import { BalanceGraph } from "../components/BalanceGraph";

export const OverviewPage = React.memo(() => {
  const { data: lendeeInfo } = useLendee("john");

  if (lendeeInfo == null) {
    return <div />;
  }

  return (
    <div className="p-12">
      <h1 className="mt-2 max-w-2xl text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl pl-12 pb-12">
        {lendeeInfo.name}
      </h1>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-2">
        <ProConCard points={lendeeInfo.verdict_json.pros} isPro={true} />
        <ProConCard points={lendeeInfo.verdict_json.cons} isPro={false} />
      </div>
      <div className="p-12 m-auto">
        <BalanceGraph
          balances={lendeeInfo.balance_json.balances}
          currency={lendeeInfo.verdict_json.currency}
        />
      </div>
    </div>
  );
});
