#!/usr/bin/env python3
"""
Create sample exam PDFs for testing Professor Profiler.

This script generates synthetic exam questions in PDF format and places them
in the input/ folder, so you can test the system without needing real exam papers.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from pathlib import Path

# Import path utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from profiler_agent.paths import get_input_path, ensure_directories


SAMPLE_EXAMS = {
    "physics_2024_midterm.pdf": {
        "title": "Physics 101 - Midterm Examination 2024",
        "questions": [
            ("1. Define Newton's first law of motion and provide an example.", "Remember"),
            ("2. A 5kg object accelerates at 2m/s². Calculate the net force acting on it.", "Apply"),
            ("3. Compare and contrast potential energy and kinetic energy.", "Understand"),
            ("4. Analyze the motion of a pendulum and explain energy transformations.", "Analyze"),
            ("5. Design an experiment to measure the acceleration due to gravity.", "Create"),
            ("6. A car moves at constant velocity. What can you infer about the forces?", "Understand"),
            ("7. Evaluate the efficiency of different types of engines.", "Evaluate"),
            ("8. State the formula for gravitational force.", "Remember"),
            ("9. Apply conservation of momentum to a collision between two objects.", "Apply"),
            ("10. Explain why astronauts feel weightless in orbit.", "Understand"),
        ]
    },
    "physics_2023_final.pdf": {
        "title": "Physics 101 - Final Examination 2023",
        "questions": [
            ("1. List the three laws of thermodynamics.", "Remember"),
            ("2. Calculate the work done by a force of 10N moving an object 5m.", "Apply"),
            ("3. Explain the relationship between temperature and kinetic energy.", "Understand"),
            ("4. Analyze heat transfer in a closed system.", "Analyze"),
            ("5. Evaluate the environmental impact of different energy sources.", "Evaluate"),
            ("6. Design a solar heating system for a house.", "Create"),
            ("7. Define entropy in your own words.", "Understand"),
            ("8. What is the first law of thermodynamics?", "Remember"),
            ("9. Apply the ideal gas law to calculate pressure at different temperatures.", "Apply"),
            ("10. Compare conduction, convection, and radiation.", "Understand"),
        ]
    },
    "chemistry_2024_q1.pdf": {
        "title": "Chemistry 201 - First Quarter Exam 2024",
        "questions": [
            ("1. Write the electron configuration for oxygen.", "Remember"),
            ("2. Balance this equation: H₂ + O₂ → H₂O", "Apply"),
            ("3. Explain why noble gases are chemically inert.", "Understand"),
            ("4. Analyze the bonding in a water molecule.", "Analyze"),
            ("5. Evaluate the safety of different laboratory procedures.", "Evaluate"),
            ("6. Design a procedure to synthesize aspirin.", "Create"),
            ("7. Define electronegativity.", "Remember"),
            ("8. Calculate the molar mass of glucose (C₆H₁₂O₆).", "Apply"),
            ("9. Compare ionic and covalent bonding.", "Understand"),
            ("10. Analyze the pH of different household substances.", "Analyze"),
        ]
    },
}


def create_sample_pdf(filename: str, exam_data: dict):
    """Create a sample exam PDF with the given questions."""
    filepath = str(get_input_path(filename))  # Convert Path to string
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='navy',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=12,
        leftIndent=20
    )
    
    # Add title
    title = Paragraph(exam_data["title"], title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add instructions
    instructions = Paragraph(
        "<b>Instructions:</b> Answer all questions. Show all work for calculation problems. "
        "Total time: 90 minutes. Good luck!",
        styles['Normal']
    )
    elements.append(instructions)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add questions
    for question_text, bloom_level in exam_data["questions"]:
        question = Paragraph(question_text, question_style)
        elements.append(question)
        elements.append(Spacer(1, 0.15*inch))
    
    # Add footer
    elements.append(Spacer(1, 0.5*inch))
    footer = Paragraph(
        f"<i>This is a sample exam generated for testing purposes. "
        f"Bloom's levels included for demonstration.</i>",
        styles['Italic']
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    print(f"✓ Created {filename}")


def main():
    """Generate all sample exam PDFs."""
    print("Generating sample exam PDFs...\n")
    
    # Ensure input directory exists
    ensure_directories()
    
    # Check if reportlab is available
    try:
        import reportlab
    except ImportError:
        print("ERROR: reportlab is required to generate sample PDFs")
        print("Install it with: pip install reportlab")
        return 1
    
    # Generate each exam
    for filename, exam_data in SAMPLE_EXAMS.items():
        try:
            create_sample_pdf(filename, exam_data)
        except Exception as e:
            print(f"✗ Failed to create {filename}: {e}")
    
    print(f"\n✓ Successfully generated {len(SAMPLE_EXAMS)} sample exam PDFs")
    print(f"✓ Files saved to: {get_input_path('')}")
    print("\nYou can now run: python demo.py")
    return 0


if __name__ == "__main__":
    exit(main())
