from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.models.project import Project
from backend.app.models.test_case import TestCase
from backend.app.models.test_suite import TestSuite
from backend.app.schemas.test_case import TestCaseCreate, TestCaseUpdate
from backend.app.schemas.test_suite import TestSuiteCreate, TestSuiteUpdate


class TestService:
    # --- Test Suites ---
    @staticmethod
    def create_test_suite(db: Session, project: Project, suite_in: TestSuiteCreate) -> TestSuite:
        suite = TestSuite(
            project_id=project.id,
            name=suite_in.name,
            description=suite_in.description,
        )
        db.add(suite)
        db.commit()
        db.refresh(suite)
        return suite

    @staticmethod
    def get_test_suites(db: Session, project: Project) -> List[TestSuite]:
        return db.query(TestSuite).filter(TestSuite.project_id == project.id).all()

    @staticmethod
    def get_test_suite_by_id(db: Session, suite_id: str, project_id: Optional[str] = None) -> TestSuite:
        query = db.query(TestSuite).filter(TestSuite.id == suite_id)
        if project_id:
            query = query.filter(TestSuite.project_id == project_id)
        suite = query.first()
        if not suite:
            raise EntityNotFoundException("TestSuite", suite_id)
        return suite

    @staticmethod
    def update_test_suite(db: Session, suite_id: str, suite_in: TestSuiteUpdate, project: Project) -> TestSuite:
        suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
        if suite_in.name is not None:
            suite.name = suite_in.name
        if suite_in.description is not None:
            suite.description = suite_in.description
        db.commit()
        db.refresh(suite)
        return suite

    @staticmethod
    def delete_test_suite(db: Session, suite_id: str, project: Project) -> None:
        suite = TestService.get_test_suite_by_id(db, suite_id, project.id)
        db.delete(suite)
        db.commit()

    # --- Test Cases ---
    @staticmethod
    def create_test_case(db: Session, suite: TestSuite, case_in: TestCaseCreate) -> TestCase:
        test_case = TestCase(
            test_suite_id=suite.id,
            name=case_in.name,
            input_prompt=case_in.input_prompt,
            expected_output=case_in.expected_output,
            evaluation_method=case_in.evaluation_method,
            required_keywords=case_in.required_keywords or [],
            forbidden_keywords=case_in.forbidden_keywords or [],
            similarity_threshold=case_in.similarity_threshold or 0.8,
            expected_tool_calls=case_in.expected_tool_calls or [],
            custom_metadata=case_in.custom_metadata or {},
        )
        db.add(test_case)
        db.commit()
        db.refresh(test_case)
        return test_case

    @staticmethod
    def get_test_cases(db: Session, suite: TestSuite) -> List[TestCase]:
        return db.query(TestCase).filter(TestCase.test_suite_id == suite.id).all()

    @staticmethod
    def get_test_case_by_id(db: Session, case_id: str, suite_id: Optional[str] = None) -> TestCase:
        query = db.query(TestCase).filter(TestCase.id == case_id)
        if suite_id:
            query = query.filter(TestCase.test_suite_id == suite_id)
        case = query.first()
        if not case:
            raise EntityNotFoundException("TestCase", case_id)
        return case

    @staticmethod
    def update_test_case(db: Session, case_id: str, case_in: TestCaseUpdate, suite: TestSuite) -> TestCase:
        case = TestService.get_test_case_by_id(db, case_id, suite.id)
        if case_in.name is not None:
            case.name = case_in.name
        if case_in.input_prompt is not None:
            case.input_prompt = case_in.input_prompt
        if case_in.expected_output is not None:
            case.expected_output = case_in.expected_output
        if case_in.evaluation_method is not None:
            case.evaluation_method = case_in.evaluation_method
        if case_in.required_keywords is not None:
            case.required_keywords = case_in.required_keywords
        if case_in.forbidden_keywords is not None:
            case.forbidden_keywords = case_in.forbidden_keywords
        if case_in.similarity_threshold is not None:
            case.similarity_threshold = case_in.similarity_threshold
        if case_in.expected_tool_calls is not None:
            case.expected_tool_calls = case_in.expected_tool_calls
        if case_in.custom_metadata is not None:
            case.custom_metadata = case_in.custom_metadata

        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def delete_test_case(db: Session, case_id: str, suite: TestSuite) -> None:
        case = TestService.get_test_case_by_id(db, case_id, suite.id)
        db.delete(case)
        db.commit()

