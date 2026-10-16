# Lab 5: Reflection

The supplied three-page handout asks for reflection but does not print four
specific questions. These answers address four reflection themes from its
objective and learning outcomes.

### 1. What is static code analysis, and why is it useful?

Static analysis checks source code without running it. In this lab it exposed
problems early, including the shared mutable default, swallowed cancellation
errors, and shell execution, before those defects could affect a real schedule.

### 2. Which finding was most important, and why?

The shell call was the most important security finding. Building a shell
command from a file path can permit command injection, and the Unix `cat`
command also failed on this Windows machine. Replacing it with Python file
operations removed both problems.

### 3. How did Pylint, Bandit, and Flake8 complement one another?

Pylint highlighted design and correctness concerns such as global state,
mutable defaults, missing documentation, and unused variables. Bandit drew
attention to the shell command and the overly broad exception handler, while
Flake8 identified formatting and unused-code issues. Running all three gave me
a broader view than relying on one tool.

### 4. What did the tools not catch, and how did you verify the fixes?

The tools did not report every behavioral defect: a reversed time range could
produce a negative duration, and an overlapping booking was still accepted.
I added input checks and booking/inventory tests for those cases. After the
changes, I ran the test suite and reran all three analyzers to check both
behavior and the remaining static findings.
