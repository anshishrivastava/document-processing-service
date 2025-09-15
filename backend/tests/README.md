# PDF Processor Test Suite

This directory contains comprehensive tests for the PDF Processor application.

## Test Structure

```
backend/tests/
├── __init__.py                 # Test package initialization
├── test_api.py                 # API integration tests
├── test_env.py                 # Environment variable tests
├── test_quick.py               # Quick API availability tests
├── test_pdf_processor.py       # Unit tests for PDF processor
├── run_tests.py                # Test runner for backend tests
└── README.md                   # This file
```

## Test Types

### 1. Unit Tests (`test_pdf_processor.py`)
- **Purpose**: Test individual components in isolation
- **Coverage**: PDFProcessor class methods
- **Dependencies**: pytest, pytest-asyncio
- **Run with**: `pytest tests/test_pdf_processor.py -v`

### 2. Integration Tests
- **Environment Test** (`test_env.py`): Validates environment variable loading
- **API Availability Test** (`test_quick.py`): Checks if API endpoints are accessible
- **API Test** (`test_api.py`): Full end-to-end API testing with PDF upload and processing

## Running Tests

### From Root Directory
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py unit      # Unit tests only
python run_tests.py integration  # Integration tests only
python run_tests.py api       # API tests only
```

### From Backend Directory
```bash
cd backend
source venv/bin/activate

# Run all tests with pytest
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_pdf_processor.py -v

# Run individual test scripts
python tests/test_env.py
python tests/test_quick.py
python tests/test_api.py ../sample.pdf
```

## Test Requirements

### Prerequisites
- Python 3.11+
- Virtual environment activated
- Dependencies installed: `pip install -r requirements.txt`
- API running (for integration tests): `./start.sh`

### Dependencies
- pytest==7.4.3
- pytest-asyncio==0.21.1
- requests (for API tests)
- All application dependencies

## Test Configuration

### pytest.ini
Located in `backend/pytest.ini`, contains:
- Test discovery patterns
- Output formatting options
- Markers for test categorization
- Warning filters

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

## Test Data

### Sample PDF
- Location: `../sample.pdf` (relative to backend directory)
- Used for: PDF processing tests
- Contains: Sample text for testing extraction and analysis

## Continuous Integration

The test suite is designed to be CI/CD friendly:
- All tests can run in headless mode
- Proper exit codes for success/failure
- Comprehensive error reporting
- No interactive prompts

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the correct directory
   - Check that the backend directory is in Python path

2. **API Connection Errors**
   - Make sure the API is running: `./start.sh`
   - Check if Redis is running
   - Verify port 8000 is available

3. **Environment Variable Issues**
   - Ensure `.env` file exists in backend directory
   - Check that GEMINI_API_KEY is set correctly

4. **PDF Processing Errors**
   - Verify sample.pdf exists in root directory
   - Check file permissions
   - Ensure PyPDF can read the file

### Debug Mode
Run tests with verbose output:
```bash
python -m pytest tests/ -v -s --tb=long
```

## Test Coverage

Current test coverage includes:
- ✅ PDF text extraction
- ✅ Gemini AI analysis (mocked and real)
- ✅ Error handling and edge cases
- ✅ API endpoint functionality
- ✅ Environment configuration
- ✅ Complete processing pipeline

## Adding New Tests

1. Create new test file: `test_<component>.py`
2. Follow naming convention: `test_<function_name>`
3. Use appropriate markers: `@pytest.mark.unit` or `@pytest.mark.integration`
4. Add to test runner if needed
5. Update this README

## Performance

- Unit tests: ~1 second
- Integration tests: ~2-3 seconds
- Full API test: ~5-10 seconds (depending on processing time)

Total test suite runtime: ~10-15 seconds
