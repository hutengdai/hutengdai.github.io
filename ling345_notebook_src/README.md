# Source for the LING 345 notebooks

The two notebooks at the repo root are **generated** from these files, so the
student copy and the answer key can never drift apart. Edit here, not in the
`.ipynb`.

    python3 build.py .          # writes both .ipynb next to build.py
    jupyter nbconvert --to notebook --execute --allow-errors \
        --output exec_LING345_python_tutorial_answers.ipynb \
        LING345_python_tutorial_answers.ipynb
    python3 finalize.py ../     # ships them to the repo root

| file | what is in it |
|---|---|
| `content_core.py` | the demo cells, the four provided functions, and both versions of each exercise (blank / filled in) |
| `prose.py` | every markdown cell |
| `helper_cell.py` | the self-check machinery, `hint()`, `report()`, `show_wave()`, `feature_table()` |
| `checks_cell.py` | the 12 expected answers and the near-miss hints |
| `audio_cell.py` | microphone, upload, WAV parsing, `demo_audio()`, `trim_silence()` |
| `voice_cells.py` | the ungraded section 4 cells |
| `build.py` | assembles both notebooks, incl. Colab badge + metadata |
| `finalize.py` | strips the student copy, bakes the answer key's outputs in |

`finalize.py` keeps the answer key's outputs for sections 1-3 (so it reads
correctly on GitHub without being run) and clears section 4's, because those
outputs describe whatever machine built the file.

This folder is not part of the website. Delete it if you would rather not keep it.
