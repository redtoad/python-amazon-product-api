# taken from http://codespeak.net/tox/example/hudson.html

import py
import subprocess

SOURCE = './source'

def test_linkcheck(tmpdir):
    doctrees = tmpdir.join("doctrees")
    htmldir = tmpdir.join("html")
    subprocess.check_call(
        ["sphinx-build", "-W", "-blinkcheck",
          "-d", str(doctrees), SOURCE, str(htmldir)])

def test_build_docs(tmpdir):
    doctrees = tmpdir.join("doctrees")
    htmldir = tmpdir.join("html")
    subprocess.check_call([
        "sphinx-build", "-W", "-bhtml",
          "-d", str(doctrees), SOURCE, str(htmldir)])

