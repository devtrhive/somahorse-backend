def test_skill_match_simple():
    from app.routers.matching import calculate_skill_match
    s = calculate_skill_match(['py','sql'], ['py','js'])
    assert s == 50.0
