import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Link, Route, Routes, useNavigate, useParams } from "react-router";
import { Alert, AlertTitle, Button, Card, CardContent, CardHeader, ListBox, ListBoxItem, Radio, RadioGroup } from "@heroui/react";
import { announce } from "@react-aria/live-announcer";
import { FullJoke, getJoke, getJokes, Joke, rateJoke } from "./api";

type ThemeMode = "system" | "light" | "dark";

function ThemeIcon({ mode }: { mode: ThemeMode }) {
  if (mode === "light") return <svg aria-hidden="true" fill="none" height="20" viewBox="0 0 24 24" width="20"><circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="2" /><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" stroke="currentColor" strokeLinecap="round" strokeWidth="2" /></svg>;
  if (mode === "dark") return <svg aria-hidden="true" fill="none" height="20" viewBox="0 0 24 24" width="20"><path d="M20.2 15.6A8.5 8.5 0 0 1 8.4 3.8 8.5 8.5 0 1 0 20.2 15.6Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="2" /></svg>;
  return <svg aria-hidden="true" fill="none" height="20" viewBox="0 0 24 24" width="20"><rect height="14" rx="1" stroke="currentColor" strokeWidth="2" width="18" x="3" y="3" /><path d="M8 21h8m-4-4v4" stroke="currentColor" strokeLinecap="round" strokeWidth="2" /></svg>;
}

function ThemeSelector() {
  const [mode, setMode] = useState<ThemeMode>("system");

  useEffect(() => {
    const query = window.matchMedia?.("(prefers-color-scheme: dark)");
    const applyTheme = () => {
      const dark = mode === "dark" || (mode === "system" && Boolean(query?.matches));
      document.documentElement.dataset.theme = dark ? "dark" : "light";
      document.documentElement.style.colorScheme = dark ? "dark" : "light";
    };
    applyTheme();
    if (mode === "system") {
      query?.addEventListener("change", applyTheme);
      return () => query?.removeEventListener("change", applyTheme);
    }
  }, [mode]);

  return <div aria-label="Theme mode" className="flex gap-1" role="group">
    {(["system", "light", "dark"] as const).map(option => <Button
      aria-label={`${option[0].toUpperCase()}${option.slice(1)} mode`}
      aria-pressed={mode === option}
      isIconOnly
      key={option}
      onPress={() => setMode(option)}
      title={`${option[0].toUpperCase()}${option.slice(1)} mode`}
      variant={mode === option ? "secondary" : "ghost"}
    ><ThemeIcon mode={option} /></Button>)}
  </div>;
}

function Layout({ children }: { children: ReactNode }) {
  return <main className="mx-auto min-h-screen max-w-3xl px-4 py-8">
    <header className="mb-8 flex items-center justify-between">
      <Link className="text-2xl font-bold" to="/">Knock-knock jokes</Link>
      <div className="flex items-center gap-4"><nav className="flex gap-4"><Link to="/">Random joke</Link><Link to="/jokes">Catalogue</Link></nav><ThemeSelector /></div>
    </header>{children}
  </main>;
}

function ErrorMessage({ message }: { message: string }) { return <Alert status="danger"><AlertTitle>{message}</AlertTitle></Alert>; }

function RatingForm({ jokeId }: { jokeId: string }) {
  const [rating, setRating] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(""); setMessage("");
    if (!rating) { setError("Please choose a rating from 1 to 5."); return; }
    try { setMessage((await rateJoke(jokeId, Number(rating))).message); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Your rating could not be saved."); }
  };
  return <form className="mt-6 space-y-4" onSubmit={submit} aria-label="Rate this joke">
    <RadioGroup aria-label="How funny was it?" value={rating} onChange={setRating}>
      {[1, 2, 3, 4, 5].map(value => <Radio.Root key={value} value={String(value)}><Radio.Content>{value}</Radio.Content></Radio.Root>)}
    </RadioGroup>
    <Button variant="primary" type="submit">Submit rating</Button>
    {message && <Alert status="success"><AlertTitle>{message}</AlertTitle></Alert>}{error && <ErrorMessage message={error} />}
  </form>;
}

function Teller({ joke }: { joke: FullJoke }) {
  const [step, setStep] = useState(0);
  const nextRef = useRef<HTMLButtonElement>(null);
  const reveal = () => {
    if (step === 1) announce(joke.lines[4], "polite");
    setStep(value => value + 1);
    window.setTimeout(() => nextRef.current?.focus(), 0);
  };
  const lines = joke.lines;
  return <Card>
    <CardHeader><h1 className="text-xl font-semibold">{joke.name}</h1></CardHeader>
    <CardContent className="gap-4">
      <p>{lines[0]}</p>
      {step === 0 ? <Button ref={nextRef} onPress={reveal}>{lines[1]}</Button> : <p aria-live="polite">{lines[1]}</p>}
      {step >= 1 && (step === 1 ? <Button ref={nextRef} onPress={reveal}>{lines[3]}</Button> : <p aria-live="polite">{lines[3]}</p>)}
      {step >= 2 && <><p>{lines[4]}</p><RatingForm jokeId={joke.id} /></>}
    </CardContent>
  </Card>;
}

function JokePage({ random = false }: { random?: boolean }) {
  const { id } = useParams(); const [joke, setJoke] = useState<FullJoke>(); const [error, setError] = useState(""); const [request, setRequest] = useState(0);
  useEffect(() => {
    let cancelled = false;
    const loadJoke = async () => {
      setError("");
      try {
        const loadedJoke = await getJoke(random ? "random" : id ?? "");
        if (!cancelled) setJoke(loadedJoke);
      } catch (reason) {
        if (!cancelled) setError(reason instanceof Error ? reason.message : "Could not load that joke.");
      }
    };
    void loadJoke();
    return () => { cancelled = true; };
  }, [id, random, request]);
  if (error) return <ErrorMessage message={error} />; if (!joke) return <p>Loading…</p>;
  return <><Teller key={joke.id} joke={joke} />{random && <Button className="mt-4" variant="tertiary" onPress={() => setRequest(value => value + 1)}>Another random joke</Button>}</>;
}

function Catalogue() {
  const [jokes, setJokes] = useState<Joke[]>([]); const [error, setError] = useState("");
  useEffect(() => { getJokes().then(setJokes).catch(reason => setError(reason.message)); }, []);
  if (error) return <ErrorMessage message={error} />;
  return <Card><CardHeader><h1 className="text-xl font-semibold">Catalogue</h1></CardHeader><CardContent><ListBox aria-label="Jokes">{jokes.map(joke => <ListBoxItem key={joke.id} textValue={joke.name}><Link to={`/jokes/${joke.id}`}>{joke.name}</Link></ListBoxItem>)}</ListBox></CardContent></Card>;
}

export default function App() { return <Layout><Routes><Route path="/" element={<JokePage random />} /><Route path="/jokes" element={<Catalogue />} /><Route path="/jokes/:id" element={<JokePage />} /></Routes></Layout>; }
