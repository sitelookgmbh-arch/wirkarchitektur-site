#!/usr/bin/env python3
"""Integrationstests in isolierten Git-Repositories, einschließlich Mutationen."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('changelog-sammeln.sh')
ORIGINAL = '# Changelog\n\n## [Unreleased]\n\n### Fixed\n- Bestehend.\n\n## [0.1.0]\n\n- Alt.\n'


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=os.devnull)
        self.git('init', '-b', 'test')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.root / 'werkzeuge').mkdir()
        self.script = self.root / 'werkzeuge/changelog-sammeln.sh'
        shutil.copyfile(SCRIPT, self.script)
        (self.root / 'changelog.d').mkdir()
        (self.root / 'changelog.d/README.md').write_text('Dokumentation\n')
        (self.root / 'CHANGELOG.md').write_text(ORIGINAL)
        self.fragment('b', 'Fixed\n- Korrektur.\n  Fortsetzung.\n')
        self.fragment('a', 'Added\n- Neu.\n')
        self.commit()

    def git(self, *args, check=True):
        return subprocess.run(['git', *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=check)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-m', 'Test fixture')

    def fragment(self, name, body):
        (self.root / f'changelog.d/{name}.md').write_text(body)

    def run_collector(self, *args):
        return subprocess.run(['bash', str(self.script), *args], cwd=self.root,
                              env=self.env, capture_output=True, text=True)

    def assert_collection(self):
        result = self.run_collector('1.0.0')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / 'CHANGELOG.md').read_text()
        self.assertIn('### Added\n- Neu.', text)
        self.assertIn('### Fixed\n- Korrektur.\n  Fortsetzung.', text)
        self.assertLess(text.index('## [1.0.0]'), text.index('## [0.1.0]'))
        self.assertEqual(text.split('## [1.0.0]')[0].rstrip(),
                         ORIGINAL.split('## [0.1.0]')[0].rstrip())
        self.assertTrue(text.endswith('## [0.1.0]\n\n- Alt.\n'))
        for name in ('a', 'b'):
            self.assertTrue((self.root / f'changelog.d/archive/1.0.0/{name}.md').is_file())
            self.assertFalse((self.root / f'changelog.d/{name}.md').exists())

    def test_collection_and_dry_run(self):
        head = self.git('rev-parse', 'HEAD').stdout
        result = self.run_collector('--dry-run', '1.0.0')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('### Added\n- Neu.', result.stdout)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')
        self.assert_collection()
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout, head)
        self.commit()
        self.assertNotEqual(self.run_collector('1.0.0').returncode, 0)

    def test_first_collection(self):
        unreleased = ORIGINAL.split('## [0.1.0]')[0].rstrip() + '\n'
        (self.root / 'CHANGELOG.md').write_text(unreleased)
        self.commit()
        result = self.run_collector('1.0.0')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / 'CHANGELOG.md').read_text()
        self.assertTrue(text.startswith(unreleased + '\n## [1.0.0] - '))
        self.assertIn('### Added\n- Neu.\n', text)
        self.assertIn('### Fixed\n- Korrektur.\n  Fortsetzung.\n', text)
        for name in ('a', 'b'):
            self.assertFalse((self.root / f'changelog.d/{name}.md').exists())
            self.assertTrue((self.root / f'changelog.d/archive/1.0.0/{name}.md').is_file())

    def test_tight_lists(self):
        self.fragment('aa', 'Added\n\n- Zweiter Punkt.\n\n')
        self.fragment('ab', 'Added\n- Ohne Schlussumbruch.')
        self.commit()
        result = self.run_collector('1.0.0')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / 'CHANGELOG.md').read_text()
        self.assertIn('### Added\n- Neu.\n- Zweiter Punkt.\n- Ohne Schlussumbruch.\n\n### Fixed', text)
        self.assertIn('  Fortsetzung.\n\n## [0.1.0]', text)

    def test_rejections_do_not_write(self):
        for args in ((), ('../bad',), ('--unknown',), ('1.0.0', '2.0.0')):
            with self.subTest(args=args):
                self.assertNotEqual(self.run_collector(*args).returncode, 0)
                self.assertEqual(self.git('status', '--porcelain').stdout, '')
        for body in ('Other\n- Text.\n', 'Fixed\n', 'Fixed\nText.\n'):
            self.fragment('a', body)
            self.commit()
            self.assertNotEqual(self.run_collector('1.0.0').returncode, 0)
            self.assertEqual(self.git('status', '--porcelain').stdout, '')

    def test_dirty_tree(self):
        for path in ('untracked', 'CHANGELOG.md'):
            p = self.root / path
            p.write_text((ORIGINAL if path == 'CHANGELOG.md' else '') + 'changed\n')
            before = {str(f.relative_to(self.root)): f.read_bytes()
                      for f in self.root.rglob('*')
                      if f.is_file() and '.git' not in f.relative_to(self.root).parts}
            for args in (('1.0.0',), ('1.0.0', '--dry-run')):
                result = self.run_collector(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Arbeitsbaum nicht sauber', result.stderr)
                after = {str(f.relative_to(self.root)): f.read_bytes()
                         for f in self.root.rglob('*')
                         if f.is_file() and '.git' not in f.relative_to(self.root).parts}
                self.assertEqual(before, after)
            if path == 'untracked':
                p.unlink()

    def test_archive_collision_and_symlink(self):
        archive = self.root / 'changelog.d/archive/1.0.0'
        archive.mkdir(parents=True)
        (archive / 'a.md').write_text('Existing')
        self.commit()
        self.assertNotEqual(self.run_collector('1.0.0').returncode, 0)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')
        fragment = self.root / 'changelog.d/a.md'
        fragment.unlink()
        fragment.symlink_to('b.md')
        self.commit()
        self.assertNotEqual(self.run_collector('2.0.0').returncode, 0)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')

    def test_no_fragments(self):
        for name in ('a', 'b'):
            (self.root / f'changelog.d/{name}.md').unlink()
        self.commit()
        self.assertNotEqual(self.run_collector('1.0.0').returncode, 0)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')

    def test_main_rejected(self):
        self.git('branch', '-m', 'main')
        self.assertNotEqual(self.run_collector('1.0.0').returncode, 0)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')

    def test_separate_branches_merge(self):
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        for branch in ('first', 'second'):
            self.git('checkout', '-b', branch, base)
            self.fragment(branch, 'Changed\n- Eigene Änderung.\n')
            self.commit()
            self.assertEqual(self.git('diff', '--name-only', base).stdout.strip(),
                             f'changelog.d/{branch}.md')
        merged = self.git('merge-tree', '--write-tree', 'first', 'second')
        tree = merged.stdout.strip()
        for branch in ('first', 'second'):
            self.assertIn('Eigene Änderung', self.git('show', f'{tree}:changelog.d/{branch}.md').stdout)

    def test_mutations_detected(self):
        original = self.script.read_text()
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        mutations = {
            'Erste Sammlung fehlt': ('END {if (!done) {print ""; insert()}}', 'END {}'),
            'Lockere Listen': (
                '''awk 'NR > 1 && NF {print}' "$file" >> "$tmp/$section"''',
                '''tail -n +2 "$file" >> "$tmp/$section"; printf '\\n' >> "$tmp/$section"'''),
            'Fragment fehlt': ('cat "$tmp/$section"', ':'),
            'Falscher Abschnitt': ("printf '\\n### %s\\n' \"$section\"", "printf '\\n### Wrong\\n'"),
            'Schmutziger Baum akzeptiert': ('[ -z "$(git status --porcelain --untracked-files=all)" ]', 'true'),
        }
        for name, (old, new) in mutations.items():
            with self.subTest(mutation=name):
                self.git('reset', '--hard', base)
                self.git('clean', '-fd')
                self.assertEqual(original.count(old), 1)
                self.script.write_text(original.replace(old, new))
                self.commit()
                if name == 'Schmutziger Baum akzeptiert':
                    (self.root / 'CHANGELOG.md').write_text(ORIGINAL + 'changed\n')
                    with self.assertRaises(AssertionError):
                        self.assertNotEqual(self.run_collector('1.0.0').returncode, 0)
                elif name == 'Erste Sammlung fehlt':
                    with self.assertRaises(AssertionError):
                        self.test_first_collection()
                elif name == 'Lockere Listen':
                    with self.assertRaises(AssertionError):
                        self.test_tight_lists()
                else:
                    preview = self.run_collector("1.0.0", "--dry-run")
                    self.assertEqual(preview.returncode, 0, preview.stderr)
                    with self.assertRaises(AssertionError):
                        self.assert_collection()
                print(f'Rot-Beweis: {name} erkannt')


if __name__ == '__main__':
    unittest.main(verbosity=2)
