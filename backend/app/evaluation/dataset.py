"""Curated Golden Benchmark Dataset for KnowFlow AI RAG Evaluation.
Contains verified SOP test cases and adversarial out-of-scope queries.
"""


from pydantic import BaseModel


class BenchmarkCase(BaseModel):
    id: str
    question: str
    category: str  # "COLD_CHAIN", "DEVIATION", "HR_POLICY", "IT_SECURITY", "ADVERSARIAL_OUT_OF_SCOPE"
    expected_doc_title: str | None = None
    expected_page: int | None = None
    expected_keywords: list[str] = []
    ground_truth_answer: str | None = None
    is_out_of_scope: bool = False


GOLDEN_BENCHMARK_CASES: list[BenchmarkCase] = [
    # --- Category: COLD_CHAIN (CLIN-SOP-009) ---
    BenchmarkCase(
        id="case-cold-001",
        question="What temperature range is required for cold chain storage?",
        category="COLD_CHAIN",
        expected_doc_title="CLIN-SOP-009: Refrigerated Storage & Cold Chain",
        expected_page=2,
        expected_keywords=["+2.0°C", "+8.0°C", "refrigerated"],
        ground_truth_answer="Refrigerated storage must be strictly maintained between +2.0°C and +8.0°C (+35.6°F to +46.4°F).",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-cold-002",
        question="How should temperature-sensitive materials be stored?",
        category="COLD_CHAIN",
        expected_doc_title="CLIN-SOP-009: Refrigerated Storage & Cold Chain",
        expected_page=2,
        expected_keywords=["temperature", "storage", "+2.0°C", "+8.0°C"],
        ground_truth_answer="Temperature-sensitive materials must be stored in qualified refrigerated units between +2.0°C and +8.0°C with continuous calibrated monitoring.",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-cold-003",
        question="What temperature is required for deep frozen and ultra-low storage?",
        category="COLD_CHAIN",
        expected_doc_title="CLIN-SOP-009: Refrigerated Storage & Cold Chain",
        expected_page=2,
        expected_keywords=["-20.0°C", "-80.0°C", "-65.0°C", "ultra-low"],
        ground_truth_answer="Deep frozen storage must be maintained at -20.0°C ± 5°C, and ultra-low storage between -80.0°C and -65.0°C.",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-cold-004",
        question="What is the immediate action required during a temperature excursion in cold chain?",
        category="COLD_CHAIN",
        expected_doc_title="CLIN-SOP-009: Refrigerated Storage & Cold Chain",
        expected_page=3,
        expected_keywords=["excursion", "quarantine", "quality assurance"],
        ground_truth_answer="Immediately quarantine affected product under controlled conditions (+2°C to +8°C) and notify Quality Assurance within 2 hours.",
        is_out_of_scope=False,
    ),

    # --- Category: DEVIATION (SOP-QA-042) ---
    BenchmarkCase(
        id="case-dev-001",
        question="What is the time limit for reporting a major deviation?",
        category="DEVIATION",
        expected_doc_title="SOP-QA-042: Deviation Management & RCA",
        expected_page=1,
        expected_keywords=["major deviation", "24 hours", "reporting"],
        ground_truth_answer="A major deviation must be reported into the QMS within 24 hours of discovery.",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-dev-002",
        question="What is the required closure timeline for a critical deviation?",
        category="DEVIATION",
        expected_doc_title="SOP-QA-042: Deviation Management & RCA",
        expected_page=2,
        expected_keywords=["critical", "investigation", "calendar days"],
        ground_truth_answer="Critical deviations require root cause analysis and investigation closure within 15 calendar days.",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-dev-003",
        question="Who is authorized to approve a CAPA extension under deviation management?",
        category="DEVIATION",
        expected_doc_title="SOP-QA-042: Deviation Management & RCA",
        expected_page=3,
        expected_keywords=["CAPA", "extension", "Quality Assurance", "director"],
        ground_truth_answer="CAPA extensions must be approved by the Head of Quality Assurance or Quality Director prior to the original due date.",
        is_out_of_scope=False,
    ),

    # --- Category: IT_SECURITY (IT-SEC-015) ---
    BenchmarkCase(
        id="case-it-001",
        question="What are the minimum password complexity requirements?",
        category="IT_SECURITY",
        expected_doc_title="IT-SEC-015: Password & Access Control Policy",
        expected_page=1,
        expected_keywords=["password", "characters", "complexity"],
        ground_truth_answer="Passwords must be at least 14 characters with uppercase, lowercase, numeric, and special characters.",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-it-002",
        question="How many failed login attempts trigger an automatic account lockout?",
        category="IT_SECURITY",
        expected_doc_title="IT-SEC-015: Password & Access Control Policy",
        expected_page=1,
        expected_keywords=["lockout", "attempts", "failed"],
        ground_truth_answer="Accounts are locked out after 5 consecutive failed login attempts.",
        is_out_of_scope=False,
    ),

    # --- Category: HR_POLICY (HR-POL-108) ---
    BenchmarkCase(
        id="case-hr-001",
        question="What is the policy for annual paid time off (PTO) and leave accrual?",
        category="HR_POLICY",
        expected_doc_title="HR-POL-108: Leave and Attendance Policy",
        expected_page=1,
        expected_keywords=["paid time off", "PTO", "accrual", "20 days"],
        ground_truth_answer="Full-time employees accrue 20 days of paid time off per calendar year, accrued semi-monthly.",
        is_out_of_scope=False,
    ),
    BenchmarkCase(
        id="case-hr-002",
        question="What is the notice period required for voluntary employee resignation?",
        category="HR_POLICY",
        expected_doc_title="HR-POL-108: Leave and Attendance Policy",
        expected_page=3,
        expected_keywords=["resignation", "notice", "weeks"],
        ground_truth_answer="Standard employees must give 2 weeks written notice; managers and directors must give 4 weeks notice.",
        is_out_of_scope=False,
    ),

    # --- Category: ADVERSARIAL / OUT-OF-SCOPE (Must be refused under Grounded Answering Policy) ---
    BenchmarkCase(
        id="case-adv-001",
        question="Who won the 2022 FIFA World Cup?",
        category="ADVERSARIAL_OUT_OF_SCOPE",
        expected_doc_title=None,
        expected_page=None,
        expected_keywords=[],
        ground_truth_answer=None,
        is_out_of_scope=True,
    ),
    BenchmarkCase(
        id="case-adv-002",
        question="What is the capital city of Australia?",
        category="ADVERSARIAL_OUT_OF_SCOPE",
        expected_doc_title=None,
        expected_page=None,
        expected_keywords=[],
        ground_truth_answer=None,
        is_out_of_scope=True,
    ),
    BenchmarkCase(
        id="case-adv-003",
        question="How do I bake a chocolate cake at 350 degrees?",
        category="ADVERSARIAL_OUT_OF_SCOPE",
        expected_doc_title=None,
        expected_page=None,
        expected_keywords=[],
        ground_truth_answer=None,
        is_out_of_scope=True,
    ),
    BenchmarkCase(
        id="case-adv-004",
        question="Can you write a python script to scrape stock prices?",
        category="ADVERSARIAL_OUT_OF_SCOPE",
        expected_doc_title=None,
        expected_page=None,
        expected_keywords=[],
        ground_truth_answer=None,
        is_out_of_scope=True,
    ),
]
