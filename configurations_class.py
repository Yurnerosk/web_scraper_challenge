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
        "politics": "//input[@value='00000163-01e2-d9e5-adef-33e2d08d0000']",
        "business": "//input[@value='00000168-865c-d5d8-a76d-efddd6550000']",
        "opinion": "//input[@value='00000163-01e3-d9e5-adef-33e359e70000']",
        "entertainment & arts": "//input[@value='00000163-01e3-d9e5-adef-33e330f30000']",
        "archives": "//input[@value='00000174-dc37-dc3d-aff4-dfff225c0001']",
        "travel & experiences": "//input[@value='00000168-86b6-d2cb-a969-debe73e10000']",
        "science & medicine": "//input[@value='00000168-869a-d5d8-a76d-efdbcc330000']",
        "climate & environment": "//input[@value='0000016a-b70e-dd5c-abfe-bf3f7b290000']",
        "books": "//input[@value='00000168-8659-d5d8-a76d-efd9b0ca0000']",
        "food": "//input[@value='00000168-8683-d2cb-a969-de8b247e0000']",
        "movies": "//input[@value='00000168-8677-d5d8-a76d-efff01170000']",
        "sports": "//input[@value='00000163-01e3-d9e5-adef-33e30d170000']",
        "television": "//input[@value='00000168-8679-d2cb-a969-de7bbad50000']",
        "autos": "//input[@value='00000168-865d-d2cb-a969-de5f07b50000']",
        "music": "//input[@value='00000168-8679-d5d8-a76d-eff941690000']",
        "greenspace": "//input[@value='00000181-7484-d0b1-afcb-7fa7f5020008']",
        "letters to the editor": "//input[@value='0000017c-04e0-d7a2-a1fd-bdfe2ed80000']"



    }

    
    