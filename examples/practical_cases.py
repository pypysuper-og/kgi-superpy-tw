"""Three synthetic, standard-library-only seams. No SDK, network or real orders.

These deliberately small models explain application decisions, not SDK contracts.
All quantities at these boundaries are normalized integer shares.
"""
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import argparse
import json
import sqlite3
import tempfile


class Conflict(ValueError):
    """An observation conflicts with an already confirmed fact."""


def positive_integer(value):
    if type(value) is not int or value <= 0:
        raise ValueError('Expected positive integer shares')
    return value


def nonnegative_integer(value):
    if type(value) is not int or value < 0:
        raise ValueError('Expected nonnegative integer shares')
    return value


def confirmed_flags(*values):
    if any(type(value) is not bool for value in values):
        raise ValueError('Expected explicit boolean decisions')


class Journal:
    """One local writer; prices stay decimal text, repeated fills stay idempotent."""

    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS intents (
                key TEXT PRIMARY KEY, account TEXT, generation INTEGER, outcome TEXT);
            CREATE TABLE IF NOT EXISTS fills (
                scope TEXT, execution TEXT, shares INTEGER, price TEXT,
                PRIMARY KEY(scope, execution));
        ''')

    def prepare(self, key, account, generation):
        with self.db:
            cursor = self.db.execute('INSERT OR IGNORE INTO intents VALUES (?,?,?,?)',
                                     (key, account, generation, 'unknown'))
        return cursor.rowcount == 1

    def returned(self, key):
        with self.db:
            self.db.execute("UPDATE intents SET outcome='returned' WHERE key=?", (key,))

    def book(self, scope, execution, shares, price):
        positive_integer(shares)
        price = Decimal(str(price))
        if not execution or not price.is_finite() or price <= 0:
            raise ValueError('Invalid execution identity or price')
        prior = self.db.execute('SELECT shares,price FROM fills WHERE scope=? AND execution=?',
                                (scope, execution)).fetchone()
        if prior:
            if prior[0] != shares or Decimal(prior[1]) != price:
                raise Conflict('Same execution identity has conflicting content')
            return False
        with self.db:
            self.db.execute('INSERT INTO fills VALUES (?,?,?,?)',
                             (scope, execution, shares, str(price)))
        return True

    def shares(self, scope):
        return self.db.execute('SELECT COALESCE(SUM(shares),0) FROM fills WHERE scope=?',
                                (scope,)).fetchone()[0]

    def close(self):
        self.db.close()


@dataclass
class MutableTrade:
    org_seqnum: str = ''
    order_id: str = ''


class FakeBroker:
    def __init__(self, *, lose_return=False):
        self.calls = []
        self.trade = MutableTrade()
        self.lose_return = lose_return

    def create(self, key):
        self.calls.append(key)
        if self.lose_return:
            raise TimeoutError('Synthetic lost return, effect indeterminate')
        return self.trade


class DelayedIdentity:
    """Retain the mutable return; never infer 'not sent' from missing identifiers."""

    def __init__(self, journal, broker, *, account='fixture-account', generation=1):
        self.journal, self.broker = journal, broker
        self.account, self.generation = account, generation
        self.key = 'fixture-intent'
        self.trade = None

    def submit(self):
        if not self.journal.prepare(self.key, self.account, self.generation):
            return False  # Existing intent requires reconciliation, including after restart.
        try:
            self.trade = self.broker.create(self.key)
        except TimeoutError:
            return False  # The durable unknown intent remains; no repeat create.
        self.journal.returned(self.key)
        return True

    def observe(self, report):
        # In a real adapter, also verify market, transaction class, order quantity
        # and date under that market's documented identity contract.
        if (report.get('account'), report.get('generation')) != (self.account, self.generation):
            return False
        if report.get('symbol') != 'SYNTH-US' or report.get('side') != 'Buy':
            return False
        if not self.trade or not self.trade.org_seqnum or not self.trade.order_id:
            return False
        if (report.get('org_seqnum'), report.get('order_id')) != (self.trade.org_seqnum, self.trade.order_id):
            return False
        self.journal.book(self.key, report['execution_id'], report['shares'], report['price'])
        return True


class CancelLateFill:
    """A canceled entry can have a nonzero final fill. Cancellation return is not terminal."""

    def __init__(self, ordered_shares=2000):
        self.ordered_shares = positive_integer(ordered_shares)
        self.fills = {}
        self.triggered = False
        self.cancel_calls = 0
        self.final_cumulative = None
        self.exit_attempted = False
        self.exit_calls = []

    def fill(self, execution, shares):
        positive_integer(shares)
        if execution in self.fills:
            if self.fills[execution] != shares:
                raise Conflict('Conflicting execution quantity')
            return
        cumulative = sum(self.fills.values()) + shares
        if cumulative > self.ordered_shares or (self.final_cumulative is not None and cumulative > self.final_cumulative):
            raise Conflict('Fill exceeds the confirmed quantity bound')
        self.fills[execution] = shares

    def trigger(self):
        self.triggered = True
        if (sum(self.fills.values()) < self.ordered_shares
                and not self.cancel_calls and self.final_cumulative is None):
            self.cancel_calls += 1

    def cancel_returned(self):
        pass  # A synchronous return supplies no final cumulative-fill evidence.

    def entry_terminal(self, cumulative_filled):
        if type(cumulative_filled) is not int or not sum(self.fills.values()) <= cumulative_filled <= self.ordered_shares:
            raise Conflict('Invalid terminal cumulative quantity')
        if self.final_cumulative is not None and self.final_cumulative != cumulative_filled:
            raise Conflict('Conflicting terminal watermark')
        self.final_cumulative = cumulative_filled

    def try_exit(self, *, available_shares, reserved_shares, authorized, fresh_quote):
        nonnegative_integer(available_shares)
        nonnegative_integer(reserved_shares)
        confirmed_flags(authorized, fresh_quote)
        filled = sum(self.fills.values())
        if not self.triggered or self.exit_attempted or self.final_cumulative is None:
            return None
        if filled != self.final_cumulative or not filled:
            return None  # A terminal report before complete execution detail is insufficient.
        if not authorized or not fresh_quote or available_shares-reserved_shares < filled:
            return None
        # Memory-only teaching boundary. A real dispatcher must persist this
        # intent and reconcile it after restart before touching the SDK.
        self.exit_attempted = True
        self.exit_calls.append(filled)
        return filled


class ObserveBeforeEligibility:
    """Book confirmed facts independently from the authority to plan a new exit."""

    def __init__(self, journal):
        self.journal = journal
        self.scope = 'fixture-account:fixture-day:SYNTH-TW'
        self.eligibility = 'monitor_only'

    def receive(self, execution, shares, price):
        # Input identity/account/day/class are assumed validated by the adapter.
        return self.journal.book(self.scope, execution, shares, price)

    def plan_exit(self, *, rules_valid, authorized, fresh_quote, available_shares):
        nonnegative_integer(available_shares)
        confirmed_flags(rules_valid, authorized, fresh_quote)
        position = self.journal.shares(self.scope)
        eligible = rules_valid and authorized and fresh_quote and available_shares >= position > 0
        self.eligibility = 'auto_exit_enabled' if eligible else 'monitor_only'
        return position if eligible else None

    def view(self):
        return dict(booked_shares=self.journal.shares(self.scope), eligibility=self.eligibility)


def demonstrate(case):
    with tempfile.TemporaryDirectory(prefix='superpy-synthetic-') as directory:
        journal = Journal(Path(directory) / 'case.sqlite3')
        try:
            if case == 'delayed-identity':
                broker = FakeBroker()
                model = DelayedIdentity(journal, broker)
                model.submit()
                broker.trade.org_seqnum, broker.trade.order_id = 'fixture-seq', 'fixture-order'
                report = dict(account='fixture-account', generation=1, symbol='SYNTH-US', side='Buy',
                              org_seqnum='fixture-seq', order_id='fixture-order',
                              execution_id='fixture-execution', shares=4, price='10.25')
                model.observe(report)
                model.observe(report)
                return dict(create_calls=len(broker.calls), booked_shares=journal.shares(model.key),
                            source='synthetic-normalized-events')
            if case == 'cancel-late-fill':
                model = CancelLateFill()
                model.fill('fixture-first', 1000)
                model.trigger()
                model.cancel_returned()
                checks = dict(available_shares=2000, reserved_shares=0, authorized=True, fresh_quote=True)
                before = model.try_exit(**checks)
                model.fill('fixture-late', 500)
                model.entry_terminal(1500)
                after = model.try_exit(**checks)
                model.try_exit(**checks)
                return dict(exit_before_terminal=before, exit_shares=after,
                            cancel_calls=model.cancel_calls, exit_calls=len(model.exit_calls),
                            source='synthetic-normalized-events')
            model = ObserveBeforeEligibility(journal)
            model.receive('fixture-execution', 1000, '100')
            model.receive('fixture-execution', 1000, '100')
            plan = model.plan_exit(rules_valid=False, authorized=True, fresh_quote=True, available_shares=1000)
            return dict(**model.view(), exit_plan=plan, source='synthetic-normalized-events')
        finally:
            journal.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, choices=['delayed-identity','cancel-late-fill','reference-missing'])
    print(json.dumps(demonstrate(parser.parse_args().case), ensure_ascii=False, indent=2))
