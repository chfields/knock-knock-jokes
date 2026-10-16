import { expect, it } from "vitest";

import { formatDuration } from "./formatDuration";

it("formats milliseconds as a compact duration", () => {
  expect(formatDuration(1337)).toBe("1.3s");
});
