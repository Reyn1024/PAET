# Method Design Notes

## Design Principle

PAET should be an intermediate representation between perception and planning:

```text
multimodal observation -> physical-affordance event tokens -> risk/wait/failure-aware decision support
```

## Minimal Version

The first version should support:

- token detection,
- confidence estimation,
- spatial anchoring,
- time-window assignment,
- evidence-channel tracing,
- downstream decision-effect annotation.

## Avoided Claims

Do not claim:

- better navigation performance before experiments are completed,
- generalization across buildings before cross-building tests exist,
- human-safety improvement without defined safety metrics,
- explainability improvement without user or faithfulness evaluation.

