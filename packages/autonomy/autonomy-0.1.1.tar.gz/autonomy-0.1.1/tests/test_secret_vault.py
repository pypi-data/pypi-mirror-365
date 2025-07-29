from pathlib import Path

from src.core.secret_vault import SecretVault


def test_vault_set_get(tmp_path: Path):
    vault_path = tmp_path / "vault.json"
    key_path = tmp_path / "vault.key"
    vault = SecretVault(vault_path=vault_path, key_path=key_path)
    vault.set_secret("github_token", "secret")

    assert vault.get_secret("github_token") == "secret"


def test_env_override(tmp_path: Path, monkeypatch):
    vault_path = tmp_path / "vault.json"
    key_path = tmp_path / "vault.key"
    vault = SecretVault(vault_path=vault_path, key_path=key_path)
    vault.set_secret("github_token", "secret")
    monkeypatch.setenv("GITHUB_TOKEN", "envtoken")
    assert vault.get_secret("github_token") == "envtoken"


# additional tests


def test_delete_secret(tmp_path: Path):
    vault_path = tmp_path / "vault.json"
    key_path = tmp_path / "vault.key"
    vault = SecretVault(vault_path=vault_path, key_path=key_path)
    vault.set_secret("github_token", "secret")
    vault.delete_secret("github_token")
    assert vault.get_secret("github_token") is None


def test_get_missing_secret(tmp_path: Path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    assert vault.get_secret("missing") is None
