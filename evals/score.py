"""Score structured development decisions; no language/heading keyword grading."""
from pathlib import Path
import argparse
import json

EXPECTED = {
    'delayed-identity': dict(retain_returned_trade=True, automatically_resubmit=False,
                             treat_empty_id_as_not_sent=False, mark_filled_now=False),
    'cancel-late-fill': dict(exit_before_cancel_terminal=False, exit_quantity_shares=1500,
                            repeat_cancel_on_timeout=False, discard_late_fill=False),
    'reference-missing': dict(booked_shares=1000, position_visible=True, continue_observation=True,
                             automatic_exit_allowed=False, erase_fill_when_reference_missing=False),
    'command-outcome': dict(first_outcome=('unknown','unknown_effect','indeterminate','結果未明','結果未確認'),
                            second_outcome=('not_executed','not_started','未執行','尚未執行'),
                            automatically_retry_first=False),
    'preserve-position-policy': dict(unit_count=2, merge_without_user_decision=False,
                                     replace_policy_because_reference_does_it=False),
    'guard-purpose': dict(reject_only_due_to_update_date=False, block_all_report_collection=False,
                          invent_an_effective_date_field=False, validate_actual_applicable_rules=True),
    'original-interface-demo': dict(reuse_maintained_ui_controls=True, isolated_fake_transport=True,
                                    verify_real_dom_interaction=True, allow_demo_to_modify_live_ledger=False),
    'workflow-recovery': dict(login_alone_completes_recovery=False, require_duplicate_user_permission=False,
                              restore_callbacks_subscriptions_and_reconcile=True, resume_A_after_requirements_met=True,
                              resume_user_stopped_B=False, reset_remaining_budget=False),
    'small-script-control': dict(require_full_state_inventory=False, require_workbench_ui=False,
                                 require_new_service_or_persistent_wal=False),
    'conflicting-execution': dict(silently_rewrite_original_cost=False, book_as_additional_fill=False,
                                  isolate_affected_symbol=True, continue_confirmed_unaffected_symbol=True),
}


def score(document):
    answers = document.get('answers')
    if not isinstance(answers, list):
        raise ValueError('answers must be a list')
    identifiers = [item.get('id') for item in answers]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != set(EXPECTED):
        raise ValueError('Need exactly one response for each frozen question')
    by_id = {item['id']: item for item in answers}
    rows = []
    for identifier, checks in EXPECTED.items():
        response = by_id[identifier]
        if not isinstance(response.get('answer'), dict) or not isinstance(response.get('reason'), str):
            raise ValueError(f'{identifier}: missing answer or reason')
        references = response.get('references')
        if not isinstance(references, list) or not all(isinstance(p, str) for p in references):
            raise ValueError(f'{identifier}: references must be a list of relative paths')
        decisions = response['answer']
        failures = []
        for field, expected in checks.items():
            observed = decisions.get(field)
            if isinstance(expected, tuple):
                ok = isinstance(observed, str) and observed.strip().lower().replace('-', '_') in expected
            else:
                ok = type(observed) is type(expected) and observed == expected
            if not ok:
                failures.append(dict(field=field, observed=observed, expected=expected))
        rows.append(dict(id=identifier, passed=len(checks)-len(failures), total=len(checks),
                         case_pass=not failures, failures=failures, references=references))
    return dict(cases_passed=sum(row['case_pass'] for row in rows), cases_total=len(rows),
                decisions_passed=sum(row['passed'] for row in rows),
                decisions_total=sum(row['total'] for row in rows), cases=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('response', type=Path)
    args = parser.parse_args()
    print(json.dumps(score(json.loads(args.response.read_text(encoding='utf-8'))), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
