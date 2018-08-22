from pytest_robot import robot2py


session_vars = {"RESOURCES": "Typhoonhilkeywords"
                             "TARGET:" "typhoonhil"}

file = robot2py("Sample2.robot", session_vars)
file = robot2py("ExampleResource.robot", session_vars)

