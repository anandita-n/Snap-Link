import os
import sys
import json
import argparse
from pydantic import BaseModel, Field
from typing import List, Literal

# Try importing google-genai and pydantic. If they are not installed, 
# we'll catch it and run the fallback report.
try:
    from google import genai
    from google.genai import types
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

class TriageReport(BaseModel):
    summary: str
    likely_root_cause: str
    severity: Literal["low", "medium", "high"]
    suggested_fix: str
    affected_files: List[str]

def read_and_truncate_log(file_path: str, max_lines: int = 200) -> str:
    if not os.path.exists(file_path):
        return f"[Log file not found: {file_path}]"
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        return f"[Error reading log file {file_path}: {str(e)}]"
    
    truncated_lines = lines[-max_lines:] if len(lines) > max_lines else lines
    content = "".join(truncated_lines)
    
    # Print metrics for cost visibility
    print(f"[AI Triage] File: {file_path}")
    print(f"[AI Triage] Original lines: {len(lines)}, Sent lines: {len(truncated_lines)}")
    print(f"[AI Triage] Sent characters: {len(content)} (~{len(content) // 4} tokens)")
    return content

def write_and_print_report(report: TriageReport):
    report_dict = report.model_dump()
    
    # Write to triage_report.json
    output_path = "triage_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)
    
    # Print to console
    print("\n" + "=" * 50)
    print("         GEMINI BUILD TRIAGE REPORT")
    print("=" * 50)
    print(f"Summary:           {report.summary}")
    print(f"Likely Root Cause: {report.likely_root_cause}")
    print(f"Severity:          {report.severity.upper()}")
    print(f"Suggested Fix:     {report.suggested_fix}")
    print(f"Affected Files:    {', '.join(report.affected_files) if report.affected_files else 'None detected'}")
    print("=" * 50 + "\n")

def get_fallback_report(error_msg: str) -> TriageReport:
    return TriageReport(
        summary="AI triage failed to analyze the build failure",
        likely_root_cause=f"The AI model failed to produce a valid report. Error details: {error_msg}",
        severity="high",
        suggested_fix="Please inspect the step logs and verify credentials and API access.",
        affected_files=[]
    )

def main():
    parser = argparse.ArgumentParser(description="Analyze build failure logs with Google Gemini.")
    parser.add_argument(
        "--failure",
        action="append",
        help="Failure details in the format <side>:<stage>:<log_file_path> (e.g. backend:test:backend_test.log)",
        required=True
    )
    
    args = parser.parse_args()
    
    # Build prompt content from logs
    prompt_sections = []
    for failure in args.failure:
        parts = failure.split(":", 2)
        if len(parts) != 3:
            print(f"[AI Triage Warning] Invalid failure parameter: {failure}")
            continue
        
        side, stage, log_path = parts
        log_content = read_and_truncate_log(log_path)
        
        section = (
            f"=== Component: {side} ===\n"
            f"=== Stage: {stage} ===\n"
            f"=== Failure Log ===\n"
            f"{log_content}\n"
        )
        prompt_sections.append(section)
        
    if not prompt_sections:
        fallback = get_fallback_report("No valid failure logs provided as input.")
        write_and_print_report(fallback)
        sys.exit(0)
        
    combined_logs = "\n".join(prompt_sections)
    
    # Tightly-scoped prompt
    prompt = (
        "You are a developer operations agent analyzing CI/CD build failures.\n"
        "Analyze the following failure logs from the build step and diagnose the root cause.\n"
        "Identify the file names and lines causing issues if present, and give a specific suggested fix.\n\n"
        f"{combined_logs}"
    )
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[AI Triage Error] GEMINI_API_KEY environment variable is missing.")
        fallback = get_fallback_report("GEMINI_API_KEY environment variable is missing.")
        write_and_print_report(fallback)
        sys.exit(0)
        
    if not SDK_AVAILABLE:
        print("[AI Triage Error] google-genai or pydantic packages are not available.")
        fallback = get_fallback_report("Required libraries (google-genai, pydantic) are not installed.")
        write_and_print_report(fallback)
        sys.exit(0)
        
    try:
        # Initialize client with 30s timeout and explicit API key
        client = genai.Client(api_key=api_key, http_options={"timeout": 30.0})
        
        # Call Gemini with structured output
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TriageReport,
            ),
        )
        
        # Parse result
        response_text = response.text
        if not response_text:
            raise ValueError("Empty response from Gemini API.")
            
        data = json.loads(response_text)
        
        # Validate using Pydantic model
        report = TriageReport(**data)
        write_and_print_report(report)
        
    except Exception as e:
        print(f"[AI Triage Error] Failed to generate triage report: {str(e)}")
        fallback = get_fallback_report(str(e))
        write_and_print_report(fallback)

if __name__ == "__main__":
    main()
