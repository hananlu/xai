# Notebook authoring and execution tools

- `build_complete_notebook.py` creates the full notebook with visible core implementations mirrored from this project's canonical scripts. It resets notebook outputs; preserve any executed notebook before rebuilding it. The frozen source scripts are not changed.
- `execute_notebook.py` runs a notebook with nbclient and a real installed kernel, validates it and writes a separate executed output. Example from the project directory:

```sh
python tools/execute_notebook.py XAI_Complete_Experiment.ipynb --kernel python3 --output XAI_Complete_Executed.ipynb
```

Use a kernel with requirements-notebook.txt installed. Full-reproduction notebook flags determine whether training and batch evaluation run; the light notebook default keeps those off. The complete notebook needs the project data/models/results beside it.

Presentation content authoring source is in `presentation/source/content.mjs`; LaTeX and reusable BibTeX sources are in `paper/`.
