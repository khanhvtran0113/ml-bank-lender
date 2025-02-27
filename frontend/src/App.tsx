import axios from "axios";
import React from "react";
import { LendeeInput } from "./components/LendeeInput";
import { FileUploader } from "./components/FileUploader";
import { LendeeSelector } from "./components/LendeeSelector";
import { FilesList } from "./components/FilesList";

export function App() {
  const [, setMessage] = React.useState<string>("");

  React.useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/")
      .then((response) => setMessage(response.data))
      .catch((error) => console.error("Error fetching data", error));
  }, []);

  const [files, setFiles] = React.useState<File[]>([]);
  const [lendeeName, setLendeeName] = React.useState<string | undefined>(
    undefined
  );

  return (
    <div className="sm:mx-auto sm:max-w-3xl mt-24">
      <form action="#" method="post">
        <LendeeInput
          lendeeName={lendeeName}
          onLendeeNameChange={setLendeeName}
        />
        {files.length === 0 ? (
          <FileUploader setFiles={setFiles} />
        ) : (
          <>
            <FilesList files={files} clearFiles={() => setFiles([])} />
            <div className="flex items-center justify-end space-x-3 mt-8">
              <button
                type="button"
                className="whitespace-nowrap rounded-tremor-small border border-tremor-border px-4 py-2 text-tremor-default font-medium text-tremor-content shadow-tremor-input transition-all hover:bg-tremor-background-muted hover:text-tremor-content-emphasis dark:border-dark-tremor-border dark:text-dark-tremor-content dark:shadow-dark-tremor-input hover:dark:bg-dark-tremor-background-muted hover:dark:text-dark-tremor-content-emphasis"
                onClick={() => setFiles([])}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="whitespace-nowrap rounded-tremor-small bg-tremor-brand px-4 py-2 text-tremor-default font-medium text-tremor-brand-inverted shadow-tremor-input transition-all hover:bg-tremor-brand-emphasis dark:bg-dark-tremor-brand dark:text-dark-tremor-brand-inverted dark:shadow-dark-tremor-input dark:hover:bg-dark-tremor-brand-emphasis"
              >
                Upload
              </button>
            </div>
          </>
        )}
      </form>
      <h2 className="font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong mb-2 mt-8">
        Already created a lendee? Select it here:
      </h2>
      <LendeeSelector />
    </div>
  );
}
