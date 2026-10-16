# Lab 5: Static Code Analysis

This submission analyzes and repairs the conference-room scheduler with
Pylint, Bandit, and Flake8.

**Submission repository:** <https://github.com/mmbasu-8866/SE-Labs-PES1UG24CS561>

## Contents

- `Lab_5_Static_Code_Analysis_Lab_Report.docx` and `.pdf`: completed lab report
  with the issues table, observations, screenshots, and conclusion.
- `issues.md`: severity-ordered static-analysis and behavioral findings.
- `*_report_before.txt`: reports for the original starter program.
- `*_report.txt`: final reports after the fixes.
- `scheduler_system.py`: corrected scheduler.
- `test_scheduler_system.py`: behavioral regression tests.
- `reflection.md`: reflection responses.

## Run

```powershell
python scheduler_system.py
python -m unittest -v test_scheduler_system
pylint scheduler_system.py
bandit -r scheduler_system.py
flake8 scheduler_system.py test_scheduler_system.py
```

The verified results are a Pylint score of 10.00/10, no Bandit findings, no
Flake8 findings, and seven passing tests.
