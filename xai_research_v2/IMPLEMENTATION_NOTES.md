# Implementation notes

Before any model fitting, the first run stopped on a sanity assertion requiring more than 400 validation windows. Institution 28 had exactly 400 valid windows after the frozen coverage/context rules. A metadata/count-only audit of all 12 selected institutions showed minimum validation count 400; the assertion was corrected to accept 400. No origin, split, model, parameter grid, selection rule, loss pattern or statistical analysis changed. No series was removed.

The initial source and hash manifest are preserved in results/pilot_prefit_initial.py.txt and results/prefit_hashes_initial.json. The amended current-source hash is recorded in results/prefit_hashes.json before fitting restarted. PROTOCOL_PILOT.md and prepare_data.py retain their original hashes. This was a software assertion correction, not an outcome-driven protocol change.
