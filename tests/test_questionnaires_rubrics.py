def test_questionnaires():
    from src.questionnaires.registry import get_questionnaire, list_questionnaires
    qs = list_questionnaires()
    assert len(qs) >= 40
    assert get_questionnaire(qs[0])["items"]

def test_rubrics():
    from src.rubrics.registry import list_rubrics, score_all
    assert len(list_rubrics()) >= 20
    s = score_all("system chokepoint kill criteria source https://a.com risk")
    assert s["count"] >= 20
    assert s["avg_percent"] is not None
