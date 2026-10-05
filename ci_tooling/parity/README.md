# parity

Tooling for the `Parity build (external-model EFI)` workflow in `.github/workflows/parity-build.yml`.

The workflow builds the OpenCore EFI for one external Mac model (default `MacBookPro11,3`) on
GitHub-hosted macOS runners with the command the CLI documents:

```
python3 OpenCore-Patcher-GUI.command --build --model MacBookPro11,3 --disable_sip --disable_smb
```

`--disable_sip` and `--disable_smb` are required in CLI mode. Without them `support/arguments.py`
forces SIP and SecureBootModel back on after the model defaults are generated, which the GUI does not do.

Each matrix job publishes its outputs to an orphan branch named
`results/<run-number>-<model>-<runner>-py<python>` so they can be fetched with plain git:

```
git ls-remote --heads origin 'results/*'
git fetch origin 'refs/heads/results/*:refs/remotes/origin/results/*'
```

Contents of a result set:

| File | Meaning |
|---|---|
| `manifest-sha256.txt` | `shasum -a 256` of every file under `Build-Folder/OpenCore-Build`, sorted |
| `tree-sizes.txt` | byte size of every file, same order |
| `config-fields.txt` | the load-bearing `config.plist` values printed by `print-config-fields.py` |
| `ocvalidate.txt` | output of the bundled `payloads/OpenCore/ocvalidate` on the built `config.plist` |
| `build.log` | full build output |
| `env.txt`, `pip-freeze.txt` | runner, macOS, Python and package versions |
| `plists/` | every `.plist`, `.contentFlavour`, `.contentVisibility`, `.strings` and `.yml` file of the tree |

Compare two builds, for example a runner build against a local one:

```
python3 ci_tooling/parity/compare-manifests.py <manifest-A> <tree-A> <manifest-B> <tree-B>
```

The script ignores `#Revision:Build-Version` (the build date) and reports every other
difference per file, with a plist-level key diff for mismatched plists.
