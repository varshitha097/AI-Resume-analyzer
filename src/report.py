
import csv
import io
from typing import Dict, List


def results_to_csv(results: List[Dict]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "File Name", "Score", "Recommendation", "Domain", "Experience Years",
        "Matched Skills", "Missing Skills", "Similarity Engine"
    ])
    for r in results:
        writer.writerow([
            r.get("rank", ""),
            r.get("file_name", ""),
            r.get("score", ""),
            r.get("recommendation", ""),
            r.get("resume_domain", {}).get("best_domain", ""),
            r.get("resume_info", {}).get("experience", {}).get("years", 0),
            ", ".join(r.get("scoring", {}).get("matched_skills", [])),
            ", ".join(r.get("scoring", {}).get("missing_skills", [])),
            r.get("engine", ""),
        ])
    return output.getvalue()
