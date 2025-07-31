# API Reference

Complete API documentation organized by common tasks and workflows. If you're new to doteval, start with the [tutorials](../tutorials/01-your-first-evaluation.md) before diving into the API details.

## Quick Navigation

- **[Common Patterns](#common-patterns)** - Quick reference for typical usage
- **[Creating Evaluations](#creating-evaluations)** - `@foreach`, `Result`, basic patterns
- **[Built-in Evaluators](#built-in-evaluators)** - `exact_match`, `contains`, scoring functions
- **[Custom Evaluators](#custom-evaluators)** - `@evaluator`, metrics, advanced patterns
- **[Session Management](#session-management)** - Experiments, progress tracking, resumption
- **[Command Line Interface](#command-line-interface)** - `doteval` commands and options
- **[Data Models](#data-models)** - Core types and classes
- **[Advanced Usage](#advanced-usage)** - Storage backends, async patterns, pytest integration

---

## Common Patterns

Quick reference for the most frequently used doteval patterns.

### Basic Evaluation

```python
from doteval import foreach
from doteval.evaluators import exact_match

@foreach("question,answer", dataset)
def eval_basic(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

### Custom Evaluator with Multiple Metrics

```python
from doteval import foreach, Result
from doteval.evaluators import evaluator
from doteval.metrics import accuracy, mean

@evaluator(metrics=[accuracy(), mean()])
def custom_score(response: str, expected: str) -> float:
    # Your scoring logic here
    return similarity_score(response, expected)

@foreach("prompt,expected", dataset)
def eval_custom(prompt, expected, model):
    response = model.generate(prompt)
    return custom_score(response, expected)
```

### Async Evaluation

```python
@foreach("prompt,expected", dataset)
async def eval_async(prompt, expected, async_model):
    response = await async_model.generate_async(prompt)
    return exact_match(response, expected)
```

### Multiple Scores per Result

```python
@foreach("prompt,expected", dataset)
def eval_multi_score(prompt, expected, model):
    response = model.generate(prompt)

    return Result(
        exact_match(response, expected),  # Primary score
        prompt=prompt,
        response=response,
        scores={
            "exact_match": exact_match(response, expected),
            "length": len(response),
            "contains_keyword": "important" in response.lower()
        }
    )
```

### Common CLI Workflows

```bash
# Run evaluation with experiment tracking
pytest eval_script.py --experiment my_eval

# Resume interrupted evaluation
pytest eval_script.py --experiment my_eval

# View results
doteval show my_eval

# List all experiments
doteval list

# Clean up old experiments
doteval delete old_experiment
```

---

## Creating Evaluations

Core functions for defining and running evaluations. Start here if you're building your first evaluation.

### @foreach Decorator

The main decorator that transforms functions into evaluations. This is the primary entry point for most users.

**Usage**: `@foreach("param1,param2", dataset)`

::: doteval.foreach

### Result Class

Return type for evaluation functions. Use this when you need to return multiple scores or metadata alongside your primary evaluation result.

**Usage**: `return Result(primary_score, prompt=prompt, response=response, scores={...})`

::: doteval.Result

### Core Evaluation Functions

Essential functions from the core module for advanced usage and programmatic access.

::: doteval.core

---

## Built-in Evaluators

Ready-to-use evaluators for common evaluation tasks. These functions can be used directly in your evaluations or as building blocks for custom evaluators.

### exact_match Evaluator

The most commonly used evaluator for exact string comparisons.

::: doteval.evaluators.exact_match

### All Built-in Evaluators

All available evaluators in the doteval.evaluators module.

::: doteval.evaluators
    options:
      filters:
        - "!evaluator"

---

## Custom Evaluators

Tools for creating your own evaluators and metrics. Use these when built-in evaluators don't meet your specific needs.

### @evaluator Decorator

Create custom evaluators with automatic metric computation and result aggregation.

**Usage**: `@evaluator(metrics=[accuracy(), mean()])`

**See also**: [How to Evaluate Structured Generation](../how-to/evaluate-structured-generation.md)

::: doteval.evaluators.evaluator

### Metrics

Built-in metrics for aggregating evaluation results across your dataset.

**Common metrics**: `accuracy()`, `mean()`, `std()`, `count()`

::: doteval.metrics

---

## Session Management

Functions for managing evaluation experiments and progress. Use these for programmatic access to experiment data and advanced session control.

**For basic usage**, the CLI commands (`doteval show`, `doteval list`) are usually sufficient.

### Experiment Functions

Programmatic access to session data and experiment management.

**See also**: [How to Resume Failed Evaluations](../how-to/resume-failed-evaluations.md)

::: doteval.sessions

### Session Classes

Data models representing evaluation sessions and their status.

::: doteval.models

---

## Command Line Interface

The `doteval` command and its subcommands for managing experiments from the command line.

**Quick reference**:
- `doteval list` - Show all experiments
- `doteval show <name>` - View experiment results
- `doteval delete <name>` - Remove experiment

**See also**: [Reference: CLI](../reference/cli.md)

::: doteval.cli

---

## Data Models

Core data types and classes used throughout doteval. These are primarily used internally but may be useful for advanced integrations.

::: doteval.models

---

## Advanced Usage

Advanced features for specialized use cases and integrations.

### pytest Integration

Functions and classes for pytest plugin functionality. Most users won't need to interact with these directly.

**See also**: [Reference: pytest Integration](../reference/pytest.md)

::: doteval.plugin

### Storage Backends

Classes for different storage systems. Use these to configure custom storage locations or implement new backends.

**See also**: [Reference: Storage Backends](../reference/storage.md)

*Note: Storage configuration is typically done via CLI arguments (`--storage`) rather than direct API usage.*

### Async Support

Functions and patterns for asynchronous evaluation to improve performance with concurrent API calls.

**See also**: [Tutorial 5: Scale with Async Evaluation](../tutorials/05-scale-with-async-evaluation.md)

*Note: Async functionality is built into the core `@foreach` decorator and doesn't require separate imports.*

---

## See Also

- **[How-To Guides](../how-to/index.md)** - Problem-focused solutions using these APIs
- **[Tutorial Series](../tutorials/01-your-first-evaluation.md)** - Step-by-step guides with practical examples
- **[Reference Documentation](../reference/index.md)** - Conceptual documentation and usage patterns
