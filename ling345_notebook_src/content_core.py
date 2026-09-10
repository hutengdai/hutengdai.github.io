"""Shared prose + code content for the LING 345 notebook pair.

Everything the two notebooks have in common lives here so the student copy and
the answer key can never drift apart.  build_notebooks.py turns this into .ipynb.
"""

# ---------------------------------------------------------------- section 3 data
DEMO_DATA = '''\
# Three demo recordings, typed out by hand rather than recorded, so that the
# numbers below come out the same for everybody.  Your own voice goes through
# this very same code later on.

demo_no = [0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5,    # n: one slow swing, up then down
           0.8, 0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8,    # then the vowel: a faster wave
           0.8, 0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8]    # 24 samples in all

demo_go = [0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5,    # g: a burst, up down up down
           0.8, 0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8,    # then the very same vowel
           0.8, 0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8]    # 24 samples in all

demo_mystery = [0.5, -0.5, 0.5, -0.5, 0.5, -0.5,              # a burst again, a shorter one
                0.8, 0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8,   # and the vowel
                0.8, 0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8,
                0.8, 0.8]                                     # 24 samples, so which word is it?

print("no     ", len(demo_no), "samples")
print("go     ", len(demo_go), "samples")
print("mystery", len(demo_mystery), "samples")
'''

FN_ZERO_CROSSINGS = '''\
def zero_crossings(recording):
    """How often the wave changes sign, per sample."""
    if len(recording) < 2:                       # too short to cross anything
        return 0.0
    crossings = 0                                # nothing counted yet
    for i in range(1, len(recording)):           # every sample except the first
        if recording[i - 1] * recording[i] < 0:  # one up and the next down: a crossing
            crossings = crossings + 1            # count it
    return round(crossings / len(recording), 3)  # per sample, so length does not matter
'''

TRY_ZERO_CROSSINGS = '''\
# Try it.  Change these lists and run the cell again -- that is the whole point
# of a notebook.  Which one wiggles more?

print("a slow wave  [1, 1, -1, -1] ->", zero_crossings([1, 1, -1, -1]))
print("a fast wave  [1, -1, 1, -1] ->", zero_crossings([1, -1, 1, -1]))
print("flat silence [0, 0,  0,  0] ->", zero_crossings([0, 0, 0, 0]))
print()
print("the whole word 'no' ->", zero_crossings(demo_no))
print("the whole word 'go' ->", zero_crossings(demo_go))
'''

FN_SLICES = '''\
def slices(recording, how_many):
    """Cut a recording into `how_many` equal pieces, in order."""
    size = len(recording) // how_many                        # how many samples in each piece
    pieces = []                                              # collect them here
    for i in range(how_many):                                # one piece at a time
        pieces.append(recording[i * size:(i + 1) * size])    # from here up to there
    return pieces                                            # the pieces, in order
'''

TRY_SLICES = '''\
# Try it.  Cut a short list into 4 pieces so you can see the shape of the answer.

for piece in slices([1, 2, 3, 4, 5, 6, 7, 8], 4):
    print(piece)

print()
print("the word 'no', cut into 8 pieces:")
for piece in slices(demo_no, 8):
    print(piece)
'''

FN_FEATURES = '''\
def features(recording):
    """Describe one recording with 8 numbers: how fast it wiggles, start to end."""
    numbers = []                                     # start with none
    for piece in slices(recording, 8):               # walk the word from start to end
        numbers.append(zero_crossings(piece))        # how fast the wave wiggles here
    total = sum(numbers)                             # one voice can wiggle more than another
    if total == 0:                                   # a silent recording: nothing to scale
        return numbers
    shares = []                                      # each slice's share of the total
    for n in numbers:
        shares.append(round(n / total, 3))           # so compare the shape, not the size
    return shares
'''

TRY_FEATURES = '''\
# Try it.  These three lines are the heart of the recognizer -- read them before
# you go on.  The words differ at the START, which is where n and g live.

print("no      ->", features(demo_no))
print("go      ->", features(demo_go))
print("mystery ->", features(demo_mystery))
'''

FN_DISTANCE = '''\
def distance(a, b):
    """How far apart two lists of eight numbers are.  Small = they look alike."""
    total = 0.0                                  # nothing added up yet
    for i in range(len(a)):                      # a[0] against b[0], and so on
        total = total + (a[i] - b[i]) ** 2       # squared, so + and - cannot cancel
    return total                                 # a small total means the two look alike
'''

TRY_DISTANCE = '''\
# Try it.  A thing is always distance 0 from itself.

print("no      vs no  ->", distance(features(demo_no), features(demo_no)))
print("no      vs go  ->", distance(features(demo_no), features(demo_go)))
print()
print("mystery vs no  ->", distance(features(demo_mystery), features(demo_no)))
print("mystery vs go  ->", distance(features(demo_mystery), features(demo_go)))
print()
print("Which of the last two is smaller?  That is the answer the recognizer has to give.")
'''

