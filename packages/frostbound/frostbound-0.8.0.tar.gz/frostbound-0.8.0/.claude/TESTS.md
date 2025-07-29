## **Engineering Protocol: High-Fidelity Unit Testing**

### 📜 **Preamble: The Philosophy of Verifiable Units**

This document defines the official engineering standard for writing unit tests.
A unit test is a formal, programmatic specification of a single, isolated unit
of behavior. Its purpose is to verify business logic, algorithms, and state
transitions with mathematical precision.

**Unit tests are first-class citizens.** They are not secondary artifacts. They
must be fully type-hinted, pass all static analysis checks, and be documented to
a professional standard. They are the first line of defense against regressions
and the living documentation of our system's components. They must be **fast**,
**deterministic**, and **unambiguous**.

A unit test **trusts** its collaborators through the power of abstraction and
test doubles. It verifies the unit's logic, not the integration between
components.

---

### 1. **The Hygiene Imperative: Non-Negotiable Quality Standards**

| Principle                       | Specification & Rationale                                                                                                                                                                           | Litmus Test                                                                                                                         |
| :------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| **Code as Production Code**     | Test code must adhere to the same quality standards as production code. This includes **100% type hinting**, zero linter warnings (`ruff`), and zero `mypy --strict` errors.                        | Does the test suite pass the exact same static analysis and linting pipeline as the application code?                               |
| **Absolute Logical Isolation**  | The unit under test must be completely decoupled from its dependencies using mock objects. There shall be no instantiation of other application classes within a unit test, except for data models. | Does the test file import any concrete class from another module that is not a plain data object or an exception?                   |
| **Documented Intent**           | Every test function and shared fixture must have a formal **Numpy/Sphinx style docstring**. The docstring clarifies the test's hypothesis, its parameters, and its expected outcome.                | Can an engineer understand the purpose, setup, and expected result of a test by reading only its docstring and signature?           |
| **Atomic & Focused Assertions** | Each test function must verify a single logical concept. It should ideally contain only one "Act" and a block of assertions that directly relate to that single action.                             | Does the test function name describe a single, specific behavior? (e.g., `test_when_user_is_archived_apply_discount_raises_error`). |
| **Strictly No I/O**             | A unit test must never access the network, filesystem, database, or any other external process. This is the cardinal rule that guarantees speed and determinism.                                    | Can the entire unit test suite be executed on a machine with no network connection?                                                 |

---

### 2. **The `pytest` Toolkit: Precision Instruments**

Master these `pytest` features to implement the standards above.

#### **Fixtures: Documented & Type-Safe Providers**

Fixtures are the foundation of test setup. They must be fully documented and
hinted.

```python
# tests/unit/conftest.py
from collections.abc import Generator
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture
from your_project.protocols import UserRepository
from your_project.domain.models import User

@pytest.fixture
def mock_user_repo(mocker: MockerFixture) -> MagicMock:
    """A MagicMock fixture for the UserRepository.

    This mock is configured with a `spec` to ensure it adheres
    to the UserRepository protocol, preventing calls to non-existent
    methods.

    Parameters
    ----------
    mocker : MockerFixture
        The pytest-mock mocker fixture.

    Returns
    -------
    MagicMock
        A configured mock object for the UserRepository.
    """
    return mocker.Mock(spec=UserRepository)

@pytest.fixture
def premium_user() -> User:
    """A fixture that returns a standard premium user domain model.

    Returns
    -------
    User
        A User object with `is_premium_member` set to True.
    """
    return User(id=uuid4(), name="Premium User", is_premium_member=True)
```

#### **`pytest.mark.parametrize`: The Engine of Specification**

Use `parametrize` to test a variety of inputs against a single logical
specification, keeping code DRY and intentions clear.

```python
# tests/unit/test_validators.py
import pytest

@pytest.mark.parametrize(
    ("email_input", "is_valid"),
    [
        ("test@example.com", True),
        ("test.name@sub.example.co.uk", True),
        ("invalid-email", False),
        ("test@.com", False),
        ("", False),
    ],
)
def test_email_validator(email_input: str, is_valid: bool) -> None:
    """
    Tests the email validator with various valid and invalid inputs.

    Parameters
    ----------
    email_input : str
        The email string to validate.
    is_valid : bool
        The expected validation outcome.
    """
    assert is_email_valid(email_input) is is_valid
```

---

