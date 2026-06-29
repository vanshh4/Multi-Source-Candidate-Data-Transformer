# **Prerequisites and Technologies**



To do this entirely offline and for free, Python is the absolute best language choice due to its robust data and NLP ecosystem.



* Language : Python 3.9+

* Structured Parsing: Built-in `csv` module or `pandas` (for CSV handling).

* Unstructured Parsing (PDF): `pdfplumber` (to extract raw text from PDFs).

* Unstructured Parsing (DOCX): `python-docx` (to extract text from Word documents).

* Local NLP / Entity Extraction: `spaCy` (a free, local, powerful NLP library for Named Entity Recognition to find names, companies, and locations).

* Specialized Formatting : `phonenumbers` (a Google port for E.164 phone number parsing) and built-in `re` (Regular Expressions for emails and dates).

* Validation : `pydantic` or `jsonschema` (to easily validate your final JSON against the schema).



\---



## Phase 1: Technical Design \& The One-Pager



Before writing any code, you must produce a one-page PDF named `\_\_Eightfold.pdf`. This is a mandatory step where evaluators see how you think.



\* Define your pipeline steps (e.g., Ingest → Extract → Normalize → Merge → Project → Validate).

\* Document your canonical schema based on the provided default schema.





\* Outline your normalization rules, explicitly stating how you will format E.164 phones and ISO-3166 locations.





\* Define your conflict-resolution policy. For example, decide if a Recruiter CSV has a higher confidence score for a current job title than a potentially outdated resume.





\* Identify 3 to 5 edge cases, such as a candidate having a completely garbled PDF resume or a CSV missing the name column, and explain how you will handle them.







\---



\### Phase 2: Ingestion \& Extraction (The Core Engine)



This phase is about reading the files and getting the data into a usable format in Python.



\* Build a CSV reader function that maps the structured rows (name, email, phone, current\_company, title) into Python dictionaries.





\* Build a document reader function that checks the file extension of the resume and uses either `pdfplumber` (for PDF) or `python-docx` (for DOCX) to extract all raw prose into a single text string.





\* Write extraction logic for the resume text using Regular Expressions to accurately find emails, phone numbers, and dates.

\* Implement `spaCy` to run over the resume text to extract unstructured entities like Candidate Name and Organizations (Companies/Universities).

\* Format the extracted dates to YYYY-MM and format all phone numbers to the E.164 standard using your chosen libraries.







\---



\### Phase 3: Merging \& The Canonical Profile



Now you must combine the CSV data and the Resume data into one single, trustworthy profile.



\* Initialize your canonical profile dictionary containing all the required fields like `candidate\_id`, `full\_name`, `emails`, `skills`, `experience`, and `provenance`.





\* Implement your merge logic. If the CSV and the Resume provide different phone numbers, append both to the `phones` array. If they provide conflicting current titles, use the confidence scores you established in Phase 1 to pick the winner.





\* Attach provenance data to every single field you populate, noting the source (e.g., "Resume") and the method (e.g., "Regex" or "spaCy").





\* Enforce the primary constraint: unknown values must become `null`, and you must never invent data. If a source is garbage, the system must not crash; it must degrade gracefully.







\---



\### Phase 4: The Projection Layer (The Twist)



You must build a runtime configuration layer that reshapes the output without changing your core engine code. Keep a clean separation between your internal canonical record and this projection layer.



\* Create a dedicated function that accepts two arguments: your Canonical JSON Profile and a Config JSON file.

\* Apply field selection logic to only output the fields requested in the config.





\* Apply mapping logic to rename canonical paths to new field names based on the config's "from" key.





\* Implement logic to toggle the `provenance` and `confidence` fields on or off based on the config settings.





\* Apply the requested missing value behavior: explicitly output `null`, completely omit the key, or throw an error if the value is missing.







\---



\### Phase 5: CLI Wrapping \& Testing



Evaluators explicitly stated that a minimal Command Line Interface (CLI) is completely sufficient and not to waste time polishing a UI.



\* Build a CLI using Python's `argparse` module that accepts file paths for the CSV, the Resume, and the Config file, and then prints or writes the final JSON.

\* Add a validation step right before outputting the JSON to ensure it matches the requested schema.





\* Write unit tests, prioritizing the edge cases you mentioned in your one-pager (e.g., testing the system's behavior when fed an empty CSV row).







\---



\### Phase 6: Deliverables \& Demo Video



Package everything for final submission.



\* Push all your working code to a public GitHub repository.





\* Write a clear README detailing the exact steps and commands required to run your CLI tool locally.





\* Include the generated JSON outputs from the sample inputs provided by Eightfold within the repository.





\* Record a roughly 2-minute screen recording.





\* In the video, run the pipeline end-to-end showing the default output and at least one custom-config output.





\* Spend the remaining time in the video briefly explaining one design decision you are proud of and one specific edge case you handled.







Since you are relying on local NLP and Regex instead of a generative API for the unstructured resumes, how do you plan to handle the extraction of complex, nested fields like "experience" (company, title, start, end, summary) from highly variable document layouts?

