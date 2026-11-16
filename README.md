# ResearchOS TECT — Synthetic Quantum Nanostructures

Reproducible modeling, experiment tracking, and evidence-linked validation of superconducting quantum metamaterials, aligned with DARPA SynQuaNon research goals for qubits, single-photon detectors, and quantum-limited signal processing.

## Status and scope

Version 0.1 provides a working command-line research workflow: validate an experiment record, verify attached evidence, run an illustrative model, capture a reproducible result bundle, and generate a Markdown report. TECT is retained as the project identifier; its expansion has not been specified.

This is an independent research workspace, with no claimed DARPA affiliation, award, or validated material/device result. The included example is synthetic. It demonstrates software behavior, not superconducting metamaterial feasibility. No open solicitation or submission deadline is asserted.

## Quick start

Python 3.10 or newer; the runner has no third-party runtime dependencies. From the repository root:

```bash
python -m researchos validate examples/synthetic-qubit.json
python -m researchos run examples/synthetic-qubit.json --output runs/demo.json
python -m researchos report runs/demo.json > runs/report.md
python -m unittest discover -s tests -v
```

Optional installation enables the `researchos` command:

```bash
python -m pip install .
researchos --help
```

Use a new output filename for each run. Existing bundles are never overwritten. Bundles and local reports are excluded from Git by default.

## Workflow

1. Copy the example record and assign an ID, owner, hypothesis, application, and honest input data kind.
2. Record model parameters with explicit units. The sole bundled model is a toy BCS gap interpolation with assumed critical temperatures.
3. For evidence, place files under the record directory, run `python -m researchos hash path/to/file`, and add each relative path and digest to `evidence`.
4. Validate, run, and generate the report using the commands above.
5. Review the evidence and limitations before making scientific claims. The report always labels model output as a synthetic illustration, even if the input record references experimental evidence.

Checksums detect file changes; they do not establish authenticity, measurement quality, or scientific validity. Record review and experimental assessment remain human tasks.

## Repository guide

| Path | Purpose |
| --- | --- |
| `researchos/cli.py` | Validation, SHA-256 evidence checks, deterministic model runner, reporting |
| `examples/synthetic-qubit.json` | Runnable synthetic experiment record |
| `tests/test_workflow.py` | Boundary, integrity, reproducibility and CLI tests |
| `docs/RESEARCH_PLAN.md` | Opportunity alignment, milestones, and evidence gates |
| `docs/RECORDS.md` | Record contract and model limitations |
| `docs/SOURCES.md` | Primary sources and opportunity status caveat |
| `.github/workflows/ci.yml` | Python version matrix and synthetic report artifacts |

## Development

Run `python -m unittest discover -s tests -v` before submitting changes. Add physical models only with a cited derivation, parameter domain, units, baseline, and independent validation checks. Preserve the distinction between synthetic, simulation, and experimental inputs. See [CONTRIBUTING.md](CONTRIBUTING.md).

Licensed under the existing [Apache License 2.0](LICENSE).
