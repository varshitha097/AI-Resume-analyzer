
from src.pipeline import ResumeAnalyzer


def test_analyze_sample_text():
    analyzer = ResumeAnalyzer()
    resume = open("samples/sample_resume_text.txt", encoding="utf-8").read()
    jd = open("samples/sample_jd.txt", encoding="utf-8").read()
    result = analyzer.analyze_text(resume, jd)
    assert result["score"] >= 40
    assert "Python" in result["resume_info"]["skills"]
    assert "Python" in result["jd_info"]["required_skills"]
