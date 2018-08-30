*** settings ***
Documentation   Test suite documentation
Library     time


*** Keywords ***
Sample Keyword
    [Documentation]     Second test
    [Arguments]     ${LALA}
    Run     ${LALA}

*** Test Cases ***
Sample Test 1
    [Documentation]    First test
    [Tags]      tag 1       tag 2
    [Timeout]   10
    Print   Sample Test 1!
    Print   a
	Sleep  5



 
    