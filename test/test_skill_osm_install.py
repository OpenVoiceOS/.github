import unittest

from os import environ
from os.path import exists, isdir, isfile, join
from shutil import rmtree

from ovos_skills_manager import SkillEntry


class TestOSM(unittest.TestCase):
    def test_osm_install(self):
        branch = environ.get("TEST_BRANCH")
        install_url = f"https://github.com/{environ.get('TEST_REPO')}@{branch}"
        skill = SkillEntry.from_github_url(install_url)
        tmp_skills = "/tmp/osm_installed_skills"
        skill_folder = f"{tmp_skills}/{skill.uuid}"

        if exists(skill_folder):
            rmtree(skill_folder)

        updated = skill.install(folder=tmp_skills, default_branch=branch)
        self.assertEqual(updated, True)
        self.assertTrue(isdir(skill_folder))
        self.assertTrue(isfile(join(skill_folder, "__init__.py")))

        updated = skill.install(folder=tmp_skills, default_branch=branch)
        self.assertEqual(updated, False)


if __name__ == "__main__":
    unittest.main()