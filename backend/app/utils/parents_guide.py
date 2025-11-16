CATEGORY_LABELS = {
    "violence": "Violence & Gore",
    "gore": "Violence & Gore",
    "profanity": "Profanity",
    "drugs": "Alcohol/Drugs/Smoking",
    "sex_act": "Sex & Nudity",
    "nudity": "Sex & Nudity",
    "child_risk": "Frightening & Intense Scenes",
}


def severity_to_gradation(severity: float) -> str:
    """Convert severity score (0-1) to IMDb-style gradation."""
    if severity == 0:
        return "None"
    elif severity < 0.3:
        return "Mild"
    elif severity < 0.6:
        return "Moderate"
    else:
        return "Severe"


def get_category_description(category: str, episodes: int, gradation: str) -> str:
    """Generate description for category based on detections."""
    templates = {
        "violence": {
            "Severe": f"Multiple scenes with graphic violence and weapons ({episodes} instances)",
            "Moderate": f"Several instances of action violence ({episodes} instances)",
            "Mild": f"Occasional violence in action context ({episodes} instances)",
        },
        "gore": {
            "Severe": f"Graphic depictions of blood and injury ({episodes} instances)",
            "Moderate": f"Some bloody violence ({episodes} instances)",
            "Mild": f"Brief moments with blood ({episodes} instances)",
        },
        "profanity": {
            "Severe": f"Pervasive use of strong language throughout ({episodes} instances)",
            "Moderate": f"Frequent profanity in dialogue ({episodes} instances)",
            "Mild": f"Occasional mild profanity ({episodes} instances)",
        },
        "drugs": {
            "Severe": f"Extensive drug use and abuse depicted ({episodes} instances)",
            "Moderate": f"Several scenes involving substance use ({episodes} instances)",
            "Mild": f"Brief references to alcohol or smoking ({episodes} instances)",
        },
        "sex_act": {
            "Severe": f"Explicit sexual content ({episodes} instances)",
            "Moderate": f"Sexual situations and innuendo ({episodes} instances)",
            "Mild": f"Brief sexual references ({episodes} instances)",
        },
        "nudity": {
            "Severe": f"Extensive nudity throughout ({episodes} instances)",
            "Moderate": f"Several scenes with partial nudity ({episodes} instances)",
            "Mild": f"Brief partial nudity ({episodes} instances)",
        },
        "child_risk": {
            "Severe": f"Intense scenes involving children in danger ({episodes} instances)",
            "Moderate": f"Some scenes may be frightening for children ({episodes} instances)",
            "Mild": f"Mild peril involving children ({episodes} instances)",
        },
    }

    if category in templates and gradation in templates[category]:
        return templates[category][gradation]

    return f"{gradation} content detected ({episodes} instances)"
