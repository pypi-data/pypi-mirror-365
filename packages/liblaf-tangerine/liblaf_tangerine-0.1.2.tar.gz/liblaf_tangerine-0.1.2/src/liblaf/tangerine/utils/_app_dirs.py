import platformdirs


def app_dirs() -> platformdirs.AppDirs:
    return platformdirs.AppDirs(appname="liblaf/tangerine", appauthor="liblaf")
