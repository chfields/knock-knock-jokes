import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Link, Route, Routes, useNavigate, useParams } from "react-router";
import { Alert, AlertTitle, Button, Card, CardContent, CardHeader, ListBox, ListBoxItem, Radio, RadioGroup } from "@heroui/react";
import { announce } from "@react-aria/live-announcer";
import { FullJoke, getJoke, getJokes, Joke, rateJoke } from "./api";

function Layout({ children }: { children: ReactNode }) {
  return <main className="mx-auto min-h-screen max-w-3xl px-4 py-8">
    <header className="mb-8 flex items-center justify-between">
      <Link className="text-2xl font-bold" to="/">Knock-knock jokes</Link>
      <nav className="flex gap-4"><Link to="/">Random joke</Link><Link to="/jokes">Catalogue</Link></nav>
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
