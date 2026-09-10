# -*- coding: utf-8 -*-
"""Generate the LING 345 notebook pair.

    python3 build.py /path/to/output/dir

Writes LING345_python_tutorial.ipynb (blanks) and
LING345_python_tutorial_answers.ipynb (filled in) from one shared source, so
the two can never drift apart.

nbformat 4.5 with per-cell ids; metadata carries the colab / kernelspec /
language_info blocks that let one file open warning-free in both Google Colab
and JupyterLab 4.
"""
import io
import json
import os
import re
import sys

import content_core as C
import prose as P
import voice_cells as V

GH_USER, GH_REPO, GH_BRANCH = "hutengdai", "hutengdai.github.io", "master"
STUDENT_NB = "LING345_python_tutorial.ipynb"
ANSWERS_NB = "LING345_python_tutorial_answers.ipynb"

HERE = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with io.open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


HELPER_CELL = read("helper_cell.py").rstrip("\n") + read("checks_cell.py").rstrip("\n")
AUDIO_CELL = read("audio_cell.py").rstrip("\n")


# ----------------------------------------------------------------- cells
class Builder(object):
    def __init__(self):
        self.cells = []
        self.ids = set()

    def _id(self, seed):
        base = re.sub(r"[^A-Za-z0-9_-]", "-", seed).strip("-")[:48] or "cell"
        cid, n = base, 1
        while cid in self.ids:
            n += 1
            cid = "%s-%d" % (base, n)
        self.ids.add(cid)
        return cid

    @staticmethod
    def _source(text):
        return text.strip("\n").splitlines(keepends=True) or [""]

    def md(self, text, cid=None):
        self.cells.append({"cell_type": "markdown",
                           "id": self._id(cid or text[:40]),
                           "metadata": {},
                           "source": self._source(text)})

    def code(self, text, cid=None, form_title=None, hide_in_jupyter=False):
        """form_title -> Colab shows only a titled play button; elsewhere it is a
        comment.  hide_in_jupyter -> JupyterLab 4 collapses the source; Colab and
        nbconvert ignore the key entirely."""
        meta = {}
        if form_title:
            meta["cellView"] = "form"
            text = "#@title %s\n" % form_title + text.lstrip("\n")
        if hide_in_jupyter:
            meta["jupyter"] = {"source_hidden": True}
        self.cells.append({"cell_type": "code",
                           "id": self._id(cid or text[:40]),
                           "metadata": meta,
                           "execution_count": None,
                           "outputs": [],
                           "source": self._source(text)})


