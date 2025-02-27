import { RiDeleteBinLine, RiFileLine } from "@remixicon/react";
import React from "react";

interface FilesListProps {
  files: File[];
  clearFiles: () => void;
}
export const FilesList = React.memo(({ files, clearFiles }: FilesListProps) => {
  return (
    <ul className="list-none mt-8">
      {files.map((file: any) => (
        <li
          key={file.path}
          className="relative rounded-tremor-default border border-tremor-border bg-tremor-background p-4 shadow-tremor-input dark:border-dark-tremor-border dark:bg-dark-tremor-background dark:shadow-dark-tremor-input"
        >
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <button
              type="button"
              className="rounded-tremor-small p-2 text-tremor-content-subtle hover:text-tremor-content dark:text-dark-tremor-content-subtle hover:dark:text-tremor-content"
              aria-label="Remove file"
              onClick={clearFiles}
            >
              <RiDeleteBinLine className="size-5 shrink-0" aria-hidden={true} />
            </button>
          </div>
          <div className="flex items-center space-x-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-tremor-small bg-tremor-background-subtle dark:bg-dark-tremor-background-subtle">
              <RiFileLine
                className="size-5 text-tremor-content-emphasis dark:text-dark-tremor-content-emphasis"
                aria-hidden={true}
              />
            </span>
            <div>
              <p className="text-tremor-label font-medium text-tremor-content-strong dark:text-dark-tremor-content-strong">
                {file.path}
              </p>
              <p className="mt-0.5 text-tremor-label text-tremor-content dark:text-dark-tremor-content">
                {file.size} bytes
              </p>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
});
