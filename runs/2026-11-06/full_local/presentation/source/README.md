# Editable slide source

`content.mjs` exports `build(presentation)` and creates all twelve slides with native text, chart, table and connector objects. It was executed using the bundled `@oai/artifact-tool` JavaScript runtime and mirrored into the live presentation session. The exported PPTX is independently editable and does not require that package.

For a code rebuild in an environment with that package, create `Presentation.create({slideSize:{width:1280,height:720}})`, pass it to `build`, apply Arial to chart text with the bundled font helper, then export through `PresentationFile.exportPptx`. Use the presentation skill finalizer for package, chart workbook, native table, arithmetic, layout and font checks. The private build/runtime paths and validator receipts are not part of this publication artifact.

Data sources: `results/forecast_macro.csv`, `results/NUMERIC_CLAIMS.json`, `results/primary_complete_pair_cells.csv`, `results/secondary_quality_contrasts.csv`, `results/ig_numerical_summary.csv`, and `results/target_forecast_table.csv`. Citations and caveats are in each slide's speaker notes. Rounded values in code are presentation values, not inputs to the scientific analysis.

Native PowerPoint/Google Slides interactive editing and save/reopen tests were unavailable. All final slides were rendered and inspected; native charts, embedded data workbooks, tables, notes and diagram connectors were checked at package level.
