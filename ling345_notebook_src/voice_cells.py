# -*- coding: utf-8 -*-
"""The ungraded 'real sound' cells."""

STANDIN = '''\
from IPython.display import Audio, display

fake_no = demo_audio("no")     # a hum, then a vowel
fake_go = demo_audio("go")     # a burst, then the same vowel

print('this one is meant to sound like "no":')
display(Audio(fake_no, rate=16000))
print('this one is meant to sound like "go":')
display(Audio(fake_go, rate=16000))

print()
print("These are 16000 numbers each, not 24, but features() does not care:")
print("no-ish ->", features(fake_no))
print("go-ish ->", features(fake_go))

if exercise_3_done():
    print()
    print("YOUR recognizer, on sound it has never seen:")
    print("  the no-ish recording ->", recognize(fake_no, model))
    print("  the go-ish recording ->", recognize(fake_go, model))
'''

TRIM = '''\
import random
random.seed(7)

# a real recording of "no": a second of quiet room, the word, quiet room again
quiet = [random.uniform(-0.01, 0.01) for _ in range(4000)]     # microphone noise
noisy = quiet + demo_audio("no") + quiet

clean = trim_silence(noisy)

print("before trimming:", len(noisy), "samples")
print("after trimming: ", len(clean), "samples")
print()
print("features with the quiet ends left in:", features(noisy))
print("features with the quiet ends cut off:", features(clean))
print()
if exercise_3_done():
    print("the recognizer, silence left in:", recognize(noisy, model))
    print("the recognizer, silence cut off:", recognize(clean, model))
    print()
    print("Room noise is quiet, but it crosses zero constantly, so the")
    print("silent ends look like a burst. Left in, they talk the recognizer")
    print("into hearing a 'g' in a word that has none.")
'''

RECORD = '''\
# Say the word once, clearly, right after the countdown.
# Change the word or the number of takes if you like.

my_takes = {"no": [], "go": []}

try:
    for word in ["no", "go"]:
        for take in range(3):
            print()
            print('=== say "%s"  (take %d of 3) ===' % (word, take + 1))
            sound = record(1.5)             # 1.5 seconds from your microphone
            my_takes[word].append(trim_silence(sound))
except MicrophoneError as problem:
    print(problem)                          # a plain explanation, not a crash

print()
for word in my_takes:
    print(word, "->", len(my_takes[word]), "takes,",
          [len(t) for t in my_takes[word]], "samples each")
'''

TRAIN = '''\
# TRAINING, for real this time: average the three takes of each word.

my_model = {}
for word in my_takes:
    each = [features(take) for take in my_takes[word]]          # 8 numbers per take
    if not each:                                                # nothing recorded for this word
        continue
    my_model[word] = [round(sum(f[i] for f in each) / len(each), 3)
                      for i in range(8)]                        # averaged, slice by slice

if len(my_model) < 2:
    print("There are not two words to tell apart yet.")
    print("Run the recording cell above first, or skip ahead to Way 3.")
else:
    for word in my_model:
        print(word, "->", my_model[word])
    print()
    print("Your two words differ most where these two lists differ most.")
'''

TEST = '''\
# Say either "no" or "go" after the countdown.

my_model = globals().get("my_model", {})     # empty if you skipped the cells above

try:
    test_sound = trim_silence(record(1.5))
except MicrophoneError as problem:
    test_sound = None
    print(problem)

if test_sound and len(my_model) == 2:
    guess = recognize(test_sound, my_model)            # YOUR function, your model
    print()
    print("the recognizer says:", guess)
    print()
    for word in my_model:
        print("  distance to %-3s = %.4f"
              % (word, distance(features(test_sound), my_model[word])))
    print()
    # thin the recording out before drawing it: 16000 dots is not a picture
    show_wave(test_sound[::max(1, len(test_sound) // 400)], "what you just said")
elif test_sound:
    print("Record your training takes further up before testing.")
'''

UPLOAD = '''\
# In Colab this opens a file picker and hands you the samples directly.
# In local Jupyter it shows an upload button; run the NEXT cell afterwards.

try:
    picked = upload_audio()
except MicrophoneError as problem:
    picked = None
    print(problem)

if picked is None:
    pass                                    # the message above says what to do
elif not isinstance(picked, list):
    print()
    print("Now run the next cell.")
else:
    uploaded = trim_silence(picked)         # Colab hands the samples straight back
    print(len(uploaded), "samples")
    print("features ->", features(uploaded))
    if exercise_3_done():
        print("the recognizer says:", recognize(uploaded, model))
'''
