# -*- coding: utf-8 -*-
"""Markdown prose for the LING 345 notebooks.

House style, taken from the instructor's own edits:
  * one line per paragraph -- do NOT hard-wrap prose
  * short; no scene-setting, no reassurance, no repeating the obvious
  * name things properly (amplitude, arguments, floor division, feature vector)
  * Colab first
  * light warmth is fine, fussiness is not

<details> blocks: the blank line after </summary> and before </details> is
load-bearing -- without it CommonMark renders the block as literal HTML.
"""

TITLE_STUDENT = """\
# A minimalistic Python tutorial

**LING 345**

This is a self-guided tutorial for Python, where you will build a very small **speech recognizer**: a program that listens to a recording and decides whether the word was *no* or *go*.

There are three exercises. Write your code to replace `...`, run the cell, and see the output.
"""

TITLE_KEY = """\
# A minimalistic Python tutorial &mdash; ANSWER KEY

**LING 345**

Every blank is filled in. Run the cells from top to bottom and all three exercises come out green.

Each exercise is followed by a **Why this answer** block explaining the code and the near-misses the checker watches for.

The student copy is `LING345_python_tutorial.ipynb`.
"""

HOWTO = """\
## Before you start: how a notebook works

A notebook is a stack of **cells**.

* **To run a cell**,  press <kbd>Shift</kbd>+<kbd>Enter</kbd>, or click the
  &#9654; button on its left.
* Cells in a notebook share one memory. A variable you make in one cell is still there in the next.
* **Order matters.** Run the cells top to bottom the first time. If Python says something
  is `not defined`, you almost certainly skipped a cell above.
* **Editing a cell changes nothing until you run it again.** This is the number one
  source of "but I fixed it!" moments.
* You can edit and re-run any cell as often as you like, learning through trials and errors.
* If you want a hard reset, do **Runtime &rarr; Restart session and run all** in Colab.
* You should copy this notebook to your own google drive for editing.

**Colab users:** the first time you edit anything, Colab offers to *Save a copy in Drive*. Say yes, or your work is not saved anywhere.

Run the next cell. It loads the self-check.
"""

S1_TEACH = """\
## 1. Numbers, text, lists, and dictionaries

`int`, `float`, `str`, `list`, `dict`

A recording is just a list of numbers. Each one is a **sample** of the amplitude of the continuous waveform.
"""

S1_NOTICE = """\
Two things worth keeping:

* `samples[-1]` counts from the **end**, so `-1` is the last item and `-2` the one before it.

* Python has **two** division signs, and they are not the same. `7 / 2` is `3.5`, keeping the
  decimal part---so called regular division. `7 // 2` is `3`, also known as floor division. You will need to choose between them below.
"""

S1_TASK = """\
### Exercise 1

Replace every `...` below with Python, then run the cell. The check at the bottom runs with it.
"""

S1_HINT = """\
Stuck? Run the next cell for a nudge, twice for a bigger one. It never gives the answer away.
"""

S1_WHY = """\
<details>
<summary><b>Why this answer</b> &mdash; click to open</summary>

`num_samples = len(samples)` &mdash; `len()` counts the items in a list, so `6`.

`last_sample = samples[-1]` &mdash; a negative index counts back from the end. `samples[len(samples) - 1]` gives the same `0.1`, but the exercise asks for the version that does not need `len()`.

`first_three = samples[:3]` &mdash; a slice stops *before* the number you write, so `:3` gives positions 0, 1 and 2. Off by one either way is the usual slip: `[:2]` gives two, `[:4]` gives four.

`duration = len(samples) / sample_rate` &mdash; regular division, one slash. `/` keeps the decimal and gives `0.000375`; `//` floors it to `0`. Six samples at 16000 Hz really is a tiny fraction of a second, and only `/` shows it.

`no_frequency = frequency["no"]` &mdash; square brackets look a key up, so `4`. `frequency.get("no", 0)` works too, since `"no"` is in the table. A `2` means you asked for `"go"`; a `0` means you used `.get()` on a key the table does not have and got the fallback.

</details>
"""

S2_TEACH = """\
## 2. Making a decision

`if` / `elif` / `else`, and conditions

The `if` statement is how Python makes decisions. Here we use it to classify a recording as
`"loud"`, `"speech"` or `"silence"` from its **peak level**: what's the maximum loudness of each recording.

Indentation matters. After a line that ends in a colon, the next line is indented by four
spaces &mdash; or you can just press <kbd>Tab</kbd>.

The code below is written as a **function**: a piece of code with a name after `def`, which takes
something in (also called arguments), such as `level` here, then outputs something with `return`.

Once we define the function, you can use it as often as you like.
"""

