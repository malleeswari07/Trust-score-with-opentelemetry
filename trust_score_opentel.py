import json
import hashlib
import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


resource = Resource.create(
    {"service.name": "trust-score"}
)

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

exporter = OTLPSpanExporter(
    endpoint="localhost:4317",
    insecure=True
)

provider.add_span_processor(
    BatchSpanProcessor(exporter)
)

tracer = trace.get_tracer(__name__)


class TrustScoreCalculator:

    def __init__(self, scores, weights):
        self.scores = scores
        self.weights = weights

    def check_inputs(self):
        with tracer.start_as_current_span("Validate Inputs") as span:
            time.sleep(0.05)

            span.set_attribute("total.scores", len(self.scores))
            span.set_attribute("total.weights", len(self.weights))

            for name, value in self.scores.items():
                if value < 0 or value > 100:
                    raise ValueError(f"{name} score should be between 0 and 100.")

            for name, value in self.weights.items():
                if value < 0 or value > 1:
                    raise ValueError(f"{name} weight should be between 0 and 1.")

            if round(sum(self.weights.values()), 5) != 1:
                raise ValueError("Weights should add up to 1.")

            span.set_attribute("validation.status", "success")

    def calculate(self):

        self.check_inputs()

        with tracer.start_as_current_span("Calculate Score") as span:

            time.sleep(0.07)
            total = 0
            for name in self.scores:
                total += self.scores[name] * self.weights[name]

            total = round(total, 2)

            span.set_attribute("trust.score", total)
            span.set_attribute("risk.level", self.get_risk(total))

            return total

    def get_risk(self, score):

        if score >= 90:
            return "Very Low Risk"
        if score >= 75:
            return "Low Risk"
        if score >= 60:
            return "Medium Risk"
        if score >= 40:
            return "High Risk"
        return "Critical Risk"

    def get_flags(self):

        with tracer.start_as_current_span("Get Risk Flags") as span:

            flags = []

            checks = {
                "fairness": "Fairness Risk",
                "robustness": "Robustness Risk",
                "privacy": "Privacy Risk",
                "reliability": "Reliability Risk",
                "security": "Security Risk",
                "accountability": "Accountability Risk"
            }

            time.sleep(0.1)

            for key, message in checks.items():
                if self.scores[key] < 60:
                    flags.append(message)

            span.set_attribute("flags.count", len(flags))

            return flags
        
    def build_evidence(self):

        with tracer.start_as_current_span("Create Evidence") as span:

            score = self.calculate()

            data = {
                "scores": self.scores,
                "weights": self.weights,
                "trust_score": score,
                "risk_level": self.get_risk(score),
                "risk_flags": self.get_flags()
            }

            span.set_attribute("evidence.created", True)

            return data

    def create_hash(self, data):

        with tracer.start_as_current_span("Generate Hash") as span:

            text = json.dumps(data, sort_keys=True)

            digest = hashlib.sha256(text.encode()).hexdigest()

            span.set_attribute("hash.length", len(digest))

            return digest

    def save(self, file_name="evidence.json"):

        with tracer.start_as_current_span("Trust Score ") as root_span:

            data = self.build_evidence()
            data["sha256"] = self.create_hash(data)

            with tracer.start_as_current_span("Save Evidence") as span:

                span.set_attribute("file.name", file_name)

                with open(file_name, "w") as file:
                    json.dump(data, file, indent=4)

                span.set_attribute("save.status", "success")

            root_span.set_attribute("pipeline.status", "completed")

            return data


if __name__ == "__main__":

    scores = {
        "fairness": 90,
        "robustness": 85,
        "privacy": 95,
        "reliability": 87,
        "security": 88,
        "accountability": 82
    }

    weights = {
        "fairness": 0.20,
        "robustness": 0.20,
        "privacy": 0.15,
        "reliability": 0.15,
        "security": 0.20,
        "accountability": 0.10
    }

    calc = TrustScoreCalculator(scores, weights)

    result = calc.save()

    print("\nTrust Score Calculator\n")
    print(f"Trust Score : {result['trust_score']}")
    print(f"Risk Level  : {result['risk_level']}")

    if result["risk_flags"]:
        print("Risk Flags  :", ", ".join(result["risk_flags"]))
    else:
        print("Risk Flags  : None")

    print("\nEvidence saved to evidence.json")

    provider.force_flush()
    provider.shutdown()
