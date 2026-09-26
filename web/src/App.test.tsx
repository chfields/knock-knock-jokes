import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router";

const { announce } = vi.hoisted(() => ({ announce: vi.fn() }));

vi.mock("@react-aria/live-announcer", () => ({ announce }));

import App from "./App";

const joke = { id: "cow-says", name: "Cow says", lines: ["Knock, knock.", "Who's there?", "Cow says.", "Cow says who?", "No, a cow says moo!"] };

function renderApp(path = "/jokes/cow-says") { return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>); }

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((promiseResolve, promiseReject) => { resolve = promiseResolve; reject = promiseReject; });
  return { promise, resolve, reject };
}

function jokeResponse(loadedJoke: typeof joke) { return new Response(JSON.stringify(loadedJoke)); }

beforeEach(() => {
  vi.restoreAllMocks();
  announce.mockClear();
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

  it("announces the punchline when it is revealed", async () => {
    renderApp();
    await screen.findByText(joke.lines[0]);

    fireEvent.click(screen.getByRole("button", { name: joke.lines[1] }));
    fireEvent.click(screen.getByRole("button", { name: joke.lines[3] }));

    expect(announce).toHaveBeenCalledWith(joke.lines[4], "polite");
  });
});

describe("random joke", () => {
  it("transitions from loading to the fetched joke", async () => {
    renderApp("/");

    expect(screen.getByText("Loading…")).toBeInTheDocument();
    expect(await screen.findByText(joke.lines[0])).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/jokes/random");
  });

  it("keeps the most recently requested joke when random responses resolve out of order", async () => {
    const first = deferred<Response>();
    const earlierReload = deferred<Response>();
    const latestReload = deferred<Response>();
    const requests = [first, earlierReload, latestReload];
    vi.stubGlobal("fetch", vi.fn(() => requests.shift()!.promise));
    const initialJoke = { ...joke, id: "initial", name: "Initial", lines: ["Initial knock", "Initial who", "Initial says", "Initial says who", "Initial punchline"] };
    const staleJoke = { ...joke, id: "stale", name: "Stale", lines: ["Stale knock", "Stale who", "Stale says", "Stale says who", "Stale punchline"] };
    const latestJoke = { ...joke, id: "latest", name: "Latest", lines: ["Latest knock", "Latest who", "Latest says", "Latest says who", "Latest punchline"] };

    renderApp("/");
    await act(async () => { first.resolve(jokeResponse(initialJoke)); });
    await screen.findByText(initialJoke.lines[0]);

    const anotherJoke = screen.getByRole("button", { name: "Another random joke" });
    fireEvent.click(anotherJoke);
    fireEvent.click(anotherJoke);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(3));

    await act(async () => { latestReload.resolve(jokeResponse(latestJoke)); });
    await screen.findByText(latestJoke.lines[0]);
    await act(async () => { earlierReload.resolve(jokeResponse(staleJoke)); });

    await waitFor(() => expect(screen.queryByText(staleJoke.lines[0])).not.toBeInTheDocument());
    expect(screen.getByText(latestJoke.lines[0])).toBeInTheDocument();
  });

  it("shows an error when loading another random joke fails", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(jokeResponse(joke))
      .mockRejectedValueOnce(new Error("Random jokes are unavailable.")));
    renderApp("/");
    await screen.findByText(joke.lines[0]);

    fireEvent.click(screen.getByRole("button", { name: "Another random joke" }));

    expect(await screen.findByText("Random jokes are unavailable.")).toBeInTheDocument();
  });

  it("resets the reveal and rating state for another random joke", async () => {
    const nextJoke = { ...joke, id: "new-joke", name: "New joke", lines: ["New knock", "New who's there?", "New says", "New says who?", "New punchline"] };
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(jokeResponse(joke))
      .mockResolvedValueOnce(new Response(JSON.stringify({ message: "Thanks for rating this joke!" }), { status: 201 }))
      .mockResolvedValueOnce(jokeResponse(nextJoke)));
    renderApp("/");
    await screen.findByText(joke.lines[0]);

    fireEvent.click(screen.getByRole("button", { name: joke.lines[1] }));
    fireEvent.click(screen.getByRole("button", { name: joke.lines[3] }));
    fireEvent.click(screen.getByRole("radio", { name: "5" }));
    fireEvent.click(screen.getByRole("button", { name: "Submit rating" }));
    expect(await screen.findByText("Thanks for rating this joke!")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Another random joke" }));
    await screen.findByText(nextJoke.lines[0]);

    expect(screen.getByRole("button", { name: nextJoke.lines[1] })).toBeInTheDocument();
    expect(screen.queryByText(nextJoke.lines[4])).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Submit rating" })).not.toBeInTheDocument();
    expect(screen.queryByText("Thanks for rating this joke!")).not.toBeInTheDocument();
    expect(screen.queryByRole("radio", { name: "5", checked: true })).not.toBeInTheDocument();
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
