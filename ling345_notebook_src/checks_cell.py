

# --- the three exercises' answers -------------------------------------

def check_1(given=None):
    """Mark Exercise 1."""
    _mark(1,
        wanted=[("num_samples", 6),
                ("last_sample", 0.1),
                ("first_three", [0.0, 0.3, -0.7]),
                ("duration", 0.000375),
                ("no_frequency", 4)],
        exact_type=("duration",),
        given=given,
        hints=[
          (lambda n, v: n == "last_sample" and v == 0.0,
           "that is samples[0], the FIRST one. A negative index counts\n"
           "back from the end."),
          (lambda n, v: n == "first_three" and v == [0.0, 0.3],
           "samples[:3] takes three, not two. Python stops BEFORE the\n"
           "number you write, so :3 gives you positions 0, 1 and 2."),
          (lambda n, v: n == "first_three" and v == [0.0, 0.3, -0.7, 0.9],
           "samples[:3] stops before position 3, so it gives you three,\n"
           "not four."),
          (lambda n, v: n == "duration" and v == 0,
           "you used // , which throws the decimal part away. Six samples\n"
           "at 16000 a second really is a tiny fraction of a second, and\n"
           "only a single / lets you see it."),
          (lambda n, v: n == "no_frequency" and v == 2,
           'that is the count for "go". Look at which key you asked for.'),
          (lambda n, v: n == "no_frequency" and v == 0,
           'a 0 means the key you asked for was not in the table. "no" IS\n'
           "in there, so ask for it by name."),
        ])


def check_2(given=None):
    """Mark Exercise 2."""
    _mark(2,
        wanted=[("label_loud", "loud"),
                ("label_speech", "speech"),
                ("label_quiet", "silence"),
                ("label_edge", "silence")],
        needs=("describe",),
        given=given,
        hints=[
          (lambda n, v: n == "label_loud" and v == "speech",
           "the wide test ran first, so the narrow one below it can never\n"
           "be reached. Put  > 0.5  above  > 0.05 ."),
          (lambda n, v: n == "label_edge" and v == "speech",
           "you used >= somewhere. Exactly 0.05 is not ABOVE 0.05, so it\n"
           'has to fall through to "silence".'),
          (lambda n, v: v is None,
           "describe() handed back None, which means some path through it\n"
           "reaches no return at all. Every branch needs one."),
        ])


def check_3(given=None):
    """Mark Exercise 3."""
    _mark(3,
        wanted=[("distance_to_no", 0.054343),
                ("answer", "go"),
                ("answer_self", "no")],
        needs=("features", "distance", "recognize", "model", "demo_no", "demo_mystery"),
        given=given,
        hints=[
          (lambda n, v: n == "answer" and v == "no",
           'it answered "no", which is the FIRST word the loop looks at.\n'
           "That happens when the return is indented inside the for loop:\n"
           "the function then quits on word one and never sees the rest.\n"
           "Move it left, so it lines up with  best_word = None  and runs\n"
           "after the loop has finished."),
          (lambda n, v: n == "answer" and v is None,
           "it never picked a word: best_word was still None at the end.\n"
           "Hand back the variable the loop filled in."),
          (lambda n, v: n == "answer" and isinstance(v, float),
           "that is the winning distance, not the winning word. The score\n"
           "lives in best_score; the word that earned it is in best_word."),
          (lambda n, v: n == "answer" and not isinstance(v, str),
           "recognize() has to hand back a word, as text. Return the\n"
           "variable holding the winning word."),
          (lambda n, v: n == "answer_self" and v == "go",
           "a stored recording has to recognize itself. Its distance from\n"
           "its own entry in the model is exactly 0, and nothing can\n"
           "beat that."),
        ])


print("Self-check ready, let's goooooooo!")
