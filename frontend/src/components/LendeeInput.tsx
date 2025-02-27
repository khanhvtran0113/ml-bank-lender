import { TextInput } from "@tremor/react";
import React from "react";

interface LendeeInputProps {
  lendeeName: string | undefined;
  onLendeeNameChange: (lendeeName: string) => void;
}

export const LendeeInput = React.memo(
  ({ lendeeName, onLendeeNameChange }: LendeeInputProps) => {
    return (
      <div>
        <h2 className="font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
          Create a new lendee and upload their bank statments
        </h2>
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-6">
          <div className="col-span-full sm:col-span-6">
            <label
              htmlFor="lendee-name"
              className="text-tremor-default font-medium text-tremor-content-strong dark:text-dark-tremor-content-strong w-full"
            >
              Lendee Name
            </label>
            <TextInput
              type="text"
              id="lendee-name"
              name="lendee-name"
              placeholder="Lendee name"
              className="mt-2 w-full"
              value={lendeeName}
              onValueChange={onLendeeNameChange}
            />
          </div>
        </div>
      </div>
    );
  }
);
