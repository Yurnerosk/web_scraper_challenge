from RPA.Robocorp.WorkItems import WorkItems

class ConfigManager:

    wi = WorkItems()
    wi.get_input_work_item()
    SEARCH_PHRASE = wi.get_work_item_variable("search_phrase")
    SECTIONS = wi.get_work_item_variable("sections")
    MONTHS_NUMBER = wi.get_work_item_variable("months_number")
    
    # SEARCH_PHRASE = "climate"
    # SECTIONS = ["world & nation"]
    # MONTHS_NUMBER = "1"

    # &s=1 means order by newest
    BASE_URL = "https://www.latimes.com/"

    # section codes doesn't have a determined sequence.
    SECTION_CODES = {
        "any": "",
        "world & nation": "//input[@value='00000168-8694-d5d8-a76d-efddaf000000']",
        "california": "//input[@value='00000163-01e2-d9e5-adef-33e2984a0000']",
        "politics": "00000163-01e2-d9e5-adef-33e2d08d0000",
        "opinion": "//input[@value='00000163-01e3-d9e5-adef-33e359e70000']",
        "entertainment & arts": "//input[@value='00000163-01e3-d9e5-adef-33e330f30000']",
        "archives": "00000174-dc37-dc3d-aff4-dfff225c0001",
        "travel & experiences": "00000168-86b6-d2cb-a969-debe73e10000",
        "science & medicine": "00000168-869a-d5d8-a76d-efdbcc330000",
        "climate & environment": "0000016a-b70e-dd5c-abfe-bf3f7b290000",
        "books": "00000168-8659-d5d8-a76d-efd9b0ca0000",
        "food": "//input[@value='00000168-8683-d2cb-a969-de8b247e0000']",

    }

    
    