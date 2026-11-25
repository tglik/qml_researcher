"""Planted-flaw eval: the checkers prove or refute each flaw from the spec, items are rejected when
their text leaks the flaw or does not state the spec, the screen prompt is blind to the answer, and
the report computes catch, false-kill and discrimination per pair.

    python -m unittest tests.lab.test_flaweval -v      (from the repo root)
"""
from __future__ import annotations

import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab.tools import flaweval as F  # noqa: E402

CLIFFORD = {"n_qubits": 4, "gates": [
    {"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}, {"name": "s", "qubits": [2]},
    {"name": "rz", "qubits": [3], "angle": math.pi / 2}, {"name": "cz", "qubits": [1, 3]},
    {"name": "rzz", "qubits": [0, 2], "angle": math.pi / 2}]}
PRODUCT = {"n_qubits": 3, "n_features": 3, "gates":
           [{"name": "h", "qubits": [q]} for q in range(3)]
           + [{"name": "rz", "qubits": [q], "feature": q, "scale": 1.0} for q in range(3)]}


CLIFFORD_FAMILY = {"n_qubits": 64, "layers": [
    {"name": "h", "on": "all"}, {"name": "cx", "on": "chain"}, {"name": "s", "on": "all"},
    {"name": "cz", "on": "odd_pairs"}, {"name": "h", "on": "all"}]}
KERNEL_FAMILY = {"n_qubits": 50, "layers": [
    {"name": "h", "on": "all"}, {"name": "ry", "on": "all", "feature": "qubit"},
    {"name": "rx", "on": "all", "feature": "qubit", "scale": 0.5}]}


def with_layer(spec, i, layer):
    s = copy.deepcopy(spec)
    s["layers"].insert(i, layer)
    return s


def entangled():
    s = copy.deepcopy(PRODUCT)
    s["gates"] += [{"name": "cz", "qubits": [0, 1]}, {"name": "cz", "qubits": [1, 2]},
                   {"name": "rx", "qubits": [1], "feature": 1, "scale": 1.0}]
    return s


class CheckerTest(unittest.TestCase):
    def test_clifford_circuit_is_flagged_and_t_gate_twin_is_not(self):
        self.assertTrue(F.clifford_circuit(CLIFFORD)[0])
        twin = copy.deepcopy(CLIFFORD)
        twin["gates"].insert(1, {"name": "t", "qubits": [0]})      # between H and CX: changes the output
        self.assertFalse(F.clifford_circuit(twin)[0])
        odd = copy.deepcopy(CLIFFORD)
        odd["gates"].insert(1, {"name": "rx", "qubits": [3], "angle": 0.7})
        self.assertFalse(F.clifford_circuit(odd)[0])

    def test_t_gates_that_cannot_change_the_output_are_ignored(self):
        for pos, q in ((len(CLIFFORD["gates"]), 1), (0, 0)):      # before measurement / on |0>
            twin = copy.deepcopy(CLIFFORD)
            twin["gates"].insert(pos, {"name": "t", "qubits": [q]})
            self.assertTrue(F.clifford_circuit(twin)[0], pos)

    def test_fixed_gates_after_the_last_feature_gate_do_not_count(self):
        s = copy.deepcopy(PRODUCT)
        s["gates"] += [{"name": "cz", "qubits": [0, 1]}, {"name": "cx", "qubits": [1, 2]}]
        self.assertTrue(F.product_kernel_circuit(s)[0])

    def test_families_are_checked_at_several_widths(self):
        self.assertTrue(F.check_clifford(CLIFFORD_FAMILY)[0])
        self.assertIn("widths 4, 6, 8", F.check_clifford(CLIFFORD_FAMILY)[1])
        self.assertFalse(F.check_clifford(with_layer(CLIFFORD_FAMILY, 2, {"name": "t", "on": "all"}))[0])
        self.assertTrue(F.check_product_kernel(KERNEL_FAMILY)[0])
        self.assertFalse(F.check_product_kernel(with_layer(KERNEL_FAMILY, 2, {"name": "cz", "on": "chain"}))[0])
        inst = F.instantiate(CLIFFORD_FAMILY, 6)
        self.assertEqual(sum(g["name"] == "cx" for g in inst["gates"]), 5)
        self.assertEqual(sum(g["name"] == "cz" for g in inst["gates"]), 2)     # odd pairs 1-2, 3-4

    def test_bad_families_are_refused(self):
        for spec in ({"n_qubits": 3, "layers": [{"name": "h", "on": "all"}]},
                     {"n_qubits": 8, "layers": [{"name": "cx", "on": "all"}]},
                     {"n_qubits": 8, "layers": [{"name": "h", "on": "chain"}]},
                     {"n_qubits": 8, "layers": [{"name": "foo", "on": "all"}]},
                     {"n_qubits": 8, "layers": [{"name": "ry", "on": "all", "feature": 2}]}):
            with self.assertRaises(F.SpecError, msg=spec):
                F.check_spec("clifford_only", spec)

    def test_pauli_test_is_exact(self):
        for p in (F._X, F._Y, F._Z, F._I2):
            self.assertTrue(F.is_pauli(p))
        self.assertTrue(F.is_pauli(1j * F.pauli_on(3, 1, F._Y)))
        self.assertFalse(F.is_pauli(F._H))
        self.assertFalse(F.is_pauli(F.FIXED1["t"]))

    def test_rotation_convention(self):
        m, _ = F.gate_matrix({"name": "rx", "qubits": [0], "angle": math.pi})
        self.assertTrue(F.is_pauli(m))            # RX(pi) = -iX
        m, _ = F.gate_matrix({"name": "ry", "qubits": [0], "feature": 0, "scale": 2.0}, x=[math.pi / 2])
        self.assertTrue(F.is_pauli(m))            # angle = scale * x = pi

    def test_product_kernel_numerically(self):
        self.assertTrue(F.product_kernel_circuit(PRODUCT)[0])
        self.assertFalse(F.product_kernel_circuit(entangled())[0])
        # a CZ on |00> before any rotation leaves a product state: the checker simulates, not pattern-matches
        trivial = {"n_qubits": 2, "n_features": 2, "gates": [
            {"name": "cz", "qubits": [0, 1]}, {"name": "ry", "qubits": [0], "feature": 0},
            {"name": "ry", "qubits": [1], "feature": 1}]}
        self.assertTrue(F.product_kernel_circuit(trivial)[0])

    def test_arithmetic_checkers(self):
        self.assertTrue(F.check_readout({"N": 2 ** 60, "readout": "all_amplitudes", "eps": 0.01,
                                         "classical_cost_ops": 5e20})[0])
        self.assertFalse(F.check_readout({"N": 2 ** 60, "readout": "scalar", "eps": 0.01,
                                          "classical_cost_ops": 5e20})[0])
        with self.assertRaises(F.SpecError):     # a cheap classical side is a G2 kill for both items
            F.check_readout({"N": 2 ** 20, "readout": "scalar", "eps": 0.01, "classical_cost_ops": 5e7})
        load = {"N_rows": 10 ** 9, "d": 10 ** 5, "access": "arbitrary_classical", "loads": 10 ** 6, "classical_cost_ops": 1e20}
        self.assertTrue(F.check_loading(load)[0])
        self.assertFalse(F.check_loading({**load, "access": "efficient_formula"})[0])
        deq = {"N": 10 ** 9, "rank": 50, "condition_number": 10, "eps": 0.05, "access": "sample_query", "output": "sample"}
        self.assertTrue(F.check_dequantizable(deq)[0])
        self.assertFalse(F.check_dequantizable({**deq, "access": "sparse_oracle", "rank": 10 ** 9})[0])
        self.assertFalse(F.check_dequantizable({**deq, "output": "full_vector"})[0])

    def test_bad_circuits_are_refused(self):
        for spec in ({"n_qubits": 11, "gates": [{"name": "h", "qubits": [0]}]},
                     {"n_qubits": 2, "gates": [{"name": "foo", "qubits": [0]}]},
                     {"n_qubits": 2, "gates": [{"name": "h", "qubits": [5]}]}):
            with self.assertRaises(F.SpecError, msg=spec):
                F.unitary(spec)

    def test_bad_specs_are_refused(self):
        for flaw, spec in (("product_state_kernel", {"n_qubits": 8, "layers": [{"name": "h", "on": "all"}]}),
                           ("full_readout", {"N": 10, "readout": "all", "eps": 0.1, "classical_cost_ops": 1}),
                           ("data_loading", {"N_rows": 10, "d": 2, "access": "x", "loads": 1, "classical_cost_ops": 1e16}),
                           ("dequantizable_lowrank", {"N": 10 ** 6, "rank": 5, "condition_number": 10, "eps": 0.1,
                                                      "access": "sample_query", "output": "sample"})):
            with self.assertRaises(F.SpecError, msg=spec):
                F.check_spec(flaw, spec)


def pair_texts():
    flawed = {"title": "Graph-state classifier for fraud rings",
              "claim": ("A 64 qubits circuit of H, CX, S and CZ gates prepares a graph state from each "
                        "transaction neighbourhood, and its measured parities classify fraud rings. On the bank's "
                        "data this beats gradient boosting while staying shallow enough for today's neutral-atom "
                        "hardware, with depth fixed as graphs grow."),
              "spec": CLIFFORD_FAMILY}
    tspec = with_layer(CLIFFORD_FAMILY, 2, {"name": "t", "on": "all"})
    twin = {"title": flawed["title"], "claim": flawed["claim"].replace("S and CZ", "S, CZ and T"),
            "spec": tspec}
    return flawed, twin


class ItemTest(unittest.TestCase):
    def test_valid_pair_is_accepted(self):
        flawed, twin = pair_texts()
        self.assertEqual(F.validate_pair(flawed, twin, "clifford_only"), [])

    def test_leak_and_missing_fact_are_rejected(self):
        flawed, twin = pair_texts()
        leaky = {**flawed, "claim": flawed["claim"] + " Because it is a stabilizer circuit, it trains fast."}
        self.assertTrue(any("leaks" in p for p in F.validate_pair(leaky, twin, "clifford_only")))
        missing = {**twin, "claim": twin["claim"].replace(" and T", "")}
        self.assertTrue(any("missing fact 'T'" in p for p in F.validate_pair(flawed, missing, "clifford_only")))

    def test_swapped_pair_is_rejected_by_the_checker(self):
        flawed, twin = pair_texts()
        problems = F.validate_pair(twin, flawed, "clifford_only")
        self.assertTrue(any("checker says has_flaw" in p for p in problems))

    def test_short_gate_names_match_whole_words_only(self):
        self.assertFalse(F._has("the shot budget", "h"))
        self.assertTrue(F._has("gates h, cx and s", "h"))
        self.assertTrue(F._has("1,048,576 amplitudes", "1048576"))

    def test_check_items_and_ids(self):
        flawed, twin = pair_texts()
        items = F.make_pair("clifford_only", flawed, twin, {"seat": "x", "family": "openai", "model": "m"}, "c-1")
        self.assertEqual([i["kind"] for i in items], ["flawed", "twin"])
        self.assertEqual(items[0]["id"][:-1], items[1]["id"][:-1])
        self.assertEqual(F.check_items(items), [])
        self.assertTrue(F.check_items(items[:1]))

    def test_committed_items_pass_their_checks(self):
        if F.ITEMS.exists():
            self.assertEqual(F.check_items(F.read_items(F.ITEMS)), [])


class GenerateTest(unittest.TestCase):
    def test_generation_keeps_only_checked_pairs_and_retries_with_feedback(self):
        flawed, twin = pair_texts()
        good = {"flawed_title": flawed["title"], "flawed_claim": flawed["claim"], "flawed_spec_json": json.dumps(CLIFFORD_FAMILY),
                "twin_title": twin["title"], "twin_claim": twin["claim"], "twin_spec_json": json.dumps(twin["spec"])}
        bad = {**good, "twin_spec_json": json.dumps(CLIFFORD_FAMILY)}     # twin still Clifford -> rejected
        answers = [bad, good]
        prompts = []

        def caller(seat, prompt, schema):
            prompts.append(prompt)
            return {"completed": True, "answer_text": json.dumps(answers.pop(0))}

        seat = {"id": "gen", "family": "openai", "model": "m"}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            res = F.generate(seat, ["clifford_only"], [{"id": "c-1", "title": "T", "claim": "C"}], 1, path,
                             caller=caller, log=lambda *a: None)
            rows = F.read_items(path)
        self.assertEqual(res["accepted"], 1)
        self.assertEqual(len(res["rejected"]), 1)
        self.assertIn("previous attempt was rejected", prompts[1])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["by"]["family"], "openai")


