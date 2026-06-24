# Milestone 27 Findings

## Research Question

Can departure simulation be fully grounded using organizational intelligence rather than handcrafted ownership and health assumptions?

---

## Initial Observation

After M26, SimulationAdapter still contained two major fixtures:

```text
OwnershipEstimate
HealthReport
```

Readiness was grounded, but simulation outcomes still depended on assumptions.

This created a mixed architecture where only part of the simulation pipeline reflected repository reality.

---

## Key Finding #1

Ownership is a critical simulation signal.

Knowledge loss is calculated from:

```text
ownership share
successor readiness
```

If ownership is fixed, simulation cannot distinguish between:

```text
primary owner
minor contributor
```

which produces unrealistic results.

---

## Key Finding #2

Health is a derived organizational metric.

Simulation should not consume arbitrary health values.

Health already exists as the result of:

```text
Coverage
Concentration
Bus Factor
```

Using HealthService ensures simulation reflects the same organizational state used elsewhere in the system.

---

## Key Finding #3

Different departure scenarios must produce different outcomes.

Prior to grounding:

```text
Alice leaves
Bob leaves
Charlie leaves
```

could produce identical results.

After grounding:

```text
Alice leaves
    ↓
higher ownership
    ↓
larger knowledge loss

Bob leaves
    ↓
lower ownership
    ↓
smaller knowledge loss
```

The simulation became sensitive to actual organizational structure.

---

## Key Finding #4

Readiness alone is insufficient.

Even perfect readiness cannot compensate for incorrect ownership assumptions.

Accurate simulation requires:

```text
Ownership
    ↓
Readiness
    ↓
Simulation
```

rather than readiness alone.

---

## Validation

Repository state:

```text
auth.py

alice    95
bob       3
charlie   2
```

Results:

### Alice

```text
Knowledge Loss: 0.28
Severity: HIGH
```

### Bob

```text
Knowledge Loss: 0.24
Severity: MODERATE
```

This verified that ownership grounding directly affects simulation outcomes.

---

## Architectural Impact

M27 completes the simulation pipeline:

```text
Expertise
        ↓
Ownership

Expertise
        ↓
Coverage
Concentration
Bus Factor
        ↓
Health

Successor
        ↓
Readiness

Ownership
Health
Readiness
        ↓
Simulation
```

The simulation engine now operates entirely on intelligence-derived inputs.

---

## Lessons Learned

1. Simulation quality depends heavily on ownership accuracy.
2. Health should be derived, not manually supplied.
3. Grounding exposes hidden assumptions.
4. Different organizational roles must produce different departure impacts.
5. Ownership and readiness are complementary signals.

---

## Milestone Summary

M27 removed the final major fixture-based simulation inputs and connected simulation directly to the intelligence graph.

The system can now model departure impact using real ownership, health, and successor readiness signals.

This milestone completes the grounding phase of the agent architecture.
