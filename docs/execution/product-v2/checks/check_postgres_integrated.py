"""D's actual isolated PostgreSQL acceptance plus A's new product flows.

All provider/retrieval fixtures are declared software fixtures. No real model,
managed identity, hosted database or Replit bucket acceptance is implied.
"""
import importlib.util
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'D/check_postgres.py'
spec=importlib.util.spec_from_file_location('minder_a_native_postgres_acceptance',path)
check=importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
check.MODULES += ('test_handoffs','test_generation','test_message_orchestrator','test_starter','test_web_evidence')
if __name__=='__main__':check.main()
