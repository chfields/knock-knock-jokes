export type Joke = { id: string; name: string };
export type FullJoke = Joke & { lines: string[] };

export async function getJokes(): Promise<Joke[]> {
  const response = await fetch("/api/jokes");
  if (!response.ok) throw new Error("Could not load the catalogue.");
  return response.json();
}

export async function getJoke(id: string | "random"): Promise<FullJoke> {
  const response = await fetch(id === "random" ? "/api/jokes/random" : `/api/jokes/${id}`);
  if (!response.ok) throw new Error("Could not load that joke.");
  return response.json();
}

export async function rateJoke(id: string, rating: number): Promise<{ message: string }> {
  const response = await fetch(`/api/jokes/${id}/ratings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating }),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.message ?? "Your rating could not be saved.");
  return body;
}
