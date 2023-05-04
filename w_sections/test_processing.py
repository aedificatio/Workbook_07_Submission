from w_sections.processing import read_profiles, sections_greater_than, sections_less_than

# test_data
profiles = read_profiles('test_IPE_profiles.csv')
# profiles = read_profiles('IPE_profiles.csv')

def test_read_profiles():
    assert profiles.loc[ 1, 'Iy'] == 2414700000.0
    assert profiles.loc[ 1, 'Wel.y'] == 6271000.0
    assert profiles.loc[ 1, 'A'] == 25080.0
    assert profiles.loc[ 1, 'iy'] == 309.0


def test_sections_greater_than():
    assert len(sections_greater_than(profiles, A=25000)) == 2
    assert len(sections_greater_than(profiles, A=25000, tw=16)) == 1

def test_sections_less_than():
    assert sections_less_than(profiles, A=19000).shape[0] == 2
    assert sections_less_than(profiles, A=19000, It=1630000).shape[0] == 1

