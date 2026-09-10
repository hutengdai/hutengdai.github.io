# -*- coding: utf-8 -*-
"""Ship-ready notebooks.

The student copy ships with no outputs at all.  The answer key ships with the
outputs of the three graded sections baked in, so it can be read on GitHub or
Canvas without running it -- but with section 4 (microphone, upload) cleared,
because those outputs describe whatever machine happened to build the file.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def clear(cell):
    if cell["cell_type"] == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    cell.get("metadata", {}).pop("execution", None)
    return cell


def load(name):
    with io.open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def save(nb, path):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


def main(out_dir):
    # --- student copy: pristine, no outputs
    student = load("LING345_python_tutorial.ipynb")
    for c in student["cells"]:
        clear(c)
    save(student, os.path.join(out_dir, "LING345_python_tutorial.ipynb"))
    print("student copy: %d cells, outputs cleared" % len(student["cells"]))

    # --- answer key: executed, with the hardware section cleared
    key = load("exec_LING345_python_tutorial_answers.ipynb")
    # the executed file carries the source of the built file; keep metadata tidy
    key["metadata"] = load("LING345_python_tutorial_answers.ipynb")["metadata"]
    cleared = 0
    for c in key["cells"]:
        c.get("metadata", {}).pop("execution", None)
        if c.get("id", "").startswith("s4-"):
            clear(c)
            cleared += 1
    save(key, os.path.join(out_dir, "LING345_python_tutorial_answers.ipynb"))
    kept = sum(1 for c in key["cells"]
               if c["cell_type"] == "code" and c.get("outputs"))
    print("answer key:   %d cells, %d with outputs kept, %d section-4 cells cleared"
          % (len(key["cells"]), kept, cleared))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE)
