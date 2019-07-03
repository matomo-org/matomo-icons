import yaml

with open("tests-ignore.yml") as f:
    data = yaml.safe_load(f)

le = data["less_important_device_detector_icons"]  # type:dict

for category, namelist in le.items():
    print([type(a) for a in namelist])
    print(namelist)
    namelist.sort(key=lambda s: s.casefold())

with open("tests-ignore.yml", "w") as f:
    yaml.safe_dump(data, f)
