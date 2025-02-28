import React from "react";
import { ComboChart, TooltipProps } from "./ComboChart";
import { Balance } from "../hooks/useLendee";

const Tooltip = (props: TooltipProps) => {
  const { payload, active, label } = props;
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0].payload;

  const categoriesToShow = ["balance", "change"];

  return (
    <div className="w-56 rounded-md border bg-white/5 p-3 text-sm shadow-sm backdrop-blur-md dark:border-gray-800 dark:bg-black/5">
      <p className="mb-2 font-medium text-gray-900 dark:text-gray-50">
        {new Date(label).toLocaleDateString("en-US", {
          month: "numeric",
          day: "numeric",
          year: "numeric",
        })}
      </p>
      <div className="flex flex-col space-y-2">
        {categoriesToShow.map((category) => (
          <div key={category} className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div
                className={` ${
                  category === "change"
                    ? "h-2.5 w-2.5 rounded-sm bg-blue-500"
                    : "h-1 w-4 rounded-full bg-pink-500"
                }`}
              />
              <p className="text-gray-700 dark:text-gray-400">{category}</p>
            </div>
            <p className="font-medium tabular-nums text-gray-900 dark:text-gray-50">
              {data[category]}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export const BalanceGraph = React.memo(
  ({ balances, currency }: { balances: Balance[]; currency: string }) => {
    const thing = balances.map(({ balance, date }, index) => ({
      balance,
      timestamp: date.getTime(),
      date: date.toUTCString(),
      change:
        balance - (balances.at(index === 0 ? 0 : index - 1)?.balance ?? 0) >= 0
          ? `+${(
              balance - (balances.at(index === 0 ? 0 : index - 1)?.balance ?? 0)
            ).toFixed(2)}`
          : (
              balance - (balances.at(index === 0 ? 0 : index - 1)?.balance ?? 0)
            ).toFixed(2),
    }));

    return (
      <div>
        <ComboChart
          className="hidden sm:block"
          data={thing}
          index="timestamp"
          enableBiaxial={false}
          intervalType={"preserveStartEnd"}
          showGridLines={true}
          showXAxis={true}
          yAxisLabel={"bank account balance (" + currency + ")"}
          barSeries={{
            colors: ["blue"],
            categories: ["change"],
            yAxisWidth: 60,
          }}
          lineSeries={{
            colors: ["pink"],
            categories: ["balance"],
          }}
          customTooltip={Tooltip}
        />
      </div>
    );
  }
);
