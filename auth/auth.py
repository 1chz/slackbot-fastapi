def is_distributor(user_id: str) -> bool:
    with open("distributors.txt", "r") as distributors:
        if user_id not in [
            distributor.strip() for distributor in distributors.readlines()
        ]:
            return False

    return True
