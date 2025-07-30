"""Tests for utility functions."""

from src.reqtracker.utils import get_package_name, is_standard_library


class TestGetPackageName:
    """Test cases for get_package_name function."""

    def test_known_mappings(self):
        """Test that known import names are correctly mapped."""
        assert get_package_name("cv2") == "opencv-python"
        assert get_package_name("PIL") == "Pillow"
        assert get_package_name("sklearn") == "scikit-learn"
        assert get_package_name("yaml") == "PyYAML"
        assert get_package_name("bs4") == "beautifulsoup4"

    def test_unknown_imports(self):
        """Test that unknown imports return unchanged."""
        assert get_package_name("numpy") == "numpy"
        assert get_package_name("requests") == "requests"
        assert get_package_name("unknown_module") == "unknown_module"

    def test_case_sensitivity(self):
        """Test that mappings are case-sensitive."""
        assert get_package_name("PIL") == "Pillow"
        assert get_package_name("pil") == "pil"  # Not mapped


class TestIsStandardLibrary:
    """Test cases for is_standard_library function."""

    def test_standard_modules(self):
        """Test that standard library modules are identified."""
        assert is_standard_library("os")
        assert is_standard_library("sys")
        assert is_standard_library("json")
        assert is_standard_library("datetime")

    def test_third_party_modules(self):
        """Test that third-party modules are not identified as stdlib."""
        assert not is_standard_library("numpy")
        assert not is_standard_library("requests")
        assert not is_standard_library("PIL")

    def test_submodules(self):
        """Test that submodules are handled correctly."""
        assert is_standard_library("os.path")
        assert is_standard_library("collections.abc")
        assert not is_standard_library("numpy.array")

    def test_more_stdlib_modules(self):
        """Test additional standard library modules."""
        assert is_standard_library("ast")
        assert is_standard_library("zipfile")
        assert is_standard_library("dataclasses")
        assert is_standard_library("asyncio")


class TestNormalizePackageName:
    """Test cases for normalize_package_name function."""

    def test_lowercase_conversion(self):
        """Test that package names are converted to lowercase."""
        from src.reqtracker.utils import normalize_package_name

        assert normalize_package_name("Django") == "django"
        assert normalize_package_name("Flask") == "flask"
        assert normalize_package_name("PyYAML") == "pyyaml"

    def test_underscore_replacement(self):
        """Test that underscores are replaced with hyphens."""
        from src.reqtracker.utils import normalize_package_name

        assert normalize_package_name("python_dateutil") == "python-dateutil"
        assert normalize_package_name("my_package") == "my-package"

    def test_dot_replacement(self):
        """Test that dots are replaced with hyphens."""
        from src.reqtracker.utils import normalize_package_name

        assert normalize_package_name("backports.csv") == "backports-csv"
        assert normalize_package_name("zope.interface") == "zope-interface"

    def test_multiple_separators(self):
        """Test that multiple separators are collapsed."""
        from src.reqtracker.utils import normalize_package_name

        assert normalize_package_name("my..package__name") == "my-package-name"
        assert normalize_package_name("test---pkg") == "test-pkg"