### 3. **A Step-by-Step Practical Blueprint**

**Scenario**: We will test the same `DiscountService` from the previous guide,
but now adhering to the rigorous engineering standards.

#### **Code to be Tested:**

```python
# your_project/services/discount.py
class DiscountService:
    def __init__(self, user_repo: UserRepository, notifier: NotificationService) -> None:
        self._user_repo = user_repo
        self._notifier = notifier

    def apply_discount(self, user_id: UUID) -> float:
        user = self._user_repo.get_by_id(user_id)
        if not user.is_premium_member:
            raise UserNotEligibleError("User is not a premium member.")
        discount_amount = 50.0
        self._notifier.send_discount_notification(user_id=user_id, amount=discount_amount)
        return discount_amount
```

#### **Test Implementation (`tests/unit/test_discount_service.py`)**

```python
# tests/unit/test_discount_service.py
from uuid import UUID, uuid4
from unittest.mock import MagicMock
import pytest
from your_project.services import DiscountService
from your_project.domain.models import User
from your_project.exceptions import UserNotEligibleError

def test_apply_discount_for_premium_user_returns_amount_and_notifies(
    mock_user_repo: MagicMock,
    mock_notifier: MagicMock,
    premium_user: User,
) -> None:
    """
    Verify discount is applied and notification sent for premium users.

    Parameters
    ----------
    mock_user_repo : MagicMock
        A mock of the UserRepository, configured to return a premium user.
    mock_notifier : MagicMock
        A mock of the NotificationService to assert calls against.
    premium_user : User
        A User domain model for a premium user.
    """
    # Arrange
    service = DiscountService(user_repo=mock_user_repo, notifier=mock_notifier)
    mock_user_repo.get_by_id.return_value = premium_user
    expected_discount = 50.0

    # Act
    actual_discount = service.apply_discount(premium_user.id)

    # Assert
    assert actual_discount == expected_discount
    mock_user_repo.get_by_id.assert_called_once_with(premium_user.id)
    mock_notifier.send_discount_notification.assert_called_once_with(
        user_id=premium_user.id, amount=expected_discount
    )

def test_apply_discount_for_non_premium_user_raises_error(
    mock_user_repo: MagicMock,
    mock_notifier: MagicMock,
) -> None:
    """
    Verify an error is raised for non-premium users.

    The test also ensures that no notification is sent if the business
    rule validation fails.

    Parameters
    ----------
    mock_user_repo : MagicMock
        A mock of the UserRepository, configured to return a non-premium user.
    mock_notifier : MagicMock
        A mock of the NotificationService to assert it was not called.
    """
    # Arrange
    service = DiscountService(user_repo=mock_user_repo, notifier=mock_notifier)
    non_premium_user = User(id=uuid4(), name="Standard User", is_premium_member=False)
    mock_user_repo.get_by_id.return_value = non_premium_user

    # Act & Assert
    with pytest.raises(UserNotEligibleError):
        service.apply_discount(non_premium_user.id)

    mock_notifier.send_discount_notification.assert_not_called()
```

---

---

## **Engineering Protocol: High-Confidence Integration Testing**

### 📜 **Preamble: The Philosophy of Verified Collaboration**

This document defines the official engineering standard for integration testing.
An integration test is a formal specification that verifies the collaboration
contract between two or more components, including live infrastructure
(databases, message queues, APIs). Its purpose is to uncover defects in the
"seams" of the application: data serialization, network communication, database
query syntax, and configuration.

Like unit tests, **integration tests are first-class citizens**. They demand the
same high standard of quality, including **full type hinting**, adherence to
**formal docstrings**, and passing all **static analysis**. They are the
ultimate proof that our system's components function as a cohesive whole.

---

### 1. **The Hygiene Imperative: Non-Negotiable Quality Standards**

