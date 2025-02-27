"use client";

import { ComboChart, TooltipProps } from "./ComboChart";

const data = [
  {
    date: "Jan 23",
    SolarCells: 2890,
    Adhesive: 1700,
  },
  {
    date: "Feb 23",
    SolarCells: 2756,
    Adhesive: 1650,
  },
  {
    date: "Mar 23",
    SolarCells: 3322,
    Adhesive: 800,
  },
  {
    date: "Apr 23",
    SolarCells: 3470,
    Adhesive: -1950,
  },
  {
    date: "May 23",
    SolarCells: 3475,
    Adhesive: -1600,
  },
  {
    date: "Jun 23",
    SolarCells: 3129,
    Adhesive: -1700,
  },
  {
    date: "Jul 23",
    SolarCells: 3490,
    Adhesive: 800,
  },
  {
    date: "Aug 23",
    SolarCells: 2903,
    Adhesive: 1900,
  },
  {
    date: "Sep 23",
    SolarCells: 2643,
    Adhesive: 3750,
  },
  {
    date: "Oct 23",
    SolarCells: 2837,
    Adhesive: 5600,
  },
  {
    date: "Nov 23",
    SolarCells: 2954,
    Adhesive: 2950,
  },
  {
    date: "Dec 23",
    SolarCells: 3239,
    Adhesive: 3800,
  },
];

const Tooltip = (props: TooltipProps) => {
  const { payload, active, label } = props;
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0].payload;

  const categoriesToShow = ["Adhesive", "SolarCells"];

  return (
    <div className="w-56 rounded-md border bg-white/5 p-3 text-sm shadow-sm backdrop-blur-md dark:border-gray-800 dark:bg-black/5">
      <p className="mb-2 font-medium text-gray-900 dark:text-gray-50">
        {label}
      </p>
      <div className="flex flex-col space-y-2">
        {categoriesToShow.map((category) => (
          <div key={category} className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div
                className={` ${
                  category === "Adhesive"
                    ? "h-2.5 w-2.5 rounded-sm bg-blue-500"
                    : "h-1 w-4 rounded-full bg-pink-500"
                }`}
              />
              <p className="text-gray-700 dark:text-gray-400">{category}</p>
            </div>
            <p className="font-medium tabular-nums text-gray-900 dark:text-gray-50">
              ${data[category]}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export function ComboChartCustomTooltipExample() {
  return (
    <div>
      <ComboChart
        className="hidden sm:block"
        data={data}
        index="date"
        enableBiaxial={true}
        barSeries={{
          colors: ["blue"],
          categories: ["Adhesive"],
          valueFormatter: (v) =>
            `$${Intl.NumberFormat("us").format(v).toString()}`,
          yAxisWidth: 60,
        }}
        lineSeries={{
          colors: ["pink"],
          categories: ["SolarCells"],
          valueFormatter: (v) =>
            `$${Intl.NumberFormat("us").format(v).toString()}`,
        }}
        customTooltip={Tooltip}
      />
      <ComboChart
        className="sm:hidden"
        data={data}
        index="date"
        enableBiaxial={true}
        barSeries={{
          colors: ["blue"],
          categories: ["Adhesive"],
          valueFormatter: (v) =>
            `$${Intl.NumberFormat("us").format(v).toString()}`,
          yAxisWidth: 60,
        }}
        lineSeries={{
          colors: ["pink"],
          categories: ["SolarCells"],
          valueFormatter: (v) =>
            `$${Intl.NumberFormat("us").format(v).toString()}`,
        }}
        customTooltip={Tooltip}
      />
    </div>
  );
}
