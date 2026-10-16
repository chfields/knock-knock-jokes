import prettyMs from "pretty-ms";

export function formatDuration(ms: number): string {
  return prettyMs(ms);
}
