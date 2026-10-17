import pytest

from knockknock.jokes import JOKE_CATEGORIES, JOKES, Joke, get_joke


def test_joke_bank_has_98_unique_well_formed_jokes():
    assert len(JOKES) == 98
    assert all(isinstance(joke, Joke) for joke in JOKES)
    assert all(joke.name.strip() and joke.punchline.strip() for joke in JOKES)
    assert len({joke.name.casefold() for joke in JOKES}) == len(JOKES)
    assert len({joke.id for joke in JOKES}) == len(JOKES)


@pytest.mark.parametrize(
    ("category", "name", "punchline", "joke_id"),
    [
        ("animals", "Alpaca", "Alpaca the snacks if you open the door!", "alpaca"),
        ("animals", "Beaver", "Beaver careful—the porch is slippery!", "beaver"),
        ("animals", "Cheetah", "Cheetah later, alligator!", "cheetah"),
        ("animals", "Dolphin", "Dolphin-ately let me in!", "dolphin"),
        ("animals", "Ewe", "Ewe know I forgot my key!", "ewe"),
        ("animals", "Frog", "Frog-et me not—open up!", "frog"),
        ("animals", "Gnu", "Gnu the answer: let me in!", "gnu"),
        ("animals", "Horse", "Horse around later; it's chilly!", "horse"),
        ("animals", "Iguana", "Iguana come inside, please!", "iguana"),
        ("animals", "Jaguar", "Jaguar-d the doorbell ringing?", "jaguar"),
        ("animals", "Koala", "Koala-fied to tell you a joke!", "koala"),
        ("animals", "Llama", "Llama in before it rains!", "llama"),
        ("animals", "Marmoset", "Marmoset a plan to let me in?", "marmoset"),
        ("animals", "Newt", "Newt-ice me standing out here?", "newt"),
        ("animals", "Otter", "Otter hurry and answer!", "otter"),
        ("animals", "Penguin", "Penguin up the phone; I'm outside!", "penguin"),
        ("animals", "Rabbit", "Rabbit up—it's getting late!", "rabbit"),
        ("animals", "Sheep", "Sheepishly, I forgot my key!", "sheep"),
        ("animals", "Tiger", "Tiger later; let me in now!", "tiger"),
        ("animals", "Yak", "Yak now or yak later?", "yak"),
        ("countries", "Canada", "Canada door open for a chilly visitor?", "canada"),
        ("countries", "Chile", "Chile out here—please let me in!", "chile"),
        ("countries", "Denmark", "Denmark my words: this joke is good!", "denmark"),
        ("countries", "Egypt", "Egypt the idea? Let me in!", "egypt"),
        ("countries", "Finland", "Finland a warm spot by the door?", "finland"),
        ("countries", "Greece", "Greece me up with a welcome!", "greece"),
        ("countries", "Hungary", "Hungary for a joke and a snack!", "hungary"),
        ("countries", "India", "India mean to leave me outside?", "india"),
        ("countries", "Japan", "Japan the door open, please!", "japan"),
        ("countries", "Kenya", "Kenya let me in before it rains?", "kenya"),
        ("countries", "Laos", "Laos of laughs are waiting inside!", "laos"),
        ("countries", "Mali", "Mali I come in for a minute?", "mali"),
        ("countries", "Nepal", "Nepal-ing any chance you'll open the door?", "nepal"),
        ("countries", "Oman", "Oman, it's cold outside!", "oman"),
        ("countries", "Peru", "Peru-se the peephole; it's me!", "peru"),
        ("countries", "Qatar", "Qatar believe I'm still outside?", "qatar"),
        ("countries", "Rwanda", "Rwanda-mfully, I brought a joke!", "rwanda"),
        ("countries", "Spain", "Spain a moment and open the door?", "spain"),
        ("countries", "Turkey", "Turkey to the door, please!", "turkey"),
        ("countries", "Yemen", "Yemen-tioned you had cookies!", "yemen"),
        ("instruments", "Accordion", "Accordion to plan, you open the door!", "accordion"),
        ("instruments", "Bass", "Bass-ically, I'm here to tell a joke!", "bass"),
        ("instruments", "Cello", "Cello there—can I come in?", "cello"),
        ("instruments", "Drum", "Drum up some warmth and open the door!", "drum"),
        ("instruments", "Flute", "Flute me in before the rain starts!", "flute"),
        ("instruments", "Guitar", "Guitar-d the door for me?", "guitar"),
        ("instruments", "Harp", "Harp you glad I knocked?", "harp"),
        ("instruments", "Kazoo", "Kazoo me a favor and answer?", "kazoo"),
        ("instruments", "Lute", "Lute me in, it's chilly!", "lute"),
        ("instruments", "Mandolin", "Mandolin the doorbell ring?", "mandolin"),
        ("instruments", "Oboe", "Oboe-ver here waiting patiently!", "oboe"),
        ("instruments", "Piano", "Piano-thing, open the door!", "piano"),
        ("instruments", "Recorder", "Recorder later; let me in now!", "recorder"),
        ("instruments", "Saxophone", "Saxophone me if you can hear me!", "saxophone"),
        ("instruments", "Trombone", "Trombone to be wild—open up!", "trombone"),
        ("instruments", "Ukulele", "Ukulele me in, please!", "ukulele"),
        ("instruments", "Violin", "Violin the doorbell, didn't you?", "violin"),
        ("instruments", "Whistle", "Whistle you open the door?", "whistle"),
        ("instruments", "Xylophone", "Xylophone home, but I can wait!", "xylophone"),
        ("instruments", "Zither", "Zither you like it or not, I'm outside!", "zither"),
    ],
)
def test_new_categorized_jokes_load(category, name, punchline, joke_id):
    joke = Joke(name, punchline, joke_id)

    assert get_joke(name) == joke
    assert joke in JOKE_CATEGORIES[category]


def test_get_joke_supports_zero_based_index_and_name():
    assert get_joke(0) is JOKES[0]
    assert get_joke(JOKES[0].name.upper()) is JOKES[0]


def test_get_joke_includes_orange_joke():
    assert get_joke("orange") == Joke(
        "Orange", "Orange you glad I didn't say banana?", "orange"
    )


def test_get_joke_includes_duck_joke():
    assert get_joke("duck") == Joke(
        "Duck", "Duck you want to hear another joke?", "duck"
    )


def test_get_joke_includes_cow_joke():
    assert get_joke("cows") == Joke("Cows", "Cows go moo, that's why I knocked!", "cows")


def test_get_joke_includes_quack_joke():
    assert get_joke("quack") == Joke(
        "Quack", "Quack the door open, it's cold out here!", "quack"
    )


def test_get_joke_includes_little_old_lady_joke():
    assert get_joke("a little old lady") == Joke(
        "A little old lady",
        "I didn't know you could yodel!",
        "a-little-old-lady",
    )


@pytest.mark.parametrize(
    ("name", "punchline", "joke_id"),
    [
        ("Justin", "Justin time for dinner!", "justin"),
        ("Harry", "Harry up and open the door, it's cold!", "harry"),
        ("Ice cream", "Ice cream every time I see a ghost!", "ice-cream"),
    ],
)
def test_get_joke_includes_new_jokes(name, punchline, joke_id):
    assert get_joke(name) == Joke(name, punchline, joke_id)


@pytest.mark.parametrize("selector", [-1, len(JOKES), "not-a-joke"])
def test_get_joke_rejects_unknown_selector(selector):
    with pytest.raises((IndexError, KeyError)):
        get_joke(selector)
