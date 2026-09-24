# Data Science / ML Engineering Exercise

Welcome, and thanks for taking the time. This is a small, self-contained exercise in
three parts. There is no hidden trick and no single "correct" solution — we are much
more interested in how you reason about a problem than in whether you produce the
cleverest possible line of code.

## Time

Please spend roughly **2–3 hours**. If you run out of time, stop and write down what
you would have done next — an honest "here's where I got to and here's my plan" is
worth more to us than a rushed, half-working submission.

## Setup

The project targets Python 3.9 and uses `pipenv`:

```bash
pipenv --python 3.9
pipenv install
pipenv run jupyter notebook
```

`pip install -r` style setups are fine too if you prefer. You may add any dependency
you want — just make sure the lockfile / requirements reflect it so we can run your
code.

## The three parts

| File | What it covers |
| --- | --- |
| `1-Natural-Numbers.ipynb` | A short algorithmic warm-up. |
| `2-FAQ.ipynb` | Read, explain, and fix a piece of broken text-similarity code. |
| `3-API.ipynb` + `app/` | Turn part 2 into a working FastAPI service with tests. |

Work through them in order — part 3 builds directly on part 2.

The API is launched with:

```bash
python app/main.py
```

and its interactive docs are at <http://localhost:8000/docs>.

Tests currently run with:

```bash
python tests/test_api.py
```

You are welcome to switch to `pytest` or any other runner if you prefer — say so in
your notes.

## What we are looking for

- **Correctness** — does it actually run, and does it give the right answer?
- **Reasoning** — the written explanations matter as much as the code. Tell us *why*.
- **Judgement** — knowing which improvements are worth making, and which are not,
  given a fixed amount of time.
- **Engineering craft** — structure, naming, testability, and knowing what you would
  do differently with more time.

You do not need to build something production-grade. You *do* need to be able to talk
us through every line you wrote.

## Submitting

Zip the folder (or push to a private repo and share a link) including:

- your completed notebooks, with output cells saved
- your `app/` and `tests/` code
- a short `NOTES.md`: what you did, what you would do next, anything you got stuck on

We will walk through your submission together in the follow-up session.
