from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.schemas.test_case import (
    TestCaseCreate,
    TestCaseResponse,
    TestCaseUpdate,
)
from backend.app.schemas.test_suite import (
    TestSuiteCreate,
    TestSuiteResponse,
    TestSuiteUpdate,
)
from backend.app.services.test_service import TestService

router = APIRouter()


# --- Test Suites ---
@router.post("/projects/{project_id}/test-suites", response_model=TestSuiteResponse, status_code=status.HTTP_201_CREATED)
def create_test_suite(
    suite_in: TestSuiteCreate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Create a new test suite within a project."""
    return TestService.create_test_suite(db, project, suite_in)


@router.get("/projects/{project_id}/test-suites", response_model=List[TestSuiteResponse])
def get_test_suites(
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List all test suites for a project."""
    return TestService.get_test_suites(db, project)


@router.get("/projects/{project_id}/test-suites/{suite_id}", response_model=TestSuiteResponse)
def get_test_suite(
    suite_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Get test suite details."""
    return TestService.get_test_suite_by_id(db, suite_id, project.id)


@router.patch("/projects/{project_id}/test-suites/{suite_id}", response_model=TestSuiteResponse)
def update_test_suite(
    suite_id: str,
    suite_in: TestSuiteUpdate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Update test suite name or description."""
    return TestService.update_test_suite(db, suite_id, suite_in, project)


@router.delete("/projects/{project_id}/test-suites/{suite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_suite(
    suite_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Delete a test suite and its test cases."""
    TestService.delete_test_suite(db, suite_id, project)


# --- Test Cases ---
@router.post(
    "/projects/{project_id}/test-suites/{suite_id}/cases",
    response_model=TestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_case(
    suite_id: str,
    case_in: TestCaseCreate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Create a new test case in a test suite."""
    suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
    return TestService.create_test_case(db, suite, case_in)


@router.get(
    "/projects/{project_id}/test-suites/{suite_id}/cases",
    response_model=List[TestCaseResponse],
)
def get_test_cases(
    suite_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List test cases in a test suite."""
    suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
    return TestService.get_test_cases(db, suite)


@router.get(
    "/projects/{project_id}/test-suites/{suite_id}/cases/{case_id}",
    response_model=TestCaseResponse,
)
def get_test_case(
    suite_id: str,
    case_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Get single test case details."""
    suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
    return TestService.get_test_case_by_id(db, case_id, suite.id)


@router.patch(
    "/projects/{project_id}/test-suites/{suite_id}/cases/{case_id}",
    response_model=TestCaseResponse,
)
def update_test_case(
    suite_id: str,
    case_id: str,
    case_in: TestCaseUpdate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Update a test case."""
    suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
    return TestService.update_test_case(db, case_id, case_in, suite)


@router.delete(
    "/projects/{project_id}/test-suites/{suite_id}/cases/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_test_case(
    suite_id: str,
    case_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Delete a test case."""
    suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
    TestService.delete_test_case(db, case_id, suite)