S2_TASK = """\
### Exercise 2

Fill in the three conditions and the three answers. The order of the tests is the exercise.
"""

S2_WHY = """\
<details>
<summary><b>Why this answer</b> &mdash; click to open</summary>

**Order is the exercise.** `0.9` is above `0.05` as well as above `0.5`, so putting `> 0.05` first swallows every loud level and `"loud"` becomes unreachable. Narrow test first, wide test second.

**`>` and not `>=`.** The docstring says *above* 0.05, and `describe(0.05)` is checked on purpose: 0.05 is not above 0.05, so it falls through to `"silence"`. `>=` makes that one case return `"speech"`, and it is the only test that catches it.

**The `else` takes no condition.** Everything that failed both tests lands there, which is the silent case.

Expected: `label_loud` &rarr; `"loud"`, `label_speech` &rarr; `"speech"`, `label_quiet` &rarr; `"silence"`, `label_edge` &rarr; `"silence"`.

</details>
"""

S3_TEACH = """\
## 3. Your first speech recognizer

everything above, in one small program

Now let's build our first speech recognizer.

Every speech recognizer, from this one to the one in your phone, has the same three jobs:

| | job | when it happens |
|---|---|---|
| **1** | **Data processing.** Turn a recording into a handful of numbers that describe it. | training *and* testing |
| **2** | **Training.** Work out what each word looks like in those numbers. | once |
| **3** | **Testing.** Score a new recording against every word, and keep the best. | every new recording |

Ours cuts each recording into eight slices and turns each slice into one number: how often the waveform crosses zero there. That is what separates **n** from **g**. [g] is a burst and flips sign on nearly every sample; [n] is a slow hum that barely crosses at all. Both words end in the same vowel, so the difference has to be at the onset.
"""

S3_DATA = """\
First, imagine we have recordings of "no" averaged into `demo_no`, and recordings of "go" averaged into `demo_go`. Now we have a new recording stored in `demo_mystery`, and our job is to recognize whether it is a no or a go.
"""

S3_SEE = """\
### Look at the two words first

The dashed purple lines mark the eight slices. Every red dot is a zero crossing. Count the dots at the left of each picture: that difference is the recognizer.
"""

S3_FUNCTIONS_INTRO = """\
### The four functions the recognizer is built from

A function can be reused over and over. It takes something in (the input), and it hands something back with `return`. Now let's write some functions as the core components of our recognizer.

Each of the next four cells defines one function, and each is followed by a **try it** cell. Run it, change the numbers, run it again.

A cell containing only a `def` prints nothing. That is normal: Python has learned the function and is waiting for you to call it.
"""

S3_ZC = """\
#### Function 1 of 4: `zero_crossings`

I essentially wrote a function called `zero_crossings` to count how often the wave crosses zero. The idea is that [g] crosses the zero more often than [n].

Walk through the recording one sample at a time. If a sample and the one before it have opposite signs, the waveform crossed zero between them. Multiplying two numbers of opposite sign gives a negative, which is what `recording[i - 1] * recording[i] < 0` tests.

Dividing by the length turns the count into a **rate**, so recordings of different lengths stay comparable.
"""

S3_SLICES = """\
#### Function 2 of 4: `slices`

One number for a whole word throws away *where* the wiggling happened, and that is the one thing separating **no** from **go**. So cut the recording into equal pieces and describe each piece separately.
"""

S3_FEATURES = """\
#### Function 3 of 4: `features`

Cut into 8 pieces, measure each piece, then divide every number by the total. What gets compared is the **shape** of the word rather than the overall rate at which it was said.

Loudness never came into it: counting sign changes ignores amplitude, so turning the volume up or down leaves these numbers unchanged.

We call this kind of information **features**, and we store them with the function `features` into a list of values. Eight numbers describing one recording is what everyone in speech technology calls a **feature vector**.
"""

S3_FEATURES_TABLE = """\
The same calculation with the work written out, one row per slice.
"""

S3_DISTANCE = """\
#### Function 4 of 4: `distance`

Two feature vectors, subtracted position by position. Each difference is squared, so `-0.2` counts as much as `+0.2` and the two cannot cancel. A **small** total means the two recordings look alike.
"""

S3_PLOT = """\
#### The decision, drawn

Look at the first two slices. `"no"` starts at `0.0`: its onset never crosses zero. `"go"` and `"mystery"` both start high. The two distances printed underneath are the decision.
"""

S3_HELP = """\
#### One notebook trick

`help(some_function)` prints what a function is for. Try `help(len)`, `help(round)`, anything. Typing `features??` in a cell shows the source code itself.
"""

