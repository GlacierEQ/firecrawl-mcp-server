"""Static release-integrity regression for GHCR publishing workflows."""

from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRECTORY = REPOSITORY_ROOT / ".github/workflows"
PINNED_ACTIONS = {
    "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
    "docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9",
    "docker/setup-buildx-action@8d2750c68a42422c14e847fe6c8ac0403b4cbd6f",
    "docker/build-push-action@10e90e3645eae34f1e60eeb005ba3a3d33f178e8",
}


def _load_workflow(name: str) -> dict:
    return yaml.safe_load((WORKFLOW_DIRECTORY / name).read_text(encoding="utf-8"))


def _actions(workflow: dict) -> set[str]:
    return {
        step["uses"]
        for step in workflow["jobs"]["push-image"]["steps"]
        if "uses" in step
    }


def _tags(workflow: dict) -> str:
    steps = workflow["jobs"]["push-image"]["steps"]
    return next(step["with"]["tags"] for step in steps if "tags" in step.get("with", {}))


def test_publish_workflows_pin_actions_and_declare_package_permissions():
    for name in ("image.yml", "image-staging.yml"):
        workflow = _load_workflow(name)

        assert workflow["permissions"] == {"contents": "read", "packages": "write"}
        assert PINNED_ACTIONS <= _actions(workflow)


def test_publish_workflows_retain_latest_and_add_immutable_commit_tags():
    for name in ("image.yml", "image-staging.yml"):
        tags = _tags(_load_workflow(name))

        assert ":latest" in tags
        assert ":${{ github.sha }}" in tags
