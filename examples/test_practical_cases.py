"""Behavioral counterexamples for the three educational seams; never a broker test."""
from pathlib import Path
import tempfile
import unittest

from practical_cases import (CancelLateFill, Conflict, DelayedIdentity, FakeBroker,
                             Journal, ObserveBeforeEligibility)


class CaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='superpy-case-tests-')
        self.path = Path(self.directory.name) / 'journal.sqlite3'
        self.journal = Journal(self.path)

    def tearDown(self):
        self.journal.close()
        self.directory.cleanup()

    def delayed(self):
        broker = FakeBroker()
        model = DelayedIdentity(self.journal, broker)
        model.submit()
        report = dict(account='fixture-account', generation=1, symbol='SYNTH-US', side='Buy',
                      org_seqnum='fixture-seq', order_id='fixture-order',
                      execution_id='fixture-execution', shares=4, price='10.25')
        return model, broker, report

    def test_late_identity_and_duplicate_fill_book_once(self):
        model, broker, report = self.delayed()
        self.assertFalse(model.observe(report))
        self.assertEqual(self.journal.shares(model.key), 0)
        broker.trade.org_seqnum, broker.trade.order_id = 'fixture-seq', 'fixture-order'
        self.assertTrue(model.observe(report))
        self.assertTrue(model.observe(report))
        self.assertEqual(self.journal.shares(model.key), 4)
        self.assertEqual(len(broker.calls), 1)

    def test_account_generation_and_identity_mismatch_do_not_book(self):
        model, broker, report = self.delayed()
        broker.trade.org_seqnum, broker.trade.order_id = 'fixture-seq', 'fixture-order'
        for change in (dict(account='other'),dict(generation=2),dict(order_id='other'),dict(side='Sell')):
            self.assertFalse(model.observe({**report, **change}))
        self.assertEqual(self.journal.shares(model.key), 0)

    def test_empty_return_and_report_identifiers_do_not_match_each_other(self):
        model, _, report = self.delayed()
        self.assertFalse(model.observe({**report, 'org_seqnum':'', 'order_id':''}))
        self.assertEqual(self.journal.shares(model.key), 0)

    def test_unknown_return_and_restart_never_replay_create(self):
        broker = FakeBroker(lose_return=True)
        model = DelayedIdentity(self.journal, broker)
        self.assertFalse(model.submit())
        self.assertFalse(model.submit())
        self.journal.close()
        self.journal = Journal(self.path)
        restored = DelayedIdentity(self.journal, broker)
        self.assertFalse(restored.submit())
        self.assertEqual(len(broker.calls), 1)

    def test_conflicting_fill_keeps_original_quantity_and_price(self):
        model, broker, report = self.delayed()
        broker.trade.org_seqnum, broker.trade.order_id = 'fixture-seq', 'fixture-order'
        model.observe(report)
        with self.assertRaises(Conflict):
            model.observe({**report, 'price':'11'})
        self.assertEqual(self.journal.shares(model.key), 4)
        self.assertEqual(self.journal.db.execute('SELECT price FROM fills').fetchone()[0], '10.25')

    def test_cancel_return_is_not_terminal_and_trigger_is_not_repeated(self):
        model = CancelLateFill()
        model.fill('first', 1000)
        model.trigger()
        model.cancel_returned()
        model.trigger()
        self.assertIsNone(model.try_exit(available_shares=2000, reserved_shares=0, authorized=True, fresh_quote=True))
        self.assertEqual(model.cancel_calls, 1)

    def test_late_fill_is_included_and_exit_is_not_repeated(self):
        model = CancelLateFill()
        model.fill('first', 1000)
        model.trigger()
        model.fill('late', 500)
        model.fill('late', 500)
        model.entry_terminal(1500)
        self.assertEqual(model.try_exit(available_shares=1500, reserved_shares=0, authorized=True, fresh_quote=True), 1500)
        self.assertIsNone(model.try_exit(available_shares=1500, reserved_shares=0, authorized=True, fresh_quote=True))
        self.assertEqual(model.exit_calls, [1500])

    def test_terminal_before_execution_detail_waits_then_continues(self):
        model = CancelLateFill()
        model.fill('first', 1000)
        model.trigger()
        model.entry_terminal(1500)
        self.assertIsNone(model.try_exit(available_shares=2000, reserved_shares=0, authorized=True, fresh_quote=True))
        model.fill('late', 500)
        self.assertEqual(model.try_exit(available_shares=2000, reserved_shares=0, authorized=True, fresh_quote=True), 1500)

    def test_untriggered_position_cannot_exit(self):
        model = CancelLateFill()
        model.fill('first', 1000)
        model.entry_terminal(1000)
        self.assertIsNone(model.try_exit(available_shares=1000, reserved_shares=0, authorized=True, fresh_quote=True))
        self.assertEqual(model.exit_calls, [])

    def test_full_entry_needs_no_cancel_and_exits_after_terminal(self):
        model = CancelLateFill()
        model.fill('full', 2000)
        model.trigger()
        self.assertEqual(model.cancel_calls, 0)
        model.entry_terminal(2000)
        self.assertEqual(model.try_exit(available_shares=2000, reserved_shares=0, authorized=True, fresh_quote=True), 2000)

    def test_exit_requires_explicit_guard_inputs(self):
        model = CancelLateFill()
        with self.assertRaises(TypeError):
            model.try_exit(available_shares=2000)
        self.assertEqual(model.exit_calls, [])

    def test_available_reservations_authority_and_quote_all_gate_exit(self):
        for overrides in (dict(available_shares=999), dict(reserved_shares=501),
                          dict(authorized=False), dict(fresh_quote=False)):
            model = CancelLateFill()
            model.fill('first', 1000)
            model.trigger()
            model.entry_terminal(1000)
            arguments = dict(available_shares=1500, reserved_shares=0, authorized=True, fresh_quote=True)
            self.assertIsNone(model.try_exit(**{**arguments, **overrides}))
            self.assertEqual(model.exit_calls, [])

    def test_quantity_conflicts_are_visible(self):
        model = CancelLateFill()
        model.fill('first', 1000)
        with self.assertRaises(Conflict):
            model.fill('first', 500)
        with self.assertRaises(Conflict):
            model.entry_terminal(999)

    def test_missing_reference_preserves_deduplicated_visible_position(self):
        model = ObserveBeforeEligibility(self.journal)
        model.receive('external', 1000, '100')
        model.receive('external', 1000, '100')
        self.assertIsNone(model.plan_exit(rules_valid=False, authorized=True, fresh_quote=True, available_shares=1000))
        self.assertEqual(model.view(), dict(booked_shares=1000, eligibility='monitor_only'))

    def test_reference_return_does_not_bypass_authority_or_freshness(self):
        model = ObserveBeforeEligibility(self.journal)
        model.receive('external', 1000, '100')
        for arguments in (dict(authorized=False,fresh_quote=True),dict(authorized=True,fresh_quote=False)):
            self.assertIsNone(model.plan_exit(rules_valid=True, available_shares=1000, **arguments))
        self.assertEqual(model.plan_exit(rules_valid=True, authorized=True, fresh_quote=True, available_shares=1000), 1000)
        self.assertEqual(self.journal.shares(model.scope), 1000)  # A plan leaves the ledger unchanged.

    def test_zero_position_and_insufficient_availability_do_not_make_a_plan(self):
        model = ObserveBeforeEligibility(self.journal)
        arguments = dict(rules_valid=True, authorized=True, fresh_quote=True)
        self.assertIsNone(model.plan_exit(available_shares=1000, **arguments))
        model.receive('external', 1000, '100')
        self.assertIsNone(model.plan_exit(available_shares=999, **arguments))
        self.assertEqual(model.plan_exit(available_shares=1000, **arguments), 1000)

    def test_invalid_preflight_values_cannot_authorize_an_exit(self):
        oco = CancelLateFill()
        oco.fill('first', 1000)
        oco.trigger()
        oco.entry_terminal(1000)
        arguments = dict(available_shares=1000, reserved_shares=0, authorized=True, fresh_quote=True)
        for change in (dict(available_shares=float('nan')), dict(reserved_shares=-1), dict(authorized='False')):
            with self.assertRaises(ValueError):
                oco.try_exit(**{**arguments, **change})
        self.assertEqual(oco.exit_calls, [])

    def test_reference_absence_and_restart_do_not_erase_or_double_book(self):
        model = ObserveBeforeEligibility(self.journal)
        model.receive('external', 1000, '100')
        self.journal.close()
        self.journal = Journal(self.path)
        restored = ObserveBeforeEligibility(self.journal)
        restored.receive('external', 1000, '100')
        self.assertEqual(restored.view()['booked_shares'], 1000)
        self.assertEqual(restored.view()['eligibility'], 'monitor_only')

    def test_malformed_quantities_never_become_fills(self):
        model = ObserveBeforeEligibility(self.journal)
        for value in (True, 1.5, 0, -1):
            with self.assertRaises(ValueError):
                model.receive('bad', value, '100')
        self.assertEqual(model.view()['booked_shares'], 0)


if __name__ == '__main__':
    unittest.main()
