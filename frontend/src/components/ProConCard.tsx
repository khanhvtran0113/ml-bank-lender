import React from "react";
import { List, ListItem } from "@tremor/react";
import { RiCheckboxCircleFill, RiCloseCircleFill } from "@remixicon/react";

function classNames(...classes: any) {
  return classes.filter(Boolean).join(" ");
}

export const ProConCard = React.memo(
  ({ points, isPro }: { points: string[]; isPro: boolean }) => {
    return (
      <div className="flex px-12 w-[700px] mx-auto">
        {/* bg-gray-950 used as color to match underlying dark mode background color */}{" "}
        <div
          className={classNames(
            "bg-tremor-background-muted dark:bg-dark-tremor-background-muted rounded-tremor-default border border-tremor-border p-6 dark:border-dark-tremor-border"
          )}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <h4 className="text-tremor-default font-semibold leading-8 text-tremor-content-strong dark:text-dark-tremor-content-strong">
                {isPro ? "Pros" : "Cons"}
              </h4>
            </div>
          </div>
          <List className="mt-4 text-tremor-content-emphasis dark:text-dark-tremor-content-emphasis">
            {points.map((point) => (
              <ListItem key={point} className="justify-start space-x-2 py-2.5">
                {isPro ? (
                  <RiCheckboxCircleFill
                    className={classNames(
                      "text-tremor-brand dark:text-dark-tremor-brand size-5 shrink-0"
                    )}
                    aria-hidden={true}
                  />
                ) : (
                  <RiCloseCircleFill
                    className={classNames(
                      "text-red-500 dark:text-red-400 size-5 shrink-0"
                    )}
                    aria-hidden={true}
                  />
                )}
                <span>{point}</span>
              </ListItem>
            ))}
          </List>
        </div>
      </div>
    );
  }
);
