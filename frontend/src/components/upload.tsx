import React from 'react';
import { RiDeleteBinLine, RiFileLine } from '@remixicon/react';
import { Divider, TextInput } from '@tremor/react';
import { useDropzone } from 'react-dropzone';
import { SelectHero } from './selector';

function classNames(...classes: any) {
  return classes.filter(Boolean).join(' ');
}

export default function FileUpload() {
  const [files, setFiles] = React.useState<any>([]);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => setFiles(acceptedFiles),
  });

  const filesList = files.map((file: any) => (
    <li
      key={file.path}
      className="relative rounded-tremor-default border border-tremor-border bg-tremor-background p-4 shadow-tremor-input dark:border-dark-tremor-border dark:bg-dark-tremor-background dark:shadow-dark-tremor-input"
    >
      <div className="absolute right-4 top-1/2 -translate-y-1/2">
        <button
          type="button"
          className="rounded-tremor-small p-2 text-tremor-content-subtle hover:text-tremor-content dark:text-dark-tremor-content-subtle hover:dark:text-tremor-content"
          aria-label="Remove file"
          onClick={() =>
            setFiles((prevFiles: any) =>
              prevFiles.filter((prevFile: any) => prevFile.path !== file.path),
            )
          }
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
  ));
  return (
    <>
      <div className="sm:mx-auto sm:max-w-3xl mt-24">
        <form action="#" method="post">
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
              />
            </div>
            <div className="col-span-full">
              <label
                htmlFor="file-upload-2"
                className="text-tremor-default font-medium text-tremor-content-strong dark:text-dark-tremor-content-strong"
              >
                File(s) upload
              </label>
              <div
                {...getRootProps()}
                className={classNames(
                  isDragActive
                    ? 'border-tremor-brand bg-tremor-brand-faint dark:border-dark-tremor-brand dark:bg-dark-tremor-brand-faint'
                    : '',
                  'mt-2 flex justify-center rounded-tremor-default border border-dashed border-gray-300 px-6 py-20 dark:border-dark-tremor-border',
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
                      <span>choose file(s)</span>
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
              {filesList.length > 0 && (
                <>
                  <h4 className="mt-6 text-tremor-default font-medium text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    File(s) to upload
                  </h4>
                  <ul className="mt-4 space-y-4">
                    {filesList}
                  </ul>
                </>
              )}
            </div>
          </div>
          <Divider className="my-10" />
          <div className="flex items-center justify-end space-x-3">
            <button
              type="button"
              className="whitespace-nowrap rounded-tremor-small border border-tremor-border px-4 py-2 text-tremor-default font-medium text-tremor-content shadow-tremor-input transition-all hover:bg-tremor-background-muted hover:text-tremor-content-emphasis dark:border-dark-tremor-border dark:text-dark-tremor-content dark:shadow-dark-tremor-input hover:dark:bg-dark-tremor-background-muted hover:dark:text-dark-tremor-content-emphasis"
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
        </form>
        <h2 className="font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong mb-2">
            Already created a lendee? Select it here:
        </h2>
        <SelectHero />
      </div>
    </>
  );
}
