# Research plan

## Opportunity alignment

DARPA SynQuaNon targets bottom-up design and synthesis of superconducting quantum metamaterials. Its program description includes qubits at elevated temperatures/frequencies, single-photon detector arrays, and quantum-limited millimeter-wave signal processing. The full program emphasizes experimental device testing and validation. See [primary sources](SOURCES.md).

ResearchOS supplies the recordkeeping and reproducibility layer. Physical fabrication, instruments, material models, and partner laboratory access are not implemented by this repository.

| Stage | Deliverable | Acceptance evidence | Current state |
| --- | --- | --- | --- |
| Workflow foundation | Record validation, evidence hashes, toy comparison and report | Automated tests and reproducible synthetic bundle | Implemented |
| Scientific model selection | Material-specific mechanism, equations, parameter domain and uncertainty | Cited derivation, independently checked reference results | Planned |
| Experiment design | Sample/control pairs, measurement protocol, calibration, temperature and uncertainty budget | Reviewed protocol and laboratory capability confirmation | Planned |
| Material characterization | Measurements of superconductivity and transport against controls | Raw files, calibration records, repeated measurements and analysis | No data |
| Device validation | Application-specific device comparison at matched conditions | Reproducible measured metrics with uncertainty and independent review | No data |

## Metrics to define with the laboratory

- Qubits: operating temperature/frequency, relaxation and coherence times, control fidelity, thermal population, and cooling overhead under comparable conditions.
- Photon detectors: system detection efficiency, dark counts, timing jitter, recovery time, operating temperature and array yield.
- Signal processing: gain, bandwidth, input-referred noise, saturation, operating frequency/temperature and power requirements.

Specify a baseline, measurement method, units, uncertainty, and preregistered success criterion before interpreting a change as an improvement. No numerical performance target is attributed to DARPA here.

## Next scientific gate

Choose one application and a material/device mechanism; identify a qualified experimental partner; confirm the relevant solicitation or collaboration route from the current official notice. Add real protocols and evidence records before representing the project as experimentally validated. The software demo is ready to run without these inputs.
