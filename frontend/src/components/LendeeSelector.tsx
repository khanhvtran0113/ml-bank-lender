import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./Select";
import { getLendees } from "../util/backend";
import { useNavigate } from "react-router-dom";

export const LendeeSelector = React.memo(
  ({ setLendeeName }: { setLendeeName: (lendeeName: string) => void }) => {
    const navigate = useNavigate();

    const [lendees, setLendees] = React.useState<string[]>([]);

    React.useEffect(() => {
      getLendees().then((response: any) => {
        if (response != null) {
          const internalLendees = response.lendees;
          setLendees(
            internalLendees.map((internalLendee: any) => internalLendee.name)
          );
        }
      });
    }, []);

    const handleLendeeSelect = React.useCallback(
      (lendeeName: string) => {
        setLendeeName(lendeeName);
        navigate("/overview");
      },
      [navigate, setLendeeName]
    );

    return (
      <Select onValueChange={handleLendeeSelect}>
        <SelectTrigger>
          <SelectValue placeholder="Select" />
        </SelectTrigger>
        <SelectContent>
          {lendees.map((lendee: string) => (
            <SelectItem key={lendee} value={lendee}>
              {lendee}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    );
  }
);
