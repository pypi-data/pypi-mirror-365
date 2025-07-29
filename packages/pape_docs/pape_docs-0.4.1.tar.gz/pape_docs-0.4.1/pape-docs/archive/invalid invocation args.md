# The script should re-ask for arguments if they were invalid in the invocation

A **bugfix/feature**, created on **July 7, 2025**

## Status

Accepted, implemented

## Description

When the user does `new-doc --priority "::"`, providing a priority number that gets sanitized to an empty string, the script should say that and re-ask for the priority interactively.

Likewise, if the user interactively provides a non-empty string that would gets sanitized to an empty string, they should be told that and re-prompted for the priority string, with a note that they can leave the string empty to use the default value ("????").

The same should also go for the short title. Re-ask if the invocation argument sanitizes to an empty string, and keep re-prompting for the short title if the user provides empty strings or strings that sanitize down to empty strings.