| Principle                            | Specification & Rationale                                                                                                                                                                | Litmus Test                                                                                                                          |
| :----------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **Code as Production Code**          | Test code must meet the same quality standards as production code: **100% type hinted**, zero linter errors, and zero `mypy --strict` errors.                                            | Does `make ci` pass successfully on the integration test suite?                                                                      |
| **Documented Intent**                | Every test function and shared fixture must have a formal **Numpy/Sphinx style docstring**, explaining its purpose, setup, and expected side effects in the live infrastructure.         | Can an engineer understand the test's impact on the Dockerized database just by reading the docstring?                               |
| **Real, Ephemeral Infrastructure**   | Tests must execute against **real services** (e.g., a PostgreSQL Docker container), not in-memory substitutes. This is the only way to catch real-world integration bugs.                | Does the test suite connect to the same software (e.g., PostgreSQL 15) that runs in production?                                      |
| **Transactional Isolation**          | Each test function must operate within its own isolated database transaction. The transaction **must be rolled back** upon test completion to ensure a pristine state for the next test. | Can the entire integration test suite be run in a randomized order without any failures?                                             |
| **Test the Contract, Not the Logic** | Do not re-test business logic already covered by unit tests. Focus on verifying the "write-read" contract: did the service call result in the expected state change in the database?     | Does the assertion phase query the database directly to verify the state, rather than just checking the return value of the service? |

---

### 2. **The `pytest` Toolkit: Instruments for Live Testing**

#### **Fixtures: Documented & Type-Safe Infrastructure Management**

Integration fixtures manage live resources. They must be robust, correctly
scoped, and clearly documented.

```python
# tests/integration/conftest.py
from collections.abc import Generator
import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from your_project.infrastructure.database.models import Base
from your_project.infrastructure.repositories import PostgresUserRepository

DATABASE_URL = "postgresql://testuser:testpassword@localhost:5433/testdb"

@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, None, None]:
    """Creates a database engine and schema for the test session.

    Yields
    ------
    Engine
        A SQLAlchemy Engine instance connected to the test database.
    """
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def db_session_factory(db_engine: Engine) -> sessionmaker[Session]:
    """Provides a SQLAlchemy session factory for the entire test session.

    Parameters
    ----------
    db_engine : Engine
        The session-scoped SQLAlchemy engine.

    Returns
    -------
    sessionmaker[Session]
        A factory for creating new Session objects.
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

@pytest.fixture()  # Default 'function' scope
def db_session(db_session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Provides a clean, transaction-wrapped database session for a single test.

    This is the key fixture for test isolation. It begins a transaction,
    yields the session for the test to use, and unconditionally rolls it
    back upon completion.

    Parameters
    ----------
    db_session_factory : sessionmaker[Session]
        The session-scoped factory for creating sessions.

    Yields
    ------
    Session
        An active SQLAlchemy Session within a transaction.
    """
    session = db_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def user_repository(db_session: Session) -> PostgresUserRepository:
    """Provides an instance of the repository using a real DB session.

    Parameters
    ----------
    db_session : Session
        The transaction-wrapped database session for a single test.

    Returns
    -------
    PostgresUserRepository
        A repository instance ready to interact with the test database.
    """
    return PostgresUserRepository(session=db_session)
```

---

### 3. **A Step-by-Step Practical Blueprint**

**Scenario**: We will write a fully-typed and documented integration test to
verify that the `PostgresUserRepository` correctly persists a `User` domain
model to the database.

#### **Test Implementation (`tests/integration/test_user_repository.py`)**

```python
# tests/integration/test_user_repository.py
from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from your_project.domain.models import User as DomainUser
from your_project.infrastructure.repositories import PostgresUserRepository
from your_project.infrastructure.database.models import User as OrmUser

@pytest.mark.integration
def test_add_and_get_user(db_session: Session) -> None:
    """
    Verify that a user can be added and retrieved from the database.

    This test validates the full "write-read" cycle for the
    PostgresUserRepository, ensuring that the domain model is correctly
    mapped to the ORM model and persisted.

    Parameters
    ----------
    db_session : Session
        A clean, transaction-wrapped database session provided by the
        fixture. This session will be used by the repository under test.
    """
    # Arrange
    repo = PostgresUserRepository(session=db_session)
    user_to_add = DomainUser(
        id=uuid4(),
        name="Test User",
        email="integration.test@example.com",
        is_premium_member=True,
    )

    # Act
    repo.add(user_to_add)
    db_session.commit() # In a real scenario, a Unit of Work would handle this.

    # Assert
    retrieved_user = repo.get_by_id(user_to_add.id)

    assert retrieved_user is not None
    assert retrieved_user.id == user_to_add.id
    assert retrieved_user.email == user_to_add.email

    # Also assert by querying directly to be 100% sure of the DB state
    user_in_db = db_session.query(OrmUser).filter_by(id=user_to_add.id).one()
    assert user_in_db.name == "Test User"
```
