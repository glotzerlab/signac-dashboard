import signac

project = signac.init_project()

for value in [1.0, 1.25, 1.5]:
    for category in ["A", "B", "C"]:
        for toggle in [True, False]:
            if value == 1.5 and category == "C":
                sp = dict(value=value, category=category, toggle=toggle, const=2)
            else:
                sp = dict(
                    value=value,
                    category=category,
                    toggle=toggle,
                    const=2,
                    missing_one=1
                )
            job = project.open_job(sp).init()
