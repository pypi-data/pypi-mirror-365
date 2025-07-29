from pydantic import BaseModel, Field

class CodeSubmission(BaseModel):
    source_code: str
    language_id: int
    stdin: str | None = None
    expected_output: str | None = None
    run_timeout: int | None = None
    memory_limit: int | None = Field(None, description='In kilobytes')
    compile_timeout: int | None = None
    check_timeout: int | None = None