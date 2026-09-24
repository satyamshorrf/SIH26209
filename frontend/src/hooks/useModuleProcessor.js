import { useCallback, useState } from "react";
import toast from "react-hot-toast";

/**
 * Reusable hook encapsulating the upload -> process workflow shared by every
 * analysis module.  It tracks the selected file, upload metadata, processing
 * progress, the result payload and any error, exposing imperative handlers.
 *
 * @param {object} apiModule - an object with `upload(file, ...)` and
 *   `process(storedName, ...)` methods (e.g. IceAPI, VolumeAPI).
 */
export function useModuleProcessor(apiModule) {
  const [file, setFile] = useState(null);
  const [secondaryFile, setSecondaryFile] = useState(null);
  const [uploadMeta, setUploadMeta] = useState(null);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle"); // idle|uploading|processing|done|error
  const [error, setError] = useState(null);

  const reset = useCallback(() => {
    setFile(null);
    setSecondaryFile(null);
    setUploadMeta(null);
    setResult(null);
    setProgress(0);
    setStatus("idle");
    setError(null);
  }, []);

  const run = useCallback(
    async (...extraArgs) => {
      if (!file) {
        toast.error("Please select a dataset file first.");
        return;
      }
      setError(null);
      setResult(null);
      try {
        // Upload phase.
        setStatus("uploading");
        setProgress(25);
        const uploaded = await apiModule.upload(file, secondaryFile);
        setUploadMeta(uploaded);
        setProgress(55);

        // Resolve the stored name(s) from the upload response.
        const primaryStored =
          uploaded.dfsar?.stored_name || uploaded.dataset?.stored_name;
        const secondaryStored = uploaded.ohrc?.stored_name;
        if (!primaryStored) {
          throw new Error("Upload did not return a stored file reference.");
        }

        // Process phase. The primary stored name is always the first argument;
        // for the ice module the secondary (OHRC) stored name follows, and any
        // caller-supplied options (depth, algorithm, grid size...) come after.
        setStatus("processing");
        setProgress(75);
        const processArgs =
          secondaryStored !== undefined
            ? [secondaryStored, ...extraArgs]
            : [...extraArgs];
        const data = await apiModule.process(primaryStored, ...processArgs);
        setResult(data);
        setProgress(100);
        setStatus("done");
        toast.success("Processing complete.");
        return data;
      } catch (err) {
        const message =
          err?.response?.data?.detail || err?.message || "Processing failed.";
        setError(message);
        setStatus("error");
        setProgress(0);
        toast.error(message);
      }
    },
    [apiModule, file, secondaryFile]
  );

  return {
    file,
    setFile,
    secondaryFile,
    setSecondaryFile,
    uploadMeta,
    result,
    progress,
    status,
    error,
    run,
    reset,
    isBusy: status === "uploading" || status === "processing",
  };
}
