from typing import List, Dict


# name, url, marquee, description
def Items(
    items: List[Dict[str, str]],
    sort: bool = False,
) -> List[str]:
    output = [
        (
            "{}[![image]({})]({}) {}".format(
                (
                    "[`{}`]({}) ".format(
                        item["name"],
                        item.get(
                            "url",
                            "#",
                        ),
                    )
                    if item["name"]
                    else ""
                ),
                item.get(
                    "marquee",
                    "https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true",
                ),
                item.get(
                    "url",
                    "#",
                ),
                item.get("description", ""),
            )
            if "name" in item
            else ""
        )
        for item in items
    ]

    if sort:
        output = sorted(output)

    return output
