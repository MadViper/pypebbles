from hypothesis import HealthCheck, Verbosity, settings


def pytest_configure() -> None:
    settings.register_profile(
        name="dev",
        max_examples=50,
        deadline=200,
    )

    settings.register_profile(
        name="ci",
        max_examples=1000,
        deadline=None,
        suppress_health_check=[
            HealthCheck.too_slow,
        ],
    )

    settings.register_profile(
        name="debug",
        max_examples=10,
        verbosity=Verbosity.verbose,
    )
