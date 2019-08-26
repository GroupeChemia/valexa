from valexa.core.profiles import Profile


def profile_to_dict(profile: Profile):
    p = dict(profile.__dict__)
    p["model"] = dict(p["model"].__dict__)
    p["model"]["name"] = profile.model.name
    p["levels"] = [l.__dict__ for l in p["levels"]]
    p["series"] = [{
        "series": s.series,
        "level": s.level,
        "concentration": s.concentration,
        "result": s.result,
    } for s in p["series"]]
    return p
    