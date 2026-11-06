# Notebook and reproduction guide

`XAI_Replication_32.ipynb` is the new-cohort analysis notebook, separate from the original source-training notebook in `../xai_cross_institution/`. Its ordinary mode reads the delivered evaluation outputs, verifies the frozen hashes, rebuilds actual input windows, loads original locked checkpoints, executes exact Shapley and adaptive IG, evaluates both response games, independently recomputes the primary paired point, and plots uncertainty/density/denominator diagnostics.

This replication does not refit any model. Use the original 95-cell `XAI_Complete_Experiment.ipynb` or fully executed `XAI_Full_Local_Run.ipynb` for actual source training. The two notebooks address different stages and should be read together.

Install `requirements-notebook.txt` in Python 3.11, select that interpreter as the kernel, and open this folder in an existing Jupyter/VS Code frontend. Install JupyterLab separately if needed. All selected data, model checkpoints and results must accompany the notebook. Colab is not tested. The CPU implementation needs no GPU.

The last notebook cell has an opt-in full-evaluation flag that copies this project into a new sibling rerun directory and invokes the frozen evaluators there. It never overwrites the delivered snapshot. This is reproduction of already observed outcomes, not a fresh holdout. The historical manifests retain their original `unscored` state; later completion/audit records identify the executed state.

The executable inline definitions expose the saved inference wrapper, neural architecture, exact coalition allocation, response utilities, IG integrator and primary bootstrap. Full cohort selection/preparation/batch code is in `tools/` and `src/`. Do not run the historical `neural_feasibility.py` development entry point: its class is imported for inference, while its original development-training main function is retained only as byte-identical provenance.

`RESULTS_BRIEF.md` and the notebook distinguish the original eight-target estimate from the new 32-target estimate. Source/model/ISP reuse prevents independent pooling. Cases with undefined Q and failed IG remain visible. More cells, records or query count do not establish scientific novelty or publication acceptance.
