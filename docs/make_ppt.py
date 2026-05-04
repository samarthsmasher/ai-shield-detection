import collections 
import collections.abc
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def add_footer(slide):
    # Add light blue rectangle at the bottom
    left = Inches(1)
    top = Inches(6.5)
    width = Inches(8)
    height = Inches(0.4)
    shape = slide.shapes.add_shape(
        1, left, top, width, height # 1 is msoShapeRectangle
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0, 176, 240) # Light blue
    shape.line.color.rgb = RGBColor(0, 176, 240)
    
    text_frame = shape.text_frame
    p = text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "DEPARTMENT OF ENGINEERING SCIENCES AND HUMANITIES, VIT, Pune."
    run.font.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 0, 0)

def add_logo(slide):
    # Add a mock VI logo
    left = Inches(0.2)
    top = Inches(0.2)
    width = Inches(1.5)
    height = Inches(0.8)
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "VI Logo"
    run.font.bold = True
    run.font.italic = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0, 112, 192)

def add_title(slide, text):
    left = Inches(2)
    top = Inches(0.5)
    width = Inches(6)
    height = Inches(1)
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.bold = True
    run.font.size = Pt(36)
    run.font.color.rgb = RGBColor(0, 0, 0)

def add_bullets(slide, bullets):
    left = Inches(1)
    top = Inches(1.8)
    width = Inches(8)
    height = Inches(4.5)
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    
    for i, text in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        run = p.add_run()
        run.text = "\u2713 " + text
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0, 0, 0)
        p.space_after = Pt(14)

