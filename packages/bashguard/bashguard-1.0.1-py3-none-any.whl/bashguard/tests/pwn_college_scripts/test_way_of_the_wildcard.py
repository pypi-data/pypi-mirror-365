import os

from pathlib import Path
from bashguard.analyzers import ScriptAnalyzer
from bashguard.core import Description


def test_way_of_the_wildcard():
    
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_way_of_the_wildcard.sh')
    
    analyzer = ScriptAnalyzer(test_file_path)
    
    vulnerabilities = analyzer.analyze()
    for vuln in vulnerabilities:
        print(vuln)

    assert len(vulnerabilities) == 2
    assert vulnerabilities[0].description == Description.GLOB_EXPANSION.value 
    assert vulnerabilities[1].description == Description.VARIABLE_EXPANSION.value
    

test_way_of_the_wildcard()