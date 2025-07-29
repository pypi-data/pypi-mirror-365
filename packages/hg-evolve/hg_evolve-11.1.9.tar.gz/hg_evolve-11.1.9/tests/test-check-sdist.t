Enable obsolescence to avoid the warning issue when obsmarkers are found

  $ cat << EOF >> "$HGRCPATH"
  > [experimental]
  > evolution = all
  > EOF

  $ cd "$TESTDIR"/..

Archiving to a separate location to avoid hardlink mess when the repo is shared

#if test-repo

  $ . "$RUNTESTDIR/helpers-testrepo.sh"
  $ testrepohg archive "$TESTTMP"/hg-evolve
  $ cd "$TESTTMP"/hg-evolve

#endif

  $ "$PYTHON" setup.py check --metadata --restructuredtext

  $ "$PYTHON" setup.py sdist --dist-dir "$TESTTMP"/dist > /dev/null
  */dist.py:*: UserWarning: Unknown distribution option: 'python_requires' (glob) (?)
    warnings.warn(msg) (?)
  warning: no previously-included files found matching 'docs/tutorial/.netlify'
  warning: no previously-included files found matching '.gitlab-ci.yml'
  warning: no previously-included files found matching '.hg-format-source'
  warning: no previously-included files found matching 'Makefile'
  no previously-included directories found matching 'contrib'
  no previously-included directories found matching 'debian'
  no previously-included directories found matching '.gitlab'
  no previously-included directories found matching 'tests/blacklists'
  $ cd "$TESTTMP"/dist

  $ find hg?evolve-*.tar.gz -size +800000c
  hg?evolve-*.tar.gz (glob)

  $ tar -tzf hg?evolve-*.tar.gz | sed 's|^hg.evolve-[^/]*/||' | sort > ../files
  $ grep -E '^tests/test-.*\.(t|py)$' ../files > ../test-files
  $ grep -E -v '^tests/test-.*\.(t|py)$' ../files > ../other-files
  $ wc -l ../other-files
  ??? ../other-files (glob)
  $ wc -l ../test-files
  ??? ../test-files (glob)
  $ grep -F debian ../files
  tests/test-check-debian.t
  $ grep -F __init__.py ../files
  hgext3rd/__init__.py
  hgext3rd/evolve/__init__.py
  hgext3rd/evolve/thirdparty/__init__.py
  hgext3rd/topic/__init__.py
  $ grep -F common.sh ../files
  docs/tutorial/testlib/common.sh
  tests/testlib/common.sh
  $ grep -F README ../files
  README.rst
  docs/README
  docs/tutorial/README.rst
  hgext3rd/topic/README

  $ grep -E '(gitlab|contrib|hack|format-source)' ../files
  [1]
  $ grep -F legacy.py ../files
  [1]
  $ grep -F netlify ../files
  [1]

#if twine
  $ twine --no-color check *
  Checking hg?evolve-*.tar.gz: PASSED (glob)
#endif
