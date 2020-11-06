from emv.protocol.data_elements import ELEMENT_TABLE


def test_data_elements():
    # Test uniqueness of the main element table
    seen_tags = set()
    seen_shortnames = set()
    for tag, name, parse, shortname in ELEMENT_TABLE:
        assert tag not in seen_tags
        if shortname is not None:
            assert shortname not in seen_shortnames
            seen_shortnames.add(shortname)
        seen_tags.add(tag)
