# Editable presentation source

`content_v4.mjs` builds the 17-slide combined study deck using native tables, charts and the requested editable pipeline. `build_v4.mjs` loads the replication REPORT_FACTS.json and exports/validates a new PPTX with the bundled @oai/artifact-tool JavaScript runtime. The file is editable in PowerPoint.

Set WORKSPACE_DIR, PRESENTATION_SKILL_DIR, RUNTIME_NODE, RUNTIME_NODE_MODULES and RUNTIME_PYTHON from Codex load_workspace_dependencies. Set BUILD_DIR to a new private directory and FINAL_PPTX to a new output filename for each revision. Link the source directory's node_modules to RUNTIME_NODE_MODULES when running as a local module. The finalizer deliberately refuses overwriting a completed export. This is the bundled artifact runtime, not a claim of a generic public npm installation workflow.

The original content.mjs and v2 deck describe the original eight-target study. The v4 deck distinguishes it from the additional 32-target replication. Chart workbooks are literal data snapshots, not links to external workbooks. No native PowerPoint application test was performed.
