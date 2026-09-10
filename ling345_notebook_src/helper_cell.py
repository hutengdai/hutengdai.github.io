# =====================================================================
#  LING 345 -- the self-check.  Run this cell once, at the top.
#
#  You never need to change anything in here, and nothing is hidden
#  from you either: it is ordinary Python and you are welcome to read
#  it.  It gives you four things:
#
#      check_1(), check_2(), check_3()   mark one exercise
#      hint(1), hint(2), hint(3)         a nudge, never the answer
#      report()                          everything at once, at the end
#      show_wave(), feature_table()      pictures, used later on
# =====================================================================
import inspect
import math

import matplotlib.pyplot as plt


# --- finding your variables ------------------------------------------
# Your answers live in the notebook's own memory, not in here, so the
# checker goes and looks for them.  If it ever cannot find them, you
# can always be explicit:   check_1(globals())

def _notebook_names(given=None):
    if isinstance(given, dict):
        return given
    space = {}
    try:                                    # IPython's copy, as a backup
        from IPython import get_ipython
        user_ns = getattr(get_ipython(), "user_ns", None)
        if isinstance(user_ns, dict):
            space.update(user_ns)
    except Exception:
        pass
    frame = inspect.currentframe()          # step out of this file's own frames
    steps = 0
    while frame is not None and steps < 20:
        if frame.f_globals.get("__name__") == "__main__" and "_notebook_names" not in frame.f_locals:
            space.update(frame.f_globals)
            space.update(frame.f_locals)
            break
        frame = frame.f_back
        steps += 1
    return space


# --- what counts as an answer ----------------------------------------

def _answered(value, depth=0):
    """A leftover ... is not an answer, and neither is a list holding one."""
    if value is Ellipsis:
        return False
    if depth < 3 and isinstance(value, (list, tuple)):
        return all(_answered(x, depth + 1) for x in value)
    return True


def _same(got, want, exact_type=False):
    if isinstance(got, bool) != isinstance(want, bool):
        return False                        # True is not 1 in this course
    if exact_type and isinstance(want, float) and not isinstance(got, float):
        return False                        # 0 from // is not 0.000375 from /
    if isinstance(got, float) or isinstance(want, float):
        try:
            return math.isclose(got, want, rel_tol=1e-9, abs_tol=1e-12)
        except TypeError:
            return False
    return got == want


def _short(value):
    text = repr(value)
    return text if len(text) <= 34 else text[:31] + "..."


# --- the checker itself ----------------------------------------------
_SECTION_TITLES = {1: "Numbers, text, lists, and dictionaries",
                   2: "Making a decision",
                   3: "Your first speech recognizer"}
_SECTION_SCORES = {}


def _mark(number, wanted, hints=(), exact_type=(), needs=(), given=None):
    here = _notebook_names(given)
    missing = [n for n in needs if n not in here]
    if missing:
        print("I cannot find: " + ", ".join(missing))
        print("You have probably skipped a cell, or edited one without running it.")
        print("Fix: Runtime > Restart session and run all   (Colab)")
        print("     Kernel > Restart Kernel and Run All Cells   (Jupyter)")
        return

    rows, right = [], 0
    for name, want in wanted:
        got = here.get(name, Ellipsis)
        blank = name not in here or not _answered(got)
        ok = (not blank) and _same(got, want, name in exact_type)
        right += 1 if ok else 0
        rows.append((name, got, ok, blank))

    width = max(len(r[0]) for r in rows)
    print("Exercise %d -- %s" % (number, _SECTION_TITLES[number]))
    print("%d of %d right" % (right, len(rows)))
    print()
    print("   %-*s  %-34s  %s" % (width, "variable", "your value", "evaluation"))
    print("   " + "-" * (width + 48))
    for name, got, ok, blank in rows:
        evaluation = "correct!" if ok else ("not filled in yet" if blank else "not right yet")
        shown = "(still a blank)" if blank else _short(got)
        print("   %-*s  %-34s  %s" % (width, name, shown, evaluation))

    notes = []
    for name, got, ok, blank in rows:
        if ok or blank:
            continue
        for test, message in hints:
            try:
                hit = test(name, got)
            except Exception:
                hit = False
            if hit:
                notes.append((name, message))
                break
    if notes:
        print()
        print("   what to look at:")
        for name, message in notes:
            for i, line in enumerate(message.split("\n")):
                print("     %s %s" % (name + ":" if i == 0 else " " * (len(name) + 1), line))

    print()
    if right == len(rows):
        print("   All of them are right. Move on.")
    else:
        print("   Fix the cell above, run it again, and this check runs with it.")
        print("   Still stuck? Run  hint(%d)  in the next cell." % number)
    _SECTION_SCORES[number] = (right, len(rows))