PLOT_CELL = '''\
# A picture of what the recognizer actually hears.  Nothing to fill in here --
# just run it.  Top row: the raw recordings.  Bottom row: the 8 feature numbers.

import matplotlib.pyplot as plt

recordings = [("no", demo_no), ("go", demo_go), ("mystery", demo_mystery)]
fig, axes = plt.subplots(2, 3, figsize=(11, 4.6))

for col, (name, rec) in enumerate(recordings):
    axes[0][col].plot(rec, marker=".")
    axes[0][col].axhline(0, color="grey", linewidth=.8)
    axes[0][col].set_title('"%s" -- the wave' % name)
    axes[0][col].set_ylim(-1, 1)

    axes[1][col].bar(range(8), features(rec))
    axes[1][col].set_title('"%s" -- the 8 features' % name)
    axes[1][col].set_xlabel("slice, start to end")
    axes[1][col].set_ylim(0, .25)

fig.tight_layout()
plt.show()

print("distance from the mystery recording to 'no':", distance(features(demo_mystery), features(demo_no)))
print("distance from the mystery recording to 'go':", distance(features(demo_mystery), features(demo_go)))
print("Smaller means more alike, so the answer has to be 'go'.")
'''

DEMO_ARGMIN = '''\
scores = {"no": 0.42, "go": 0.07, "up": 0.31}   # one distance per word

best_word = None              # nothing chosen yet
best_score = float("inf")     # bigger than every real number

for word in scores:                    # one word at a time
    print("looking at", word, scores[word])
    if scores[word] < best_score:      # closer than the best so far?
        best_word = word               # then this is the new best
        best_score = scores[word]      # and this is the score to beat now

print()
print("the closest word:", best_word)
'''

DEMO_TYPES = '''\
samples = [0.0, 0.3, -0.7, 0.9, -0.2, 0.1]
sample_rate = 16000             # int: samples per second
word = "no"                     # str: text goes in quotes

print("how many samples: ", len(samples))
print("the first one:    ", samples[0])
print("the last one:     ", samples[-1])
print("the first three:  ", samples[:3])
print("how long, seconds:", len(samples) / sample_rate)

# a dictionary is a lookup table:
frequency = {"no": 4, "go": 2}
print("the frequency of 'no':", frequency["no"])

# .get(key, 0) hands back a fallback 0 instead of an error when the key is
# missing from the dictionary -- so a missing word gives 0, not a crash
print("the frequency of 'up':", frequency.get("up", 0))
'''

DEMO_COND = '''\
def describe(level):
    if level > 0.5:
        return "loud"
    elif level > 0.05:
        return "speech"
    else:
        return "silence"


for x in [0.9, 0.2, 0.01]:
    print(x, "->", describe(x))
'''

# ------------------------------------------------------- exercises: blank / filled
EX1_BLANK = '''\
samples = [0.0, 0.3, -0.7, 0.9, -0.2, 0.1]
sample_rate = 16000

num_samples = ...       # how many samples there are
last_sample = ...       # the last sample, WITHOUT using len()
first_three = ...       # a list of the first three samples
duration = ...          # how long the recording lasts, in seconds.
                        # This one must come out as a decimal, not a whole
                        # number, so think about which kind of division.

frequency = {"no": 4, "go": 2}
no_frequency = ...      # how many times "no" was said, looked up in the table above
'''

EX1_FILLED = '''\
samples = [0.0, 0.3, -0.7, 0.9, -0.2, 0.1]
sample_rate = 16000

num_samples = len(samples)             # how many samples there are
last_sample = samples[-1]              # the last sample, WITHOUT using len()
first_three = samples[:3]              # a list of the first three samples
duration = len(samples) / sample_rate  # how long the recording lasts, in seconds.
                                       # This one must come out as a decimal, not a
                                       # whole number, so think about which kind of
                                       # division.

frequency = {"no": 4, "go": 2}
no_frequency = frequency["no"]         # how many times "no" was said, looked up in the table above
'''

EX2_BLANK = '''\
def describe(level):
    """Three answers: "loud" above 0.5, "speech" above 0.05,
    otherwise "silence".
    """
    if ...:
        return ...
    elif ...:
        return ...
    else:
        return ...


# do not change these four lines
label_loud = describe(0.9)
label_speech = describe(0.2)
label_quiet = describe(0.01)
label_edge = describe(0.05)
'''

EX2_FILLED = '''\
def describe(level):
    """Three answers: "loud" above 0.5, "speech" above 0.05,
    otherwise "silence".
    """
    if level > 0.5:
        return "loud"
    elif level > 0.05:
        return "speech"
    else:
        return "silence"


# do not change these four lines
label_loud = describe(0.9)
label_speech = describe(0.2)
label_quiet = describe(0.01)
label_edge = describe(0.05)
'''

EX3_BLANK = '''\
# STEP 2, TRAINING.  The model is everything the machine knows about each
# word, and ours is just those 8 numbers.

model = {"no": features(demo_no), "go": features(demo_go)}   # one entry per word


# STEP 3, TESTING.  The loop below has the same shape as the demo above.

def recognize(recording, model):
    # do not change these two lines
    best_word = None             # nothing chosen yet
    best_score = float("inf")    # bigger than every real distance

    for word in model:           # "no", then "go"
        score = distance(features(recording), model[word])
        if score < best_score:   # closer than the best so far?
            best_word = word     # then this is the new best
            best_score = score   # and this is the score to beat now

    return ...                   # hand back whichever word ended up closest


# do not change these three lines
distance_to_no = distance(features(demo_mystery), model["no"])
answer = recognize(demo_mystery, model)
answer_self = recognize(demo_no, model)

print("distance from the mystery recording to 'no':", distance_to_no)
print("the recognizer says the mystery word is:    ", answer)
print("and 'no' recognizes itself as:              ", answer_self)
'''

EX3_FILLED = EX3_BLANK.replace(
    "    return ...                   # hand back whichever word ended up closest",
    "    return best_word             # hand back whichever word ended up closest")
