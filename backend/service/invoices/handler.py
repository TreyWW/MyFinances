PAGES = ["single", "recurring"]

SUB_PAGES = ["single/create"]


def validate_page(page: str, sub_page: str) -> bool:
    if not page:
        return True

    if sub_page:
        for sub_page_looped in SUB_PAGES:
            sub_page_page = sub_page_looped.split("/")[0]
            if page == sub_page_page and sub_page == sub_page_looped.split("/")[1]:
                return True
    else:
        if page in PAGES:
            return True
    return False
