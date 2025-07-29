# Welcome to the `statement-reader`

## About

Welcome to the official documentation for **statement-reader** — a Python library designed to help you extract and structure data from bank PDF statements.

Banking operations are often provided in PDF format, which is great for human readability but not ideal for further processing by computers. This library solves that problem by parsing unstructured PDF text into structured Python objects that can be easily analyzed, stored, or visualized.

---

## Basic usage

```python
import psycopg2
from statement_reader.parsers import SberParser
from statement_reader.models import Operation
from pypdf import PdfReader

data: list[Operation] = []

reader = PdfReader("example.pdf")
for page in reader.pages:
    raw_str = page.extract_text()
    data.extend(SberParser.parse_lines(str_=raw_str))

conn = psycopg2.connect(dsn="postgres://postgres:secretpassword@localhost:15432/postgres")
with conn.cursor() as c:
    c.execute("DELETE FROM public.stats")
    for operation in data:
        c.execute(
            f"""
                INSERT INTO public.stats (date_, time, category, income, remains, sum, weekday)
                VALUES (%(date)s, %(time)s, %(category)s, %(is_income)s, %(remains)s, %(sum)s, %(weekday)s);
            """, operation.model_dump()
        )
conn.commit()
```

---

## Why Use `statement-reader`?

- ✅ **Extracts key operation fields**: date, time, category, amount, balance, and more.
- ✅ **Supports income/expense classification** based on the transaction pattern.
- ✅ **Automatically cleans up** non-breaking spaces and commas for correct numeric parsing.
- ✅ **Returns structured Python objects** for easy integration with other tools and libraries.
- ✅ **Designed for Sberbank** statement lines, but extensible to other formats.

---

## Getting Started

To get started, install the package:

```commandline
pip install statement-reader
```

---

## Usage

Use it to parse a line from a Sberbank statement:

```python
from statement_reader.parsers import SberParser
line = "12.03.2024 14:22 456789 КАФЕ +100.00 12345.67" 
operation = SberParser.parse_main_line(line)
print(operation.model_dump())
#> {
#>  'date': '2024-03-12',
#>  'time': '14:22',
#>  'category': 'КАФЕ',
#>  'sum': 100.0,
#>  'remains': 12345.67,
#>  'is_income': True,
#>  'weekday': 2
#> }
```

---

## API Reference

For full details about classes, methods, and parameters, check out the API reference.
