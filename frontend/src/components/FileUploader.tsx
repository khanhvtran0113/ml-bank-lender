import React from "react";
import { RiFileLine } from "@remixicon/react";
import { useDropzone } from "react-dropzone";

function classNames(...classes: any) {
  return classes.filter(Boolean).join(" ");
}

export const FileUploader = React.memo(
  ({ setFiles }: { setFiles: (files: File[]) => void }) => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop: (acceptedFiles) => setFiles(acceptedFiles),
    });

    return (
      <div className="col-span-full">
        <label
          htmlFor="file-upload-2"
          className="text-tremor-default font-medium text-tremor-content-strong dark:text-dark-tremor-content-strong"
        >
          File upload
        </label>
        <div
          {...getRootProps()}
          className={classNames(
            isDragActive
              ? "border-tremor-brand bg-tremor-brand-faint dark:border-dark-tremor-brand dark:bg-dark-tremor-brand-faint"
              : "",
            "mt-2 flex justify-center rounded-tremor-default border border-dashed border-gray-300 px-6 py-20 dark:border-dark-tremor-border"
          )}
        >
          <div>
            <RiFileLine
              className="mx-auto h-12 w-12 text-tremor-content-subtle dark:text-dark-tremor-content"
              aria-hidden={true}
            />
            <div className="mt-4 flex text-tremor-default leading-6 text-tremor-content dark:text-dark-tremor-content">
              <p>Drag and drop or</p>
              <label
                htmlFor="file"
                className="relative cursor-pointer rounded-tremor-small pl-1 font-medium text-tremor-brand hover:underline hover:underline-offset-4 dark:text-dark-tremor-brand"
              >
                <span>choose file</span>
                <input
                  {...getInputProps()}
                  id="file-upload-2"
                  name="file-upload-2"
                  type="file"
                  accept="application/pdf"
                  className="sr-only"
                />
              </label>
              <p className="pl-1">to upload</p>
            </div>
          </div>
        </div>
        <p className="mt-2 text-tremor-label leading-5 text-tremor-content dark:text-dark-tremor-content sm:flex sm:items-center sm:justify-between">
          <span>Only PDFs are allowed to be upload.</span>
          <span className="pl-1 sm:pl-0">Max. size per file: 50MB</span>
        </p>
      </div>
    );
  }
);
