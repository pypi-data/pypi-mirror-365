import pytest
from versum.crypt.passwd import PasswordManager, PasswordPolicies


# Policy-compliant passwords (lowest policy they target)
# Each strong password should pass strong, medium, and weak
compliant_examples = {
    "weak_only": ("abc123", [PasswordPolicies.WEAK]),
    "medium": ("Abc12345", [PasswordPolicies.WEAK, PasswordPolicies.MEDIUM]),
    "strong": ("Str0ngPassw@rd", [PasswordPolicies.WEAK, PasswordPolicies.MEDIUM, PasswordPolicies.STRONG]),
}


@pytest.mark.parametrize("label,password,allowed_policies", [
    (label, pw, policies)
    for label, (pw, policies) in compliant_examples.items()
])
@pytest.mark.parametrize("policy", list(PasswordPolicies))
def test_policy_compliance_matrix(label, password, allowed_policies, policy):
    manager = PasswordManager(policy=policy)

    should_pass = policy in allowed_policies or policy == PasswordPolicies.NO_POLICY
    result = manager.policy_compliant(password)

    assert result == should_pass, f"Password '{label}' (policy {policy.name}) compliance mismatch"


@pytest.mark.parametrize("policy,password", [
    (PasswordPolicies.NO_POLICY, "abc"),
    (PasswordPolicies.WEAK, "abc123"),
    (PasswordPolicies.MEDIUM, "Abc12345"),
    (PasswordPolicies.STRONG, "Str0ngPassw@rd"),
])
def test_hashing_for_compliant_passwords(policy, password):
    manager = PasswordManager(policy=policy)

    hashed = manager.hash_password(password)
    assert hashed.startswith("$argon2")


@pytest.mark.parametrize("policy,password", [
    (PasswordPolicies.WEAK, "abc"),               # too short
    (PasswordPolicies.MEDIUM, "abc12345"),        # no uppercase
    (PasswordPolicies.STRONG, "Abc123456789"),    # no special char
])
def test_hashing_rejects_noncompliant_passwords(policy, password):
    manager = PasswordManager(policy=policy)

    with pytest.raises(ValueError):
        manager.hash_password(password)


def test_verify_and_rehash():
    password = "Abc12345"
    weak_manager = PasswordManager(time_cost=2, policy=PasswordPolicies.MEDIUM)
    strong_manager = PasswordManager(time_cost=5, policy=PasswordPolicies.MEDIUM)

    old_hash = weak_manager.hash_password(password)

    ok, rotated_hash = strong_manager.verify(password, old_hash)
    assert ok is True
    assert rotated_hash is not None


def test_verify_wrong_password():
    manager = PasswordManager(policy=PasswordPolicies.MEDIUM)
    good_password = "Abcdef12"
    bad_password = "wrongpass"

    hashed = manager.hash_password(good_password)
    ok, new_hash = manager.verify(bad_password, hashed)
    assert ok is False
    assert new_hash is None


def test_check_and_hash_new_password():
    manager = PasswordManager(policy=PasswordPolicies.STRONG)
    password = "Str0ngPassw@rd"

    ok, hashed = manager.check_and_hash(password)
    assert ok is True
    assert isinstance(hashed, str)


def test_check_and_hash_with_existing_valid_hash():
    manager = PasswordManager(policy=PasswordPolicies.MEDIUM)
    password = "Abcdef12"
    hashed = manager.hash_password(password)

    ok, new_hash = manager.check_and_hash(password, stored_hash=hashed)
    assert ok is True
    assert new_hash is None


def test_check_and_hash_with_existing_outdated_hash():
    password = "Str0ngPassw@rd"

    weak_manager = PasswordManager(time_cost=2, policy=PasswordPolicies.STRONG)
    strong_manager = PasswordManager(time_cost=5, policy=PasswordPolicies.STRONG)

    weak_hash = weak_manager.hash_password(password)

    ok, rotated_hash = strong_manager.check_and_hash(password, stored_hash=weak_hash)
    assert ok is True
    assert rotated_hash is not None