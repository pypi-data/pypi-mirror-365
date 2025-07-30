#!/usr/bin/env python3
"""
Tests for the hybrid file categorization system in TDD validator.

This test suite verifies that the fast path pattern matching works correctly
and that the LLM fallback is used only when necessary.
"""

import os
import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from cc_validator.tdd_validator import TDDValidator
from cc_validator.file_storage import FileStorage


class TestHybridCategorization:
    """Test the hybrid categorization approach with fast path and LLM fallback"""

    @pytest.fixture
    def tdd_validator(self) -> TDDValidator:
        """Create a TDD validator instance with mocked API"""
        # Create validator with mock API key
        validator = TDDValidator(api_key="test-api-key")
        
        # Mock the internal processors to avoid actual API calls
        validator.processor = Mock()
        validator.file_categorization_processor = Mock()
        
        return validator

    def test_fast_path_test_files(self, tdd_validator: TDDValidator) -> None:
        """Test that test files are correctly identified by fast path"""
        test_cases = [
            ("test_something.py", "test"),
            ("something_test.py", "test"),
            ("module_test.go", "test"),  # Go convention: *_test.go
            ("user_test.go", "test"),
            ("test.py", None),  # Ambiguous - could be test or not
            ("something.spec.ts", "test"),
            ("component.test.js", "test"),
            ("__tests__/component.js", "test"),
            ("tests/integration_test.py", "test"),
            ("src/test/java/TestClass.java", "test"),
        ]
        
        for file_path, expected_category in test_cases:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected_category, f"Failed for {file_path}"

    def test_fast_path_documentation_files(self, tdd_validator: TDDValidator) -> None:
        """Test that documentation files are correctly identified by fast path"""
        test_cases = [
            ("README.md", "docs"),
            ("CHANGELOG.md", "docs"),
            ("LICENSE", None),  # No extension, needs LLM
            ("LICENSE.md", "docs"),  # With extension, fast path works
            ("CONTRIBUTING.md", "docs"),
            ("docs/api.md", "docs"),
            ("documentation/guide.rst", "docs"),
            ("wiki/page.md", "docs"),
            ("ROADMAP.txt", "docs"),
            ("AUTHORS", None),  # No extension, needs LLM
            ("doc/tutorial.adoc", "docs"),
        ]
        
        for file_path, expected_category in test_cases:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected_category, f"Failed for {file_path}"

    def test_fast_path_config_files(self, tdd_validator: TDDValidator) -> None:
        """Test that configuration files are correctly identified by fast path"""
        test_cases = [
            (".gitignore", "config"),
            ("package.json", "config"),
            ("pyproject.toml", "config"),
            ("Cargo.toml", "config"),
            ("tsconfig.json", "config"),
            ("jest.config.js", "config"),  # This is in the known list
            (".eslintrc.js", None),  # Not in known list, needs LLM
            ("Dockerfile", "config"),
            ("docker-compose.yml", "config"),
            ("requirements.txt", "docs"),  # .txt extension matches docs first
            ("Gemfile", None),  # Not in known list, needs LLM
            (".env", None),  # Not in known list, needs LLM
            ("config.yml", "config"),  # Has .yml extension
            ("settings.json", "config"),  # Has .json extension
        ]
        
        for file_path, expected_category in test_cases:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected_category, f"Failed for {file_path}"

    def test_fast_path_structural_files(self, tdd_validator: TDDValidator) -> None:
        """Test that potential structural files need LLM verification"""
        # These files could be structural or implementation - fast path returns None
        ambiguous_structural_files = [
            "__init__.py",  # Could have imports or be empty
            "index.js",     # Could be barrel file or have logic
            "index.ts",     # Could be barrel file or have logic
            "mod.rs",       # Could be module declaration or have logic
            "constants.py", # Not in structural list - could have logic
            "types.ts",     # Not in structural list - could have validation
            "doc.go",       # Could be docs or have logic
            "main.go",      # Could be minimal or have logic
        ]
        
        for file_path in ambiguous_structural_files:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result is None, f"Expected None for ambiguous file {file_path}, got {result}"

    def test_fast_path_generated_files(self, tdd_validator: TDDValidator) -> None:
        """Test that generated files are correctly identified by fast path"""
        test_cases = [
            ("schema.generated.ts", None),  # Generated files need LLM
            ("types.g.dart", None),  # Generated files need LLM
            ("model.freezed.dart", None),  # Generated files need LLM
            ("proto_pb.go", None),  # Doesn't match pattern - needs dot before pb
            ("proto.pb.go", None),  # Generated files need LLM
            ("api.pb.py", None),  # Generated files need LLM
            ("api_pb2.py", None),  # Generated files need LLM
            ("autogen_schema.py", None),  # Doesn't match - no pattern for autogen_
            ("api_generated.py", None),  # Generated files need LLM
            ("package-lock.json", "config"),  # .json extension matches config
            ("yarn.lock", None),  # No matching pattern
            ("Cargo.lock", None),  # No matching pattern  
            ("go.sum", None),  # Lock files need LLM
        ]
        
        for file_path, expected_category in test_cases:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected_category, f"Failed for {file_path}"

    def test_fast_path_data_files(self, tdd_validator: TDDValidator) -> None:
        """Test that data files are correctly identified by fast path"""
        test_cases = [
            ("data.json", "config"),  # .json is config, not data
            ("dataset.csv", None),  # Data files need LLM
            ("fixtures/users.json", "config"),  # .json is config
            ("testdata/sample.xml", None),  # Data files need LLM
            ("mock_data.json", "config"),  # .json is config
            ("seeds/test.sql", None),  # Data files need LLM
            ("config.yaml", "config"),  # .yaml is config
            ("data/values.xml", None),  # Data files need LLM
            ("log.jsonl", None),  # Data files need LLM
            ("stream.ndjson", None),  # Data files need LLM
        ]
        
        for file_path, expected_category in test_cases:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected_category, f"Failed for {file_path}"

    def test_fast_path_returns_none_for_ambiguous(self, tdd_validator: TDDValidator) -> None:
        """Test that ambiguous files return None (need LLM)"""
        ambiguous_files = [
            "main.py",  # Could be structural or implementation
            "app.js",   # Could be structural or implementation
            "service.go",  # Likely implementation but needs content check
            "utils.py",  # Could be either
            "helper.rs",  # Could be either
            "model.dart",  # Could be either
            "handler.ts",  # Could be either
        ]
        
        for file_path in ambiguous_files:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result is None, f"Expected None for ambiguous file {file_path}"

    @pytest.mark.asyncio
    async def test_hybrid_approach_uses_fast_path(self, tdd_validator: TDDValidator) -> None:
        """Test that hybrid approach uses fast path when possible"""
        # Test file should use fast path
        result = await tdd_validator.categorize_file("test_user.py", "def test_create(): pass")
        assert result["category"] == "test"
        assert "Pattern-based categorization" in result["reason"]
        
        # Documentation should use fast path
        result = await tdd_validator.categorize_file("README.md", "# Project Title")
        assert result["category"] == "docs"
        assert "Pattern-based categorization" in result["reason"]

    @pytest.mark.asyncio
    async def test_hybrid_approach_fallback_to_llm(self, tdd_validator: TDDValidator) -> None:
        """Test that hybrid approach falls back to LLM for ambiguous files"""
        # Mock the LLM response
        mock_response = {
            "category": "implementation",
            "requires_tdd": True,
            "reason": "Contains business logic"
        }
        
        # Setup mock to return the response
        mock_part = Mock()
        mock_part.value = json.dumps(mock_response)
        
        tdd_validator.file_categorization_processor.call = AsyncMock()
        tdd_validator.file_categorization_processor.call.return_value.__aiter__.return_value = [mock_part]
        
        # Test with ambiguous file
        result = await tdd_validator.categorize_file(
            "service.py",
            "class UserService:\n    def create_user(self, name): return User(name)"
        )
        
        assert result["category"] == "implementation"
        assert result["requires_tdd"] is True
        assert tdd_validator.file_categorization_processor.call.called

    @pytest.mark.asyncio  
    async def test_llm_fallback_on_error(self, tdd_validator: TDDValidator) -> None:
        """Test fallback logic when LLM fails"""
        # Make LLM fail
        tdd_validator.file_categorization_processor.call = AsyncMock(side_effect=Exception("LLM error"))
        
        # Python file with implementation logic should trigger LLM, which will fail and use fallback
        result = await tdd_validator.categorize_file("service.py", "class UserService: pass")
        # Fallback logic categorizes .py files with classes as implementation
        assert result["category"] == "implementation"
        assert "fallback" in result["reason"].lower()
        assert "LLM categorization failed" in result["reason"]

    def test_fast_path_performance(self, tdd_validator: TDDValidator) -> None:
        """Test that fast path categorization is fast"""
        import time
        
        test_files = [
            "test_user.py",
            "README.md",
            "package.json",
            "__init__.py",
            "data.csv",
            "generated.pb.go",
        ]
        
        start = time.time()
        for _ in range(1000):  # Run 1000 iterations
            for file_path in test_files:
                tdd_validator._fast_path_categorize(file_path)
        elapsed = time.time() - start
        
        # Should be very fast - less than 0.1 seconds for 6000 categorizations
        assert elapsed < 0.1, f"Fast path too slow: {elapsed:.3f}s"

    def test_template_file_categorization(self, tdd_validator: TDDValidator) -> None:
        """Test that template files are correctly categorized"""
        template_files = [
            ("index.html", None),  # HTML not in fast path patterns
            ("template.jinja2", None),  # Template files need LLM
            ("email.html.erb", None),  # Template files need LLM
            ("view.blade.php", None),  # PHP files need LLM
            ("component.vue", None),  # Vue could have logic, needs LLM
            ("page.jsx", None),  # JSX could have logic, needs LLM
        ]
        
        for file_path, expected in template_files:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected, f"Failed for {file_path}"

    def test_migration_file_categorization(self, tdd_validator: TDDValidator) -> None:
        """Test that migration files need LLM categorization"""
        migration_files = [
            ("001_create_users.rb", None),  # Ruby files not in fast path
            ("20240101_add_column.sql", None),  # SQL files need LLM
            ("migrations/001_initial.py", None),  # Ambiguous Python file
            ("db/migrate/create_tables.sql", None),  # SQL files need LLM
        ]
        
        for file_path, expected in migration_files:
            result = tdd_validator._fast_path_categorize(file_path)
            assert result == expected, f"Failed for {file_path}, expected {expected}, got {result}"