# Input Folder

Place your exam/question paper PDF files here for analysis.

## Usage

1. Copy your exam PDFs into this folder:
   ```bash
   cp your_exam.pdf input/
   ```

2. Run the analysis:
   ```bash
   python demo.py
   ```
   
   Or use the filename directly in your queries:
   ```python
   query = "Analyze physics_2024.pdf and identify key topics"
   ```

3. Results will be saved to the `output/` folder

## Supported Formats

- **PDF files** (.pdf) - Primary format for exam papers
- Files can be named anything (e.g., `physics_2024.pdf`, `midterm_exam.pdf`)

## Tips

- Use descriptive filenames for easy reference
- You can analyze multiple exams at once
- The system will automatically find PDFs in this folder

## Examples

```
input/
├── physics_2024_midterm.pdf
├── physics_2023_final.pdf
├── chemistry_2024_q1.pdf
└── math_201_exam.pdf
```
