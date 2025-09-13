##########################
# Basic download/compile
#########################

from textwrap import dedent
import pathlib
import shutil
import zipfile

import pytest

from .testutils import make_crossenv


@pytest.fixture
def hello_module_path(tmp_path: pathlib.Path):
    # It's a huge PITA to do out-of-source with setuptools, so we'll just
    # make a copy.
    source = pathlib.Path(__file__).parent / "sources" / "hello"
    dest = tmp_path / "hello-module"
    shutil.copytree(source, dest)
    return dest


def test_build_simple(tmp_path, host_python, build_python, hello_module_path):

    # Take care to prevent creation of a .pth file; we don't want to have to mess
    # with sitecustomize.py stuff to make this work.
    crossenv = make_crossenv(tmp_path, host_python, build_python)
    crossenv.check_call(["pip", "install", "setuptools"])
    crossenv.check_call(
        [
            "python",
            "setup.py",
            "install",
            "--single-version-externally-managed",
            "--root",
            hello_module_path,
            "--install-lib",
            ".",
        ],
        cwd=hello_module_path,
    )

    host_python.setenv("PYTHONPATH", str(hello_module_path) + ":$PYTHONPATH")
    host_python.check_call(
        [
            host_python.binary,
            "-c",
            dedent(
                """\
            import hello
            assert hello.hello() == 'Hello, world'
            """
            ),
        ]
    )


def test_wheel_simple(tmp_path, host_python, build_python, hello_module_path):

    crossenv = make_crossenv(tmp_path, host_python, build_python)
    crossenv.check_call(["pip", "install", "wheel", "setuptools"])
    crossenv.check_call(["python", "setup.py", "bdist_wheel"], cwd=hello_module_path)

    mods = hello_module_path / "mods"
    for whl in hello_module_path.glob("dist/*.whl"):
        with zipfile.ZipFile(whl) as zp:
            zp.extractall(mods)

    host_python.setenv("PYTHONPATH", str(mods) + ":$PYTHONPATH")
    host_python.check_call(
        [
            host_python.binary,
            "-c",
            dedent(
                """\
            import hello
            assert hello.hello() == 'Hello, world'
            """
            ),
        ]
    )


# def test_pip_install_numpy(tmp_path, host_python, build_python):
#     return
#     crossenv = make_crossenv(tmp_path, host_python, build_python)

#     # Numpy is far too clever, and if it detects that any linear algebra
#     # libraries are available on the build system, then it will happily try to
#     # include them in the host build. Disable them so we have a consistent

#     crossenv.setenv('ATLAS', 'None')

#     # if python_version == 'main':
#     #     # Not sure whose fault this sort of thing is.
#     #     pytest.xfail("Known broken against master branch")

#     crossenv.check_call(['cross-pip', '--no-cache-dir', 'install',
#         'numpy==1.18.1', 'pytest==5.3.5'])

#     # Run some tests under emulation. We don't do the full numpy test suite
#     # because 1) it's very slow, and 2) there are some failing tests.
#     # The failing tests might be an issue with numpy on the given archtecture,
#     # or with qemu, or who knows, but in any case, it's really beyond the scope
#     # of this project to address. We'll choose a quick, but nontrivial set of
#     # tests to run.

#     host_python.setenv('PYTHONPATH',
#             str(crossenv.cross_site_packages) + ':$PYTHONPATH')
#     host_python.check_call([host_python.binary, '-c', dedent('''\
#             import sys, numpy
#             ok = numpy.test(tests=['numpy.polynomial'])
#             sys.exit(ok != True)
#             ''')])


# def test_pip_install_bcrypt(tmp_path, host_python, build_python):
#     return
#     crossenv = make_crossenv(tmp_path, host_python, build_python)
#     crossenv.check_call(['build-pip', '--no-cache-dir', 'install', 'cffi'])
#     crossenv.check_call(['cross-pip', '--no-cache-dir', 'install', 'bcrypt~=3.1.0'])

#     # From the bcrypt test suites
#     host_python.setenv('PYTHONPATH',
#             str(crossenv.cross_site_packages) + ':$PYTHONPATH')
#     output = host_python.check_output([host_python.binary, '-c', dedent('''
#             import bcrypt, sys
#             pw = b"Kk4DQuMMfZL9o"
#             salt = b"$2b$04$cVWp4XaNU8a4v1uMRum2SO"
#             print(bcrypt.hashpw(pw, salt).decode('ascii'))
#             ''')])
#     output = output.strip()
#     expected = b"$2b$04$cVWp4XaNU8a4v1uMRum2SO026BWLIoQMD/TXg5uZV.0P.uO8m3YEm"
#     assert output == expected


def test_build_cross_expose(tmp_path, host_python, build_python):
    # Adapted from https://github.com/benfogle/crossenv/issues/108
    crossenv = make_crossenv(tmp_path, host_python, build_python)

    proj = tmp_path / "dummy-dependency"
    proj.mkdir()
    with open(proj / "dummy_dependency.py", "w"):
        pass
    with open(proj / "pyproject.toml", "w") as fp:
        fp.write(
            dedent(
                """
            [build-system]
            requires = ["setuptools"]
                        
            [project]
            name = "dummy-dependency"
            version = "0.1"
            """
            )
        )

    crossenv.check_call(["build-pip", "--no-cache-dir", "install", "."], cwd=proj)

    proj = tmp_path / "myproj"
    proj.mkdir()
    with open(proj / "dummy.py", "w"):
        pass
    with open(proj / "pyproject.toml", "w") as fp:
        fp.write(
            dedent(
                """
            [build-system]
            requires = ["setuptools", "dummy-dependency"]
            """
            )
        )

    crossenv.check_call(
        ["cross-pip", "--no-cache-dir", "install", "-U", "setuptools", "wheel", "build"]
    )
    crossenv.check_call(
        ["build-pip", "--no-cache-dir", "install", "-U", "setuptools", "wheel", "build"]
    )

    crossenv.check_call(["cross-expose", "dummy-dependency"])

    crossenv.check_call(["cross-python", "-m", "build", "--no-isolation"], cwd=proj)
