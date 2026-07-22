#!/usr/bin/env python3
"""Validate task API ServiceMonitor and Service compatibility."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def load_resources(
    path: Path,
    kind: str,
) -> list[dict[str, Any]]:
    """Load Kubernetes resources of the requested kind."""

    if not path.is_file():
        raise SystemExit(f"FAIL: Rendered file not found: {path}")

    resources: list[dict[str, Any]] = []

    with path.open(encoding="utf-8") as stream:
        for document in yaml.safe_load_all(stream):
            if (
                isinstance(document, dict)
                and document.get("kind") == kind
            ):
                resources.append(document)

    return resources


def resource_name(resource: dict[str, Any]) -> str:
    """Return metadata.name from a Kubernetes resource."""

    name = resource.get("metadata", {}).get("name")

    if not isinstance(name, str) or not name:
        raise SystemExit(
            "FAIL: Kubernetes resource has no metadata.name"
        )

    return name


def validate_disabled(
    environment: str,
    rendered_file: Path,
) -> None:
    """Verify that an environment renders no ServiceMonitor."""

    monitors = load_resources(
        rendered_file,
        "ServiceMonitor",
    )

    if monitors:
        names = [resource_name(item) for item in monitors]
        raise SystemExit(
            f"FAIL: {environment} must not render "
            f"ServiceMonitors: {names}"
        )

    print(
        f"PASS: {environment} ServiceMonitor remains disabled"
    )


def validate_dev(rendered_file: Path) -> None:
    """Verify the Dev ServiceMonitor-to-Service contract."""

    services = load_resources(rendered_file, "Service")
    monitors = load_resources(
        rendered_file,
        "ServiceMonitor",
    )

    if len(monitors) != 1:
        raise SystemExit(
            "FAIL: Dev must render exactly one ServiceMonitor, "
            f"found {len(monitors)}"
        )

    monitor = monitors[0]
    monitor_name = resource_name(monitor)
    spec = monitor.get("spec", {})

    selector = (
        spec.get("selector", {})
        .get("matchLabels", {})
    )

    if not isinstance(selector, dict) or not selector:
        raise SystemExit(
            f"FAIL: {monitor_name} has no selector.matchLabels"
        )

    endpoints = spec.get("endpoints", [])

    if len(endpoints) != 1:
        raise SystemExit(
            f"FAIL: {monitor_name} must have exactly one endpoint"
        )

    endpoint = endpoints[0]

    expected_endpoint = {
        "port": "http",
        "path": "/metrics",
        "interval": "30s",
        "scrapeTimeout": "10s",
    }

    for key, expected_value in expected_endpoint.items():
        actual_value = endpoint.get(key)

        if actual_value != expected_value:
            raise SystemExit(
                f"FAIL: {monitor_name} {key} must be "
                f"{expected_value!r}, found {actual_value!r}"
            )

    matching_services: list[dict[str, Any]] = []

    for service in services:
        labels = (
            service.get("metadata", {})
            .get("labels", {})
        )

        if all(
            labels.get(key) == value
            for key, value in selector.items()
        ):
            matching_services.append(service)

    if len(matching_services) != 1:
        matched_names = [
            resource_name(service)
            for service in matching_services
        ]

        raise SystemExit(
            f"FAIL: {monitor_name} matched "
            f"{len(matching_services)} Services: "
            f"{matched_names}"
        )

    service = matching_services[0]
    service_name = resource_name(service)

    port_names = {
        port.get("name")
        for port in service.get("spec", {}).get("ports", [])
    }

    if endpoint["port"] not in port_names:
        raise SystemExit(
            f"FAIL: {monitor_name} expects port "
            f"{endpoint['port']}, but {service_name} "
            f"exposes {sorted(port_names)}"
        )

    print(
        f"PASS: Dev {monitor_name} -> "
        f"{service_name}:http/metrics"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dev",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--staging",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--production",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    validate_dev(args.dev)
    validate_disabled("Staging", args.staging)
    validate_disabled("Production", args.production)

    print(
        "\nTask API metrics discovery contracts passed."
    )


if __name__ == "__main__":
    main()