def answer(verdict, **gates):
    g = {"G1": "green", "G2": "green", "G3": "green", **gates}
    return {"completed": True, "answer_text": json.dumps({"G0": "none", **g, "verdict": verdict,
                                                          "deciding_gates": [], "note": "Clifford circuit"})}


class ScreenTest(unittest.TestCase):
    def setUp(self):
        flawed, twin = pair_texts()
        self.items = F.make_pair("clifford_only", flawed, twin, {"seat": "g", "family": "openai", "model": "m"}, "c-1")
        self.assertIn("twin_easy", self.items[1]["check"])      # H then a CX chain on |+>: a product state
        self.items[1]["check"].pop("twin_easy")                  # score it as a hard twin below

    def test_prompt_is_blind_to_spec_flaw_and_author(self):
        text = F.screen_prompt(self.items[0])
        self.assertIn(self.items[0]["claim"], text)
        self.assertNotIn('"gates"', text)
        self.assertNotIn("clifford_only", text)
        self.assertNotIn("Gottesman-Knill simulates it", text)   # the checker's evidence
        self.assertNotIn("openai", text)
        self.assertIn("## Triage mode", text)

    def test_run_resumes_and_report_scores_pairs(self):
        calls = []

        def caller(seat, prompt, schema):
            calls.append(1)
            if "CZ and T" in prompt:
                return answer("pass")
            return answer("killed", G3="red")

        seat = {"id": "screen", "family": "anthropic", "model": "m"}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            F.run(seat, self.items, out, runs=2, caller=caller, log=lambda *a: None)
            F.run(seat, self.items, out, runs=2, caller=caller, log=lambda *a: None)   # nothing new
            rows = F.read_items(out / "screens.jsonl")
        self.assertEqual(len(calls), 4)
        rep = F.report(rows, self.items)
        s = rep["seats"]["screen"]["all"]
        self.assertEqual(s["catch_rate"], 1.0)
        self.assertEqual(s["catch_rate_strict"], 1.0)
        self.assertEqual(s["false_kill_rate"], 0.0)
        self.assertEqual(s["discrimination"], 1.0)
        self.assertEqual(s["run_agreement"], 1.0)
        self.assertEqual(s["mechanism_named"], 1.0)

    def test_topic_reaction_scores_zero_discrimination(self):
        seat = {"id": "screen", "family": "anthropic", "model": "m"}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            F.run(seat, self.items, out, caller=lambda *a: answer("killed", G1="red"), log=lambda *a: None)
            rows = F.read_items(out / "screens.jsonl")
        s = F.report(rows, self.items)["seats"]["screen"]["all"]
        self.assertEqual(s["catch_rate"], 1.0)
        self.assertEqual(s["catch_rate_strict"], 0.0)   # killed at the wrong gate
        self.assertEqual(s["false_kill_rate"], 1.0)
        self.assertEqual(s["discrimination"], 0.0)

    def test_easy_twins_do_not_count_as_false_kills(self):
        self.items[1]["check"]["twin_easy"] = "easy: low-bond MPS"
        seat = {"id": "screen", "family": "anthropic", "model": "m"}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            F.run(seat, self.items, out, caller=lambda *a: answer("killed", G3="red"), log=lambda *a: None)
            rows = F.read_items(out / "screens.jsonl")
        rep = F.report(rows, self.items)["seats"]["screen"]
        self.assertIsNone(rep["all"]["false_kill_rate"])
        self.assertEqual(rep["all"]["easy_twins_excluded"], 1)
        self.assertTrue(rep["twin_kills"][0]["easy"])

    def test_bad_screen_answer_is_recorded_as_failure(self):
        seat = {"id": "screen", "family": "anthropic", "model": "m"}
        with tempfile.TemporaryDirectory() as d:
            res = F.run(seat, self.items, Path(d), caller=lambda *a: {"completed": True, "answer_text": "{}"},
                        log=lambda *a: None)
        self.assertEqual(res["failed"], 2)


if __name__ == "__main__":
    unittest.main()
