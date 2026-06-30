# Trust Score Calculator with OpenTelemetry

## Overview

This  is a simple Trust Score Calculator that evaluates how trustworthy a system is based on different AI governance factors like fairness, privacy, security, and reliability.

To make the system observable, it is instrumented with OpenTelemetry. All execution steps are traced and exported to Jaeger so we can visually understand how the calculation flows internally.

---

## What This file Does

The calculator takes a set of scores and weights, and then:

- Validates the inputs
- Calculates a final trust score
- Identifies risk areas
- Generates a secure hash of the result
- Saves everything into a JSON file

At the same time, every major step is tracked using distributed tracing.

---

## Trust Attributes Used

The trust attributes are:

- Fairness
- Robustness
- Privacy
- Reliability
- Security
- Accountability

Each of these is assigned a weight and contributes to the final score.

---

## How Tracing is Designed

The application creates 5 spans ,those spans are :

### 1. Validate Inputs
Checks whether all scores and weights are within valid limits and ensures weights add up correctly.

### 2. Calculate Score
Computes the final weighted trust score and determines the risk level.

### 3. Get Risk Flags
Identifies weak areas where scores are below the safe threshold.

### 4. Generate Hash
Creates a SHA-256 hash of the final evidence to ensure integrity.

### 5. Save Evidence
Stores the final result in a JSON file.

## Trace Flow
The execution flow looks like this in Jaeger:

Save Evidence
 └── Create Evidence
      ├── Calculate Score
      │    └── Validate Inputs
      ├── Get Risk Flags
      └── Generate Hash

## Tech Stack

- Python
- OpenTelemetry SDK
- Jaeger (for tracing visualization)
- Docker (to run Jaeger locally)


## How to Run

### 1. Start Jaeger (Docker)

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one