S3_ARGMIN = """\
### Picking the winner

Step 3 goes through the words one at a time and holds on to the best one so far. Run this to watch that idea on its own, before you meet it inside the recognizer.
"""

S3_ARGMIN_NOTICE = """\
`float("inf")` is infinity. Every real number is below it, so the first word always wins and leaves the rest something to beat. Starting at `0` would break this, because a distance is never below zero, so no word could ever win.

Change the numbers in `scores` above, add a fourth word, run it again.
"""

S3_TASK = """\
### Exercise 3

Everything is written except the last line of `recognize`. Fill it in and run the cell.
"""

S3_WHY = """\
<details>
<summary><b>Why this answer</b> &mdash; click to open</summary>

One blank: `return best_word`.

**`best_word`, not `best_score`.** The loop keeps two things in step, the smallest distance so far and the word that earned it, and a recognizer returns the *word*. `best_score` answers `0.007777` instead of `"go"`, and the checker rejects it because a number is not a word.

**Return it *after* the loop**, at the function's own indentation. A `return` inside the `for` body quits on the first word it looks at, which here is always `"no"`.

**Why the answer is `"go"`:** the mystery recording opens with a burst that changes sign on nearly every sample, which is exactly what `features()` measures. Its first two slices come out at `0.2`, close to `"go"`'s `0.182` and far from `"no"`, which opens at `0.0`. The distances follow: `0.007777` to `"go"` against `0.054343` to `"no"`, and the smaller wins.

`answer_self` is the sanity check: `demo_no` scored against a model built from `demo_no` has distance exactly `0`, so a working recognizer has to call it `"no"`.

</details>
"""

VOICE_INTRO = """\
## 4. Now with real sound

The three exercises are done. Everything from here is ungraded.

Your recognizer does not care where its numbers come from. So far they were typed by hand; now we feed it real audio, three ways, each a fallback for the one before:

1. **A synthesized word.** Always works, no permissions needed.
2. **Your own microphone.** Works in Colab.
3. **A sound file you upload.** For when the microphone will not cooperate.

The next cell loads the audio helper, which turns sound into a list of numbers between -1.0 and 1.0.
"""

VOICE_STANDIN = """\
### Way 1: a word the computer makes up

`demo_audio("no")` and `demo_audio("go")` build a second of fake speech: a hum or a burst followed by a vowel. Listen, then hand them to the recognizer you wrote. Same `recognize()` as Exercise 3, now running on 16000 numbers instead of 24.
"""

VOICE_TRIM = """\
### Trimming the silence

Real recordings start and end with silence, and silence is mostly microphone noise, which crosses zero constantly. Left in, it swamps the eight numbers that matter.

So cut the quiet ends off before calling `features()`. Finding where speech starts and stops has a name, **endpoint detection**, and the classic version of it uses exactly what we have here: energy and zero-crossing rate.
"""

VOICE_MIC = """\
### Way 2: your own voice

Say **no** into the microphone once, right after the countdown. Do this three times, then the same for **go**. That is your training data.

Leave a moment of silence at each end. Averaging three takes of a word is a real, if tiny, version of training a speech model.

If the microphone does not work, skip these cells. Nothing below depends on them.
"""

VOICE_TEST = """\
### Now say one of them again

Run the cell, say either **no** or **go**, and watch the two distances.

No worries if this simplified model makes mistakes! Eight zero-crossing numbers is an absurdly small description of a word: no pitch, no vowel quality, no duration. The accuracy will improve if you go back and record more takes.
"""

VOICE_UPLOAD = """\
### Way 3: upload a sound file

Record a voice memo on your phone, get the file onto this computer, and load it here.

In Colab any format works, since the browser does the decoding. In local Jupyter use a `.wav`; most phones record `.m4a`, so you may need to convert it.
"""

BEFORE_SUBMIT = """\
## Your report
"""

SUBMIT = """\
## How to hand this in

**Run everything one last time.** **Runtime &rarr; Restart session and run all**. Only cells you have actually run show their output, and only what is on the screen ends up in the PDF.

**Make the PDF.** **File &rarr; Print**, set *Destination* to **Save as PDF**, then **Save**. That is the normal route; Colab has no other PDF export. (In local Jupyter: **File &rarr; Save and Export Notebook As&hellip; &rarr; HTML**, open the `.html` in a browser, then print to PDF. Do not pick "PDF" directly, which needs LaTeX and will fail.)

**Upload the PDF to Canvas.** To keep the working notebook too, use **File &rarr; Download &rarr; Download .ipynb**.

If something did not work &mdash; the microphone, a cell that will not run, anything &mdash; say so when you submit. A broken tool is my problem, not your evening.
"""
