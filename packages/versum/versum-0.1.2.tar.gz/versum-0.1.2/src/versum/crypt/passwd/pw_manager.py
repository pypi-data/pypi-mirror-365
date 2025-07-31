import enum
import re
from argon2 import PasswordHasher, exceptions as argon2_exceptions


class PasswordPolicies(enum.Enum):
    NO_POLICY = -1
    WEAK = 0
    MEDIUM = 1
    STRONG = 2


# Precompiled regexes for policy enforcement
_WEAK_RE = re.compile(r"^[a-zA-Z0-9]{6,}$")
_MEDIUM_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$")
_STRONG_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
)


class PasswordManager:
    def __init__(
        self,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        salt_len=16,
        policy: PasswordPolicies = PasswordPolicies.MEDIUM,
    ):
        self.hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
        )
        self.policy = policy

    def policy_compliant(self, password: str) -> bool:
  
        if self.policy == PasswordPolicies.NO_POLICY:
            return True

        # Define all levels
        strength_checks = {
            PasswordPolicies.WEAK: _WEAK_RE.match(password) is not None,
            PasswordPolicies.MEDIUM: _MEDIUM_RE.match(password) is not None,
            PasswordPolicies.STRONG: _STRONG_RE.match(password) is not None,
        }

        match self.policy:
            case PasswordPolicies.WEAK:
                return (
                    strength_checks[PasswordPolicies.WEAK]
                    or strength_checks[PasswordPolicies.MEDIUM]
                    or strength_checks[PasswordPolicies.STRONG]
                )
            case PasswordPolicies.MEDIUM:
                return (
                    strength_checks[PasswordPolicies.MEDIUM]
                    or strength_checks[PasswordPolicies.STRONG]
                )
            case PasswordPolicies.STRONG:
                return strength_checks[PasswordPolicies.STRONG]

        return False

    def hash_password(self, password: str) -> str:
        if not self.policy_compliant(password):
            raise ValueError(
                f"Password does not meet the required policy: {self.policy.name}. "
                "To disable this check (not recommended), use PasswordPolicies.NO_POLICY."
            )
        return self.hasher.hash(password)

    def update_needed(self, stored_hash: str) -> bool:
        """Returns True if the stored hash is outdated (due to changed hashing parameters)."""
        return self.hasher.check_needs_rehash(stored_hash)

    def verify(self, password: str, stored_hash: str) -> tuple[bool, str | None]:
        """
        Verifies a password and returns (is_valid, updated_hash or None).

        - If password is correct and hash is outdated: (True, new_hash)
        - If correct and up-to-date: (True, None)
        - If incorrect: (False, None)
        """
        try:
            valid = self.hasher.verify(stored_hash, password)
            if valid and self.update_needed(stored_hash):
                return True, self.hash_password(password)
            return valid, None
        except argon2_exceptions.VerifyMismatchError:
            return False, None
        except argon2_exceptions.VerificationError:
            return False, None

    def rehash(self, password: str, stored_hash: str) -> str:
        """
        Rehashes the password if the stored hash is outdated. Returns the new hash,
        or the same hash if it's still valid.
        """
        if self.update_needed(stored_hash):
            return self.hash_password(password)
        return stored_hash

    def check_and_hash(self, password: str, stored_hash: str | None = None) -> tuple[bool, str | None]:
        """
        Convenience method:
        - If no stored_hash: hashes a new password if compliant
        - If stored_hash: verifies and optionally rehashes

        Returns: (valid, new_or_existing_hash | None)
        """
        if stored_hash is None:
            return True, self.hash_password(password)

        return self.verify(password, stored_hash)