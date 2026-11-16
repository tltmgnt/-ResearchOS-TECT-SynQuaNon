# Record contract, version 1

Records are UTF-8 JSON objects. The executable validator is `researchos.cli.validate`; evidence is additionally checked by `verify_evidence`. Additional metadata fields are retained so protocols and reviewer notes can be included.

| Field | Contract |
| --- | --- |
| schema_version | Integer 1 |
| id | 1–80 lowercase letters, digits, underscores or hyphens; first character alphanumeric |
| title, hypothesis, owner | Nonempty strings |
| data_kind | synthetic, simulation, or experimental; describes inputs |
| application | qubits, photon-detectors, or signal-processing |
| model.name | bcs-gap-toy-v1 |
| model.critical_temperature_K | Positive finite assumed candidate Tc in kelvin |
| model.baseline_critical_temperature_K | Positive finite assumed baseline Tc in kelvin |
| model.temperatures_K | 1–10000 finite nonnegative temperatures in kelvin |
| evidence | Array of objects containing relative path and lowercase SHA-256 digest; required nonempty for experimental inputs |

Evidence paths must resolve inside the record directory, including symlink resolution. Absolute paths and traversal outside that directory fail. Missing or changed evidence fails the run. Hashes in a record are declarations supplied by its author, not signatures or independent verification.

## Model

The illustrative interpolation is Δ(T) = 1.764 kB Tc tanh(1.74 sqrt(Tc/T − 1)) below Tc, with Δ(0) = 1.764 kB Tc and Δ(T ≥ Tc) = 0. kB = 0.08617333262 meV/K. This is a weak-coupling BCS-inspired toy, not a model of nanopatterning, proximity effects, disorder, strong coupling, or device dynamics. Critical temperatures are assumed inputs. Numerical output is not evidence of an enhanced critical temperature, qubit coherence, detection efficiency, or amplifier noise improvement.

## Bundle

Each run embeds the input record, input-byte SHA-256, runner and Python versions, model limitations, and result rows. Identical input bytes and runtime yield identical bundle bytes. No timestamps or random numbers are introduced. This is local reproducibility, not a signed audit trail. Original evidence files must be retained separately; bundles embed their declared hashes, not their contents. Reports summarize bundles and do not re-check external evidence; use `validate` on the original record to re-check files.
