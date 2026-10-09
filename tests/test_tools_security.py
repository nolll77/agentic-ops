import pytest
import time
from agentic_ops.tools.base import SecurityException
from agentic_ops.tools.data import ExecuteSql
from agentic_ops.tools.infra import CheckDatabaseHealth

def test_readonly_tool_executes_without_approval():
    tool = CheckDatabaseHealth()
    result = tool.run(db_name="mlops_db")
    assert "Ping réussi sur mlops_db" in result

def test_dangerous_tool_blocked_without_approval():
    tool = ExecuteSql()
    with pytest.raises(SecurityException) as exc:
        tool.run(query="DROP TABLE users;", database="mlops_db")
    
    assert "nécessite une élévation de privilège" in str(exc.value)

def test_dangerous_tool_allowed_with_approval():
    tool = ExecuteSql()
    result = tool.run(query="DROP TABLE users;", database="mlops_db", approved_by_admin=True)
    assert "Exécution SQL" in result