def build(answers):
    b = Builder()
    nb_name = ANSWERS_NB if answers else STUDENT_NB
    colab_url = ("https://colab.research.google.com/github/%s/%s/blob/%s/%s"
                 % (GH_USER, GH_REPO, GH_BRANCH, nb_name))

    # The badge.  metadata.id == "view-in-github" is what makes Colab manage
    # this cell itself rather than showing it as content.
    b.md('<a href="%s" target="_parent">'
         '<img src="https://colab.research.google.com/assets/colab-badge.svg" '
         'alt="Open In Colab"/></a>' % colab_url, cid="view-in-github")
    b.cells[-1]["metadata"] = {"id": "view-in-github", "colab_type": "text"}

    b.md(P.TITLE_KEY if answers else P.TITLE_STUDENT, cid="title")
    b.md(P.HOWTO, cid="howto")
    b.code(HELPER_CELL, cid="setup-selfcheck",
           form_title="Run me first: the self-check (click the play button)",
           hide_in_jupyter=True)

    # ---------------------------------------------------------- section 1
    b.md(P.S1_TEACH, cid="s1-teach")
    b.code(C.DEMO_TYPES, cid="s1-demo")
    b.md(P.S1_NOTICE, cid="s1-notice")
    b.md(P.S1_TASK, cid="s1-task")
    b.code((C.EX1_FILLED if answers else C.EX1_BLANK) + "\n\ncheck_1()\n", cid="s1-exercise")
    if answers:
        b.md(P.S1_WHY, cid="s1-why")
    else:
        b.md(P.S1_HINT, cid="s1-hint-note")
        b.code("hint(1)\n", cid="s1-hint")

    # ---------------------------------------------------------- section 2
    b.md(P.S2_TEACH, cid="s2-teach")
    b.code(C.DEMO_COND, cid="s2-demo")
    b.md(P.S2_TASK, cid="s2-task")
    b.code((C.EX2_FILLED if answers else C.EX2_BLANK) + "\n\ncheck_2()\n", cid="s2-exercise")
    if answers:
        b.md(P.S2_WHY, cid="s2-why")
    else:
        b.code("hint(2)\n", cid="s2-hint")

    # ---------------------------------------------------------- section 3
    b.md(P.S3_TEACH, cid="s3-teach")
    b.md(P.S3_DATA, cid="s3-data-note")
    b.code(C.DEMO_DATA, cid="s3-data")
    b.md(P.S3_SEE, cid="s3-see")
    b.code('show_wave(no_example, "no")\nshow_wave(go_example, "go")\n', cid="s3-waves")
    b.md(P.S3_FUNCTIONS_INTRO, cid="s3-functions-intro")

    b.md(P.S3_ZC, cid="s3-zc")
    b.code(C.FN_ZERO_CROSSINGS, cid="s3-fn-zc")
    b.code(C.TRY_ZERO_CROSSINGS, cid="s3-try-zc")

    b.md(P.S3_SLICES, cid="s3-slices")
    b.code(C.FN_SLICES, cid="s3-fn-slices")
    b.code(C.TRY_SLICES, cid="s3-try-slices")

    b.md(P.S3_FEATURES, cid="s3-features")
    b.code(C.FN_FEATURES, cid="s3-fn-features")
    b.code(C.TRY_FEATURES, cid="s3-try-features")
    b.code(C.TRY_ROUND, cid="s3-try-round")
    b.md(P.S3_FEATURES_TABLE, cid="s3-features-table-note")
    b.code('feature_table(go_example, "go_example")\n\n'
           '# TRY: change go_example to no_example above and run this again.\n',
           cid="s3-feature-table")

    b.md(P.S3_DISTANCE, cid="s3-distance")
    b.code(C.FN_DISTANCE, cid="s3-fn-distance")
    b.code(C.TRY_DISTANCE, cid="s3-try-distance")

    b.md(P.S3_PLOT, cid="s3-plot-note")
    b.code(C.PLOT_CELL, cid="s3-plot")

    b.md(P.S3_HELP, cid="s3-help-note")
    b.code("help(features)\n", cid="s3-help")

    b.md(P.S3_ARGMIN, cid="s3-argmin-note")
    b.code(C.DEMO_ARGMIN, cid="s3-argmin")
    b.md(P.S3_ARGMIN_NOTICE, cid="s3-argmin-notice")

    b.md(P.S3_TASK, cid="s3-task")
    b.code((C.EX3_FILLED if answers else C.EX3_BLANK) + "\ncheck_3()\n", cid="s3-exercise")
    if answers:
        b.md(P.S3_WHY, cid="s3-why")
    else:
        b.code("hint(3)\n", cid="s3-hint")

    # ---------------------------------------------------------- section 4
    b.md(P.VOICE_INTRO, cid="s4-intro")
    b.code(AUDIO_CELL, cid="s4-audio-helper",
           form_title="Run me: the audio helper (click the play button)",
           hide_in_jupyter=True)

    b.md(P.VOICE_STANDIN, cid="s4-standin-note")
    b.code(V.STANDIN, cid="s4-standin")

    b.md(P.VOICE_TRIM, cid="s4-trim-note")
    b.code(V.TRIM, cid="s4-trim")

    b.md(P.VOICE_MIC, cid="s4-mic-note")
    b.code(V.RECORD, cid="s4-record")
    b.code(V.TRAIN, cid="s4-train")

    b.md(P.VOICE_TEST, cid="s4-test-note")
    b.code(V.TEST, cid="s4-test")

    b.md(P.VOICE_UPLOAD, cid="s4-upload-note")
    b.code(V.UPLOAD, cid="s4-upload")
    b.code('# Local Jupyter only: run this AFTER you have chosen a file above.\n'
           '# In Colab the cell above already did everything.\n'
           'if picked is None or isinstance(picked, list):\n'
           '    print("Nothing to do here -- see the cell above.")\n'
           'elif not getattr(picked, "value", None):\n'
           '    print("No file chosen yet. Click the button in the cell above,")\n'
           '    print("pick a .wav file, then run this cell again.")\n'
           'else:\n'
           '    uploaded = trim_silence(finish_upload(picked))\n'
           '    print(len(uploaded), "samples")\n'
           '    print("features ->", features(uploaded))\n'
           '    if exercise_3_done():\n'
           '        print("the recognizer says:", recognize(uploaded, model))\n',
           cid="s4-upload-finish")

    # ------------------------------------------------------------- finish
    b.md(P.BEFORE_SUBMIT, cid="report-note")
    b.code("report()\n", cid="report")
    b.md(P.SUBMIT, cid="submit")

    return {
        "cells": b.cells,
        "metadata": {
            "colab": {"name": nb_name,
                      "provenance": [],
                      "toc_visible": True,
                      "collapsed_sections": [],
                      "include_colab_link": True},
            "kernelspec": {"display_name": "Python 3",
                           "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python",
                              "version": "3.12",
                              "mimetype": "text/x-python",
                              "file_extension": ".py",
                              "codemirror_mode": {"name": "ipython", "version": 3},
                              "nbconvert_exporter": "python",
                              "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else HERE
    for answers, name in ((False, STUDENT_NB), (True, ANSWERS_NB)):
        nb = build(answers)
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
        n_code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
        print("wrote %s  (%d cells: %d code, %d markdown)"
              % (path, len(nb["cells"]), n_code, len(nb["cells"]) - n_code))
        try:
            import nbformat
            nbformat.validate(nbformat.read(path, as_version=4))
            print("   nbformat validation: OK")
        except ImportError:
            print("   nbformat not installed; validation skipped")


if __name__ == "__main__":
    main()
