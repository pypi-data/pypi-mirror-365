import os

from pathlib import Path
from bashguard.analyzers import ScriptAnalyzer
from bashguard.core import Description


def test_path_of_the_unquoted():
    
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_path_of_the_unquoted.sh')
    
    analyzer = ScriptAnalyzer(test_file_path)
    
    vulnerabilities = analyzer.analyze()
    for vuln in vulnerabilities:
        print(vuln)

    assert len(vulnerabilities) == 1
    assert vulnerabilities[0].description == Description.VARIABLE_EXPANSION.value 
    

test_path_of_the_unquoted()