This module provides the basis for creating key performance indicators,
including static and dynamic thresholds (SQL query or Python code) on the
local database.

A scheduler runs every hour and updates KPI values based on the periodicity
of each KPI. KPI computation can also be done manually.

A threshold is a list of ranges. Each range has a name, minimum and maximum
values (fixed, SQL query, or Python code), and a color (RGB code).