def create_ppt(filename):
    prs = Presentation()
    blank_slide_layout = prs.slide_layouts[6]
    
    # ------------------ SLIDE 1: TITLE SLIDE ------------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    
    # Top text
    txBox = slide1.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "ASE PROJECT – PPT FOR END SEMESTER ASSESSMENT – MAY 2026"
    run.font.bold = True
    run.font.size = Pt(14)

    # Boxed Title
    shape = slide1.shapes.add_shape(1, Inches(0.8), Inches(1.2), Inches(8.4), Inches(0.8))
    shape.fill.background() # transparent
    shape.line.color.rgb = RGBColor(0, 0, 0)
    p = shape.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "TITLE :- Multi-Modal AI Content & Spam Detection System"
    run.font.bold = True
    run.font.size = Pt(24)
    run.font.color.rgb = RGBColor(0, 0, 0)

    # Info row
    txBox = slide1.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(8.4), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "Div:- CSAI-F          ASEP_GROUP No :- 1          Day:- Friday          Date:- 03/05/2026"
    run.font.bold = True
    run.font.size = Pt(14)

    # Presented by
    txBox = slide1.shapes.add_textbox(Inches(1.5), Inches(3.2), Inches(3), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Presented by"
    run.font.bold = True

    shape = slide1.shapes.add_shape(1, Inches(1), Inches(3.7), Inches(4), Inches(1.2))
    shape.fill.background()
    shape.line.color.rgb = RGBColor(0, 0, 0)
    p = shape.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "1) Shruti Shirude\n2) Soham Shirole\n3) Sidhhi Shirsath\n4) Samarth Shingare"
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 0, 0)

    # Project Guide
    txBox = slide1.shapes.add_textbox(Inches(6), Inches(3.2), Inches(3), Inches(0.5))
    p = txBox.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Project Guide"
    run.font.bold = True

    shape = slide1.shapes.add_shape(1, Inches(5.5), Inches(3.7), Inches(4), Inches(0.4))
    shape.fill.background()
    shape.line.color.rgb = RGBColor(0, 0, 0)
    p = shape.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "Prof(Dr).Pankaj Gaigole"
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 0, 0)

    # Bottom Text
    txBox = slide1.shapes.add_textbox(Inches(1), Inches(5.8), Inches(8), Inches(1))
    p = txBox.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "DEPARTMENT OF ENGINEERING SCIENCES AND HUMANITIES (DESH)\nVISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE"
    run.font.bold = True
    run.font.size = Pt(14)

    # ------------------ CONTENT SLIDES ------------------

    # 2. Intro
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Introduction")
    add_bullets(slide, [
        "The spread of misinformation is increasing rapidly due to unchecked AI generation.",
        "Deepfakes, AI-generated images, and text spam are major causes of digital deception.",
        "Conventional verification depends completely on users and often fails in real situations.",
        "Recent advancements in machine learning enable real-time monitoring of content authenticity.",
        "The proposed system uses heuristic ML models, FastAPI, and Next.js to enhance digital safety."
    ])
    add_footer(slide)

    # 3. Objectives
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Objectives")
    add_bullets(slide, [
        "To detect spam messages using an NLP-based TF-IDF and Naïve Bayes pipeline.",
        "To ensure visual media authenticity by extracting heuristic properties of images.",
        "To detect deepfake videos in real-time using frame extraction and majority voting.",
        "To log user requests and detection history securely using MongoDB Atlas.",
        "To provide an asynchronous, multi-modal web interface using Next.js and FastAPI."
    ])
    add_footer(slide)

    # 4. Components / Technologies
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Technologies Used")
    add_bullets(slide, [
        "Frontend: Next.js 15, Tailwind CSS, Framer Motion",
        "Backend: FastAPI, Uvicorn, Python 3.11",
        "Database: MongoDB Atlas, Motor (Async)",
        "Machine Learning: scikit-learn, OpenCV, NumPy, Pillow, joblib",
        "Security & Auth: JWT Authentication, bcrypt"
    ])
    add_footer(slide)

    # 5. Methodology 1
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Methodology\n1. Text Spam Detection")
    add_bullets(slide, [
        "The user inputs text which is sanitized and preprocessed.",
        "A TF-IDF vectorizer converts the text into numerical vectors (unigrams and bigrams).",
        "The Naïve Bayes model predicts whether the text is 'Spam' or 'Authentic'.",
        "If spam is detected, the frontend triggers a red warning alert instantly."
    ])
    add_footer(slide)

    # 6. Methodology 2
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Methodology\n2. Image Authenticity Detection")
    add_bullets(slide, [
        "The uploaded image is resized to 224x224 pixels and converted to a NumPy array.",
        "Statistical features like Laplacian variance and colour entropy are extracted.",
        "A Random Forest classifier evaluates these features without heavy GPU usage.",
        "The system instantly flags AI-generated images lacking natural noise."
    ])
    add_footer(slide)

    # 7. Methodology 3
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Methodology\n3. Video Deepfake Detection")
    add_bullets(slide, [
        "The system receives an MP4 video file for analysis.",
        "OpenCV extracts exactly one frame per second to optimize performance.",
        "Each frame is passed to the Image Module for independent prediction.",
        "If over 50% of the frames are synthetic, the video is flagged as a deepfake."
    ])
    add_footer(slide)

    # 8. Methodology 4
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Methodology\n4. Asynchronous Integration")
    add_bullets(slide, [
        "FastAPI receives concurrent requests without blocking the event loop.",
        "The detection results and timestamps are securely logged into MongoDB.",
        "The Next.js frontend fetches the JSON response and displays confidence scores.",
        "JWT tokens ensure that only authenticated users can access the system history."
    ])
    add_footer(slide)

    # 9. Results
    slide = prs.slides.add_slide(blank_slide_layout)
    add_logo(slide)
    add_title(slide, "Result And Discussions")
    add_bullets(slide, [
        "The text spam model successfully detected spam with 98.48% accuracy.",
        "The heuristic image module accurately identified synthetic images in under 2 seconds on a CPU.",
        "The video deepfake module efficiently detected manipulated frames using 1 fps sampling.",
        "The integrated MongoDB database successfully logged all activities in real-time.",
        "Overall system testing demonstrated stable operation, quick response time, and effective multi-modal coordination."
    ])
    add_footer(slide)

    prs.save(filename)
    print(f"Successfully saved {filename}")

if __name__ == '__main__':
    create_ppt('Project_Presentation.pptx')
