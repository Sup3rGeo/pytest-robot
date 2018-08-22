*** Settings ***
Documentation     An example resource file
Library           time

*** Variables ***
${MULTIPLIER}    2

*** Keywords ***
My Sleep
    [Arguments]        ${time}
    [Documentation]    Opens browser to login page
    Sleep              ${time}

