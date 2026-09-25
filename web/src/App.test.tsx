import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router";
import App from "./App";

const joke = { id: "cow-says", name: "Cow says", lines: ["Knock, knock.", "Who's there?", "Cow says.", "Cow says who?", "No, a cow says moo!"] };

function renderApp(path = "/jokes/cow-says") { return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>); }

beforeEach(() => {
  vi.restoreAllMocks();
  vi.stubGlobal("fetch", vi.fn((url: string, init?: RequestInit) => {
    if (init?.method === "POST") return Promise.resolve(new Response(JSON.stringify({ message: "Thanks for rating this joke!" }), { status: 201 }));
    return Promise.resolve(new Response(JSON.stringify(url.includes("/api/jokes/") ? joke : [joke])));
  }));
});
afterEach(cleanup);

describe("joke reveal", () => {
  it("reveals each line in order and shows rating last", async () => {
    renderApp();
    await screen.findByText(joke.lines[0]);
    const first = screen.getByRole("button", { name: joke.lines[1] });
    fireEvent.click(first);
    expect(screen.getByText(joke.lines[1])).toBeInTheDocument();
    expect(screen.getByRole("button", { name: joke.lines[3] })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: joke.lines[3] }));
    expect(screen.getByText(joke.lines[4])).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Submit rating" })).toBeInTheDocument();
  });
});

describe("rating form", () => {
  it("shows success after submitting", async () => {
    renderApp();
    await screen.findByText(joke.lines[0]);
    fireEvent.click(screen.getByRole("button", { name: joke.lines[1] }));
    fireEvent.click(screen.getByRole("button", { name: joke.lines[3] }));
    fireEvent.click(screen.getByRole("radio", { name: "5" }));
    fireEvent.click(screen.getByRole("button", { name: "Submit rating" }));
    expect(await screen.findByText("Thanks for rating this joke!")).toBeInTheDocument();
  });

  it("shows an API error", async () => {
    vi.stubGlobal("fetch", vi.fn((url: string, init?: RequestInit) => {
      if (init?.method === "POST") return Promise.resolve(new Response(JSON.stringify({ message: "No storage" }), { status: 500 }));
      return Promise.resolve(new Response(JSON.stringify(url.includes("/api/jokes/") ? joke : [joke])));
    }));
    renderApp();
    await screen.findByText(joke.lines[0]);
    fireEvent.click(screen.getByRole("button", { name: joke.lines[1] }));
    fireEvent.click(screen.getByRole("button", { name: joke.lines[3] }));
    fireEvent.click(screen.getByRole("radio", { name: "1" }));
    fireEvent.click(screen.getByRole("button", { name: "Submit rating" }));
    await waitFor(() => expect(screen.getByText("No storage")).toBeInTheDocument());
  });
});
