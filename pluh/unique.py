_seen = set()


def generate_unique_name(want: str) -> str:
    result = want
    suffix = 1
    while result in _seen:
        result = f"{want}{suffix}"
        suffix += 1

    _seen.add(result)
    return result


def reset_unique_name_generator() -> None:
    _seen.clear()
