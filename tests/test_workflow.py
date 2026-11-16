import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from researchos.cli import ValidationError, digest, gap_meV, read_json, report, run, validate, verify_evidence

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/synthetic-qubit.json'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.record = read_json(EXAMPLE)

    def test_gap_boundaries(self):
        self.assertAlmostEqual(gap_meV(0, 2), 1.764 * 0.08617333262 * 2)
        self.assertEqual(gap_meV(2, 2), 0)
        self.assertEqual(gap_meV(3, 2), 0)
        self.assertGreater(gap_meV(.1, 2), gap_meV(1, 2))

    def test_invalid_records(self):
        mutations = [lambda r: r.pop('owner'),
                     lambda r: r.update(id='../escape'),
                     lambda r: r.update(schema_version=True),
                     lambda r: r.update(data_kind='experimental'),
                     lambda r: r['model'].update(critical_temperature_K=0),
                     lambda r: r['model'].update(temperatures_K=[float('nan')]),
                     lambda r: r['model'].update(temperatures_K=[True]),
                     lambda r: r['model'].update(temperatures_K=[-1])]
        for mutate in mutations:
            r = copy.deepcopy(self.record)
            mutate(r)
            with self.subTest(record=r), self.assertRaises(ValidationError):
                validate(r)

    def test_evidence_tampering_and_containment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data.csv').write_bytes(b'real data')
            self.record['evidence'] = [{'path': 'data.csv', 'sha256': digest(b'real data')}]
            verify_evidence(validate(self.record), root)
            (root / 'data.csv').write_bytes(b'changed')
            with self.assertRaises(ValidationError):
                verify_evidence(self.record, root)
            for path in ('../outside', '/etc/passwd'):
                self.record['evidence'][0]['path'] = path
                with self.assertRaises(ValidationError):
                    verify_evidence(self.record, root)
            (root / 'link').symlink_to(root.parent)
            self.record['evidence'][0]['path'] = 'link/outside'
            with self.assertRaises(ValidationError):
                verify_evidence(self.record, root)

    def test_reproducible_bundle_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / 'one.json', Path(tmp) / 'two.json'
            run(EXAMPLE, first)
            run(EXAMPLE, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            bundle = read_json(first)
            self.assertEqual(bundle['input_sha256'], digest(EXAMPLE.read_bytes()))
            self.assertIn('synthetic illustration', report(bundle))
            self.assertEqual(len(bundle['results']), 8)
            with self.assertRaises(FileExistsError):
                run(EXAMPLE, first)

    def test_cli_end_to_end_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / 'bundle.json'
            for args in (['validate', str(EXAMPLE)], ['run', str(EXAMPLE), '--output', str(bundle)], ['report', str(bundle)]):
                result = subprocess.run([sys.executable, '-m', 'researchos', *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            bad = Path(tmp) / 'bad.json'
            bad.write_text('{"value": NaN}')
            result = subprocess.run([sys.executable, '-m', 'researchos', 'validate', str(bad)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('non-finite', result.stderr)


if __name__ == '__main__':
    unittest.main()
