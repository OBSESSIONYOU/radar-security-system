"""Regenerate fictional UI samples from mathematical functions; no capture input."""
from datetime import datetime, timedelta, timezone
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 684001
NOTICE = '合成演示：未使用真实采集数据，分数仅为界面示例，不代表实测性能。'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    rng = np.random.default_rng(SEED)
    paths = []
    events = []
    splits = [('known_train', 'worker_01', 's01'), ('known_train', 'worker_02', 's01'),
              ('known_test', 'worker_01', 's02'), ('unknown_test', 'visitor_x', 's01')]
    x = np.linspace(0, 4 * np.pi, 192)[None, :]
    y = np.linspace(-1, 1, 128)[:, None]
    for group, (split, subject, session) in enumerate(splits):
        for index in range(7):
            sample = f'{subject}_{session}_{index:04d}'
            path = ROOT / 'data/generated/spectrograms' / split / subject / (sample + '.png')
            path.parent.mkdir(parents=True, exist_ok=True)
            center = 0.35 * np.sin(x * (1 + group * 0.15) + index * 0.27)
            intensity = np.exp(-((y - center) / 0.08) ** 2)
            intensity += 0.5 * np.exp(-((y + center * 0.55) / 0.13) ** 2)
            intensity += rng.uniform(0, 0.08, size=(128, 192))
            plt.imsave(path, intensity, cmap='magma', vmin=0, vmax=1.5,
                       metadata={'Title': 'Synthetic mathematical demo', 'Description': NOTICE,
                                 'Software': 'generate_synthetic_demo.py seed 684001'})
            paths.append(path)
            known = split != 'unknown_test'
            score = round(0.24 + index * 0.035 if known else 0.79 + index * 0.02, 3)
            events.append({'id': f'synthetic-{len(events)+1:03d}',
                           'time': (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=len(events)*3)).isoformat(),
                           'zone': '合成演示区域 ' + ('A' if known else 'B'),
                           'sampleId': sample, 'spectrogramUrl': path.relative_to(ROOT).as_posix(),
                           'identityLabel': subject, 'isKnown': known, 'confidence': round(1-score/2, 3),
                           'openSetScore': score, 'threshold': 0.68, 'decision': 'allow' if known else 'reject',
                           'latencyMs': 0, 'condition': 'normal' if known else 'unknown_entry',
                           'message': NOTICE, 'synthetic': True})
    summary = {'total_samples': 28, 'samples_by_split': {'known_train': 14, 'known_test': 7, 'unknown_test': 7},
               'subjects_by_split': {'known_train': ['worker_01', 'worker_02'], 'known_test': ['worker_01'], 'unknown_test': ['visitor_x']},
               'known_train_subjects': ['worker_01', 'worker_02'], 'known_test_subjects': ['worker_01'], 'unknown_test_subjects': ['visitor_x']}
    baseline = {'method': 'synthetic_ui_fixture', 'notes': NOTICE, 'warnings': [NOTICE], 'sample_summary': summary,
                'closed_set': {'accuracy': None, 'macro_precision': None, 'macro_recall': None, 'macro_f1': None},
                'open_set': {'unknown_test_samples': 7, 'unknown_rejection_rate': None, 'false_acceptance_rate': None, 'auroc': None, 'fpr95': None}}
    preflight = {'model': 'not-trained', 'torch_available': False, 'torch_status': NOTICE,
                 'ready_for_training': False, 'blocking_issues': [NOTICE], 'warnings': [NOTICE], 'sample_summary': summary}
    status = {'qc': {'totalCaptures': 0, 'passedCaptures': 0, 'failedCaptures': 0, 'totalFrames': 0, 'totalDurationMs': 0, 'failedMessages': []},
              'baseline': baseline, 'resnetPreflight': preflight,
              'captureProfile': {'capture_mode': 'synthetic_demo', 'ready_for_live_capture': False, 'live_udp_implemented': False,
                                 'issues': [{'severity': 'warning', 'message': NOTICE}], 'issue_counts': {'error': 0, 'warning': 1}, 'profile': {'network': {}}},
              'readiness': {'ready_for_real_experiment': False, 'blockers': [NOTICE]},
              'provenance': {'synthetic': True, 'seed': SEED, 'real_capture_inputs': 0}}
    for relative, value in [('data/dashboard_events.json', events), ('data/pipeline_status.json', status),
                            ('data/metrics/baseline_metrics.json', baseline), ('data/metrics/resnet_preflight.json', preflight)]:
        path = ROOT / relative
        write_json(path, value)
        paths.append(path)
    for relative, header, rows in [
        ('data/metrics/baseline_predictions.csv', ['sample_id', 'synthetic', 'illustrative_decision', 'illustrative_score'],
         [[e['sampleId'], 'true', e['decision'], e['openSetScore']] for e in events]),
        ('data/qc/adc_qc_report.csv', ['source', 'synthetic', 'real_capture_count', 'notice'],
         [['mathematical_formula', 'true', 0, NOTICE]])]:
        path = ROOT / relative
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(header)
            writer.writerows(rows)
        paths.append(path)
    manifest = {'format': 'synthetic-radar-demo.v1', 'synthetic': True, 'seed': SEED,
                'notice': NOTICE, 'real_capture_inputs': [], 'generator': 'scripts/generate_synthetic_demo.py',
                'files_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    manifest_path = ROOT / 'data/synthetic-provenance.json'
    write_json(manifest_path, manifest)
    paths.append(manifest_path)
    policy_path = ROOT / 'scripts/privacy-policy.json'
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        approved = policy['approved_data'].setdefault(name, [])
        if checksum not in approved:
            approved.append(checksum)
    write_json(policy_path, policy)
    print('Generated 28 synthetic patterns; no real captures or measured evaluation metrics.')


if __name__ == '__main__':
    main()
