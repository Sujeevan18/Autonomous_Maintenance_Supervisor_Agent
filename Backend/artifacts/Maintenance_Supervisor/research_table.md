# Autonomous Maintenance Supervisor - Model Benchmark Comparison

| Model Architecture | Accuracy | Macro F1 | False Critical Rate | Missed Critical Rate | Economic Cost Penalty |
|---|---|---|---|---|---|
| Majority Vote Baseline | 0.5850 | 0.1476 | 0.0000 | 1.0000 | $55,536.00 |
| Rule-Based Baseline | 0.0567 | 0.0215 | 1.0000 | 0.0000 | $40,486.00 |
| RUL-Only Baseline | 0.0567 | 0.0215 | 1.0000 | 0.0000 | $40,486.00 |
| Risk-Only Baseline | 0.6937 | 0.3941 | 0.1231 | 0.0000 | $4,070.00 |
| Anomaly-Only Baseline | 0.6838 | 0.3610 | 0.2078 | 0.0000 | $5,228.00 |
| Champion Supervisor Agent | 0.0567 | 0.0215 | 1.0000 | 0.0000 | $40,486.00 |