# --- graduated hints, which never give the answer away ----------------
_HINTS = {
    1: ["Everything you need is in the demo cell just above the exercise.\n"
        "Every one of the five answers appears there in some form.",
        "num_samples counts.  last_sample uses a negative number in the\n"
        "brackets.  first_three uses a colon.  duration divides, and it has\n"
        "to keep the decimal part.  no_frequency looks a key up in the table."],
    2: ["Two things are being tested: the ORDER of the two conditions, and\n"
        "whether you wrote > or >=.",
        "Ask the narrow question first (is it above 0.5?), then the wide one\n"
        "(is it above 0.05?).  And 'above 0.05' does not include 0.05 itself."],
    3: ["The loop keeps updating the best score and the best, most plausible\n"
        "word for a new recording.  A recognizer returns a word.",
        "Note that the return indentation should be carefully placed so it is\n"
        "not inside the loop."],
}
_HINTS_GIVEN = {}


def hint(number):
    """A nudge for one exercise. Run it again for a bigger one."""
    level = _HINTS_GIVEN.get(number, 0)
    messages = _HINTS[number]
    print(messages[min(level, len(messages) - 1)])
    if level + 1 < len(messages):
        print()
        print("(run hint(%d) again for a bigger hint)" % number)
    _HINTS_GIVEN[number] = level + 1


def report():
    """Everything at once. Run this at the end, before you hand the notebook in."""
    right = total = 0
    print("=" * 64)
    print("LING 345 -- Python self-check -- your report")
    print("=" * 64)
    for number in (1, 2, 3):
        title = _SECTION_TITLES[number]
        if number in _SECTION_SCORES:
            r, n = _SECTION_SCORES[number]
            verdict = "solid" if r == n else ("nearly" if r >= n - 1 else "keep going")
            print("   Exercise %d  %-38s  %d/%d  %s" % (number, title, r, n, verdict))
            right += r
            total += n
        else:
            print("   Exercise %d  %-38s   not run yet" % (number, title))
    print("-" * 64)
    print("   TOTAL: %d of %d" % (right, total))
    print()
    if total == 12 and right == 12:
        print("   All green. Follow the hand-in instructions at the bottom.")
    else:
        print("   Anything not green: fix that exercise cell, run it again (the")
        print("   check runs with it), then run report() once more.")
    print("=" * 64)


# --- section 4 runs on the recognizer you wrote in Exercise 3 ----------

def exercise_3_done():
    """True once recognize() actually hands back a word."""
    here = _notebook_names()
    if not callable(here.get("recognize")) or "model" not in here:
        print("Section 4 uses the recognize() you write in Exercise 3.")
        print("Go back and finish Exercise 3 first, then run this cell again.")
        return False
    try:
        answer = here["recognize"](here["demo_no"], here["model"])
    except Exception as problem:
        print("Exercise 3 is not working yet: %s" % problem)
        print("Fix that cell, run it, then come back here.")
        return False
    if not isinstance(answer, str):
        print("Exercise 3 is not finished: recognize() is handing back")
        print("%r instead of a word. Fill in its last line, run that cell," % (answer,))
        print("then come back here.")
        return False
    return True


# --- pictures ---------------------------------------------------------

def show_wave(recording, title):
    """Draw one recording, with a red dot at every zero crossing."""
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.axhline(0, color="0.4", linewidth=1)
    ax.plot(range(len(recording)), recording, color="#1b1b1b",
            linewidth=1.4, marker="o", markersize=3.5)
    crossings = [i for i in range(1, len(recording))
                 if recording[i - 1] * recording[i] < 0]
    ax.plot([i - 0.5 for i in crossings], [0] * len(crossings), "o",
            color="#b3261e", markersize=8, zorder=3,
            label="zero crossing (%d in all)" % len(crossings))
    size = len(recording) // 8
    for k in range(1, 8):
        ax.axvline(k * size - 0.5, color="#7c3aed", linestyle="--",
                   linewidth=1, alpha=.5)
    top = max(abs(v) for v in recording)
    for k in range(8):
        ax.text(k * size + size / 2 - 0.5, top * 1.25, str(k),
                ha="center", color="#7c3aed", fontsize=9)
    ax.set_title('"%s"' % title)
    ax.set_xlabel("sample number")
    ax.set_ylabel("level")
    ax.set_ylim(-top * 1.5, top * 1.5)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    plt.show()


def feature_table(recording, name=""):
    """Show the work inside features(): every slice, its raw rate, its share."""
    pieces = slices(recording, 8)
    raw = [zero_crossings(p) for p in pieces]
    total = sum(raw)
    print("features(%s), one row per slice" % name)
    print()
    print("   %5s | %-26s | %7s | %7s" % ("slice", "the samples in it", "raw", "share"))
    print("   " + "-" * 56)
    for i, piece in enumerate(pieces):
        share = round(raw[i] / total, 3) if total else 0.0
        print("   %5d | %-26s | %7s | %7s" % (i, str(piece), raw[i], share))
    print("   " + "-" * 56)
    print("   %5s | %-26s | %7s | %7s" % ("total", "", round(total, 3), 1.0))


