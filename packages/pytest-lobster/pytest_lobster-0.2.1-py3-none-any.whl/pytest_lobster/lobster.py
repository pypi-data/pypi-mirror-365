import pytest
import dataclasses
import json
import pathlib
from typing import List


def pytest_addoption(parser):
    parser.addoption(
        "--lobster", action="store", type=pathlib.Path, help="filename for lobster file"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "trace_to(requirment): trace the requirements")
    config.addinivalue_line(
        "markers", "justification(justification): justification for the test"
    )


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers(name="trace_to"):
            trace_to = marker.args[0]
            item.user_properties.append(("trace_to", trace_to))
        for marker in item.iter_markers(name="justification"):
            justification = marker.args[0]
            item.user_properties.append(("justification", justification))


@dataclasses.dataclass
class LobsterFileReference:
    file: str
    line: int | None
    column: int | None
    kind: str = "file"

    @staticmethod
    def from_item(item: pytest.Item):
        (relfspath, lineno, testname) = item.location
        return LobsterFileReference(relfspath, lineno, None)


@dataclasses.dataclass
class LobsterActivity:
    tag: str
    location: LobsterFileReference
    name: str
    refs: List[str]
    just_up: List[str]
    just_down: List[str]
    just_global: List[str]
    framework: str
    kind: str
    status: str | None

    @staticmethod
    def from_item(item: pytest.Item) -> "LobsterActivity":
        activity = LobsterActivity(
            "pytest " + item.nodeid,
            LobsterFileReference.from_item(item),
            item.name,
            LobsterActivity._get_trace(item),
            LobsterActivity._get_justifications(item),
            [],
            [],
            "PyTest",
            "Test",
            None,
        )
        return activity

    @staticmethod
    def _get_justifications(item):
        just_up = []
        for marker in item.own_markers:
            if marker.name == "justification":
                for arg in marker.args:
                    just_up.append(arg)
        return just_up

    @staticmethod
    def _get_trace(item):
        refs = []
        for marker in item.own_markers:
            if marker.name == "trace_to":
                for arg in marker.args:
                    refs.append(f"req {arg}")
        return refs


@dataclasses.dataclass
class Lobster:
    data: List[LobsterActivity] = dataclasses.field(default_factory=list)
    schema: str = "lobster-act-trace"
    version: int = 3
    generator: str = "pytest_lobster"

    def have_item(self, key: str) -> bool:
        lobster_key = "pytest " + key
        return any(i.tag == lobster_key for i in self.data)

    def update_activity_status(self, key: str, status: str) -> None:
        tag = "pytest " + key
        for item in self.data:
            if item.tag == tag:
                item.status = status


@dataclasses.dataclass
class LobsterMin:
    version: int = 3
    schema: str = "lobster-act-trace"
    generator: str = "pytest_lobster"


lobster_report_key = pytest.StashKey[Lobster]()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    if dont_make_lobster_report(item.session):
        return

    lobster = item.session.stash[lobster_report_key]
    if not lobster.have_item(item.nodeid):
        lobster.data.append(LobsterActivity.from_item(item))
    lobster.update_activity_status(item.nodeid, status_of_call(call))


def status_of_call(call):
    if call.excinfo:
        if call.excinfo.typename is "Skipped":
            new_status = "not run"
        else:
            new_status = "fail"
    else:
        new_status = "ok"
    return new_status


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    file_name = session.config.getoption("--lobster")
    if file_name:
        lobster = Lobster()
        session.stash[lobster_report_key] = lobster


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    if dont_make_lobster_report(session):
        return

    report = session.stash[lobster_report_key]
    lobster_json = json.dumps(dataclasses.asdict(report))
    file_name = session.config.getoption("--lobster")
    if file_name:
        with file_name.open("w") as f:
            f.write(lobster_json)


def dont_make_lobster_report(session):
    return not lobster_report_key in session.stash
