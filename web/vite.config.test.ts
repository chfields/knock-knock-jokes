import { describe, expect, it } from "vitest";
import config from "./vite.config";

describe("development server configuration", () => {
  it("proxies API requests to Flask instead of serving the SPA fallback", () => {
    expect(config.server?.proxy).toMatchObject({
      "/api": { target: "http://127.0.0.1:5000" },
    });
  });
});
