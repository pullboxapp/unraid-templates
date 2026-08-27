from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
RAW_ROOT = "https://raw.githubusercontent.com/pullboxapp/unraid-templates/main"
EXPECTED_TEMPLATES = {
    "pullbox.xml": "ghcr.io/pullboxapp/pullbox:latest",
    "pullbox-provider-getcomics.xml": (
        "ghcr.io/pullboxapp/pullbox-provider-getcomics:latest"
    ),
    "pullbox-provider-annas-archive.xml": (
        "ghcr.io/pullboxapp/pullbox-provider-annas-archive:latest"
    ),
}
PLACEHOLDERS = ("YOUR_", "example-app", "container_name", "YOUR ")


def _required_text(root: ET.Element, tag: str) -> str:
    node = root.find(tag)
    if node is None or not (node.text or "").strip():
        raise AssertionError(f"<{tag}> must be present and non-empty")
    return (node.text or "").strip()


class RepositoryContractTests(unittest.TestCase):
    def test_repository_uses_pullbox_license(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("GNU GENERAL PUBLIC LICENSE", license_text)
        self.assertIn("Version 3, 29 June 2007", license_text)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("GPL-3.0-or-later", readme)

    def test_profile_is_complete_and_has_no_starter_placeholders(self) -> None:
        profile_path = ROOT / "ca_profile.xml"
        profile_text = profile_path.read_text(encoding="utf-8")
        root = ET.fromstring(profile_text)
        self.assertEqual(root.tag, "CommunityApplications")
        _required_text(root, "Profile")
        self.assertEqual(_required_text(root, "Icon"), f"{RAW_ROOT}/icon.png")
        _required_text(root, "WebPage")
        for placeholder in PLACEHOLDERS:
            self.assertNotIn(placeholder, profile_text)

    def test_exact_production_template_inventory(self) -> None:
        paths = {path.name for path in TEMPLATES.glob("*.xml")}
        self.assertEqual(paths, set(EXPECTED_TEMPLATES))
        self.assertFalse((ROOT / "plugins").exists())

    def test_templates_follow_the_unraid_and_pullbox_contracts(self) -> None:
        for filename, image in EXPECTED_TEMPLATES.items():
            with self.subTest(template=filename):
                path = TEMPLATES / filename
                template_text = path.read_text(encoding="utf-8")
                root = ET.fromstring(template_text)
                self.assertEqual(root.tag, "Container")
                self.assertEqual(root.attrib.get("version"), "2")
                for tag in (
                    "Name",
                    "Repository",
                    "Registry",
                    "Network",
                    "Shell",
                    "Privileged",
                    "Icon",
                    "Overview",
                    "Project",
                    "Support",
                    "TemplateURL",
                    "Category",
                    "License",
                ):
                    _required_text(root, tag)
                self.assertEqual(_required_text(root, "Repository"), image)
                self.assertEqual(
                    _required_text(root, "TemplateURL"),
                    f"{RAW_ROOT}/templates/{filename}",
                )
                self.assertEqual(
                    _required_text(root, "Icon"), f"{RAW_ROOT}/icon.png"
                )
                self.assertEqual(_required_text(root, "Privileged"), "false")
                self.assertEqual(_required_text(root, "License"), "GPL-3.0-or-later")
                for placeholder in PLACEHOLDERS:
                    self.assertNotIn(placeholder, template_text)

    def test_providers_are_hardened_and_offer_only_an_optional_fallback_port(self) -> None:
        for filename in (
            "pullbox-provider-getcomics.xml",
            "pullbox-provider-annas-archive.xml",
        ):
            with self.subTest(template=filename):
                root = ET.parse(TEMPLATES / filename).getroot()
                extra = _required_text(root, "ExtraParams")
                for argument in (
                    "--user=65532:65532",
                    "--read-only",
                    "--cap-drop=ALL",
                    "--security-opt=no-new-privileges",
                    "--tmpfs=/tmp:rw,noexec,nosuid,size=16m",
                ):
                    self.assertIn(argument, extra)

                configs = root.findall("Config")
                tokens = [node for node in configs if node.attrib.get("Target") == "PULLBOX_PROVIDER_TOKEN"]
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].attrib.get("Required"), "true")
                self.assertEqual(tokens[0].attrib.get("Mask"), "true")
                self.assertFalse((tokens[0].text or "").strip())

                ports = [node for node in configs if node.attrib.get("Type") == "Port"]
                self.assertEqual(len(ports), 1)
                self.assertEqual(ports[0].attrib.get("Required"), "false")
                self.assertFalse((ports[0].text or "").strip())


if __name__ == "__main__":
    unittest.main()
