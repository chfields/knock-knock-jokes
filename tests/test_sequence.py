from knockknock.jokes import JOKES
from knockknock.sequence import tell


def test_tell_builds_the_classic_five_line_sequence():
    joke = JOKES[0]

    assert tell(joke) == [
        "Knock knock.",
        "Who's there?",
        f"{joke.name}.",
        f"{joke.name} who?",
        joke.punchline,
    ]
