from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)

def add_bullet(doc, text, bold_text=""):
    p = doc.add_paragraph(style='List Bullet')
    if bold_text:
        p.add_run(bold_text).bold = True
        p.add_run(text)
    else:
        p.add_run(text)

doc = Document()

# Title
title = doc.add_heading('AI Shield: Detailed Presentation Guide', 0)
title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

doc.add_paragraph("This document provides a highly detailed, step-by-step technical explanation of the AI Shield project for your professor.\n")

# Section 1
add_heading(doc, '1. Introduction & Motivation')
doc.add_paragraph("Goal: Establish the real-world problem and introduce your project as a comprehensive solution.")
add_bullet(doc, " The internet is increasingly flooded with AI-generated content—fake images, deepfake videos, and automated text spam.", bold_text="The Problem:")
add_bullet(doc, " I developed AI Shield, a Multi-Modal Detection System capable of analyzing Text, Images, and Videos in real-time to determine if the content is authentic or artificially generated.", bold_text="The Solution:")

# Section 2
add_heading(doc, '2. High-Level Architecture (The Tech Stack)')
doc.add_paragraph("Goal: Demonstrate your full-stack engineering capabilities and choice of modern tools.")
add_bullet(doc, " Built using Next.js 15 (App Router), TypeScript, and Tailwind CSS. It features a premium 'dark mode' glassmorphism UI with Framer Motion animations for a highly responsive user experience.", bold_text="Frontend:")
add_bullet(doc, " Developed using FastAPI (Python 3.11). It is extremely fast, asynchronous, and handles file uploads, ML model inference, and request logging.", bold_text="Backend API:")
add_bullet(doc, " Used for the persistent storage of user credentials, detection logs, and system audit trails using the async Motor driver.", bold_text="Database (MongoDB Atlas):")

# Section 3
add_heading(doc, '3. The Machine Learning Pipeline (The Core Logic)')
doc.add_paragraph("Goal: Explain the mathematical and statistical foundation of how the system actually detects AI fakes. This is the most important part for your professor.")

add_heading(doc, '3.1 Text Spam Detection', level=2)
add_bullet(doc, " We use a Term Frequency-Inverse Document Frequency (TF-IDF) vectorizer. It converts text into numerical data by evaluating how important a word is to a message relative to the entire dataset.", bold_text="Vectorization:")
add_bullet(doc, " The data is passed into a Multinomial Naïve Bayes classifier. This model relies on Bayes' theorem to calculate the probability that a message is spam based on its vocabulary.", bold_text="Classification:")
add_bullet(doc, " Trained on over 5,500 real SMS messages, the model achieves a 98.5% accuracy rate, successfully catching patterns like excessive capitalization and typical spam keywords.", bold_text="Performance:")

add_heading(doc, '3.2 Image Authenticity Detection', level=2)
doc.add_paragraph("Unlike basic neural networks, this model relies on 8 statistically engineered features extracted using OpenCV and NumPy to differentiate natural camera photos from AI-generated ones:")
add_bullet(doc, " Real photos have natural camera noise. AI images often have an unnaturally low noise floor or perfectly smooth patches.", bold_text="Global Noise Estimate & Patch Variance:")
add_bullet(doc, " Real photos have rich edge textures. AI models often blur fine details or create artificial checkerboard patterns.", bold_text="Laplacian Variance & High-Frequency Energy:")
add_bullet(doc, " Real photos contain thousands of unique colors. AI images sometimes exhibit 'color quantization' or flat colored regions.", bold_text="Color Histogram Entropy & Diversity:")
add_bullet(doc, " These 8 mathematical features are extracted from the image and fed into a Random Forest Classifier to make the final 'Real' or 'Fake' prediction.", bold_text="The Decision Model:")

add_heading(doc, '3.3 Video Deepfake Detection', level=2)
add_bullet(doc, " The system uses OpenCV to split the uploaded video into individual frames.", bold_text="Frame Extraction:")
add_bullet(doc, " Each frame is passed through the Image Authenticity logic mentioned above.", bold_text="Analysis:")
add_bullet(doc, " The system takes a majority vote across all analyzed frames to confidently determine if the video as a whole is deepfaked.", bold_text="Aggregation:")

# Section 4
add_heading(doc, '4. Backend Engineering & Security')
doc.add_paragraph("Goal: Highlight the robust software engineering practices implemented in the API.")
add_bullet(doc, " Users must register and log in. Passwords are cryptographically hashed using bcrypt, and stateless JWT (JSON Web Tokens) are used for secure session management.", bold_text="Authentication:")
add_bullet(doc, " I wrote a custom FastAPI middleware that intercepts every incoming request. It measures the processing time in milliseconds and asynchronously saves a SystemLog document to MongoDB. This ensures we have a complete audit trail without slowing down the user response.", bold_text="Performance Logging Middleware:")

# Section 5
add_heading(doc, '5. Step-by-Step Live Demo Instructions')
doc.add_paragraph("When you demo the project to your professor, follow these exact steps:")
p1 = doc.add_paragraph("1. ", style='List Number')
p1.add_run("Show the Live Dashboard: ").bold = True
p1.add_run("Start on the home page. Point out the 'Detection History' dashboard. Explain that it pulls live statistics (Total Scans, Safe Rate, Threats Found) directly from the MongoDB backend.")

p2 = doc.add_paragraph("2. ", style='List Number')
p2.add_run("Demonstrate Text Detection: ").bold = True
p2.add_run("Navigate to the Text tab. Paste a realistic spam message (e.g., 'URGENT! Click the link to claim your $1000 prize'). Show how quickly the system flags it as SPAM.")

p3 = doc.add_paragraph("3. ", style='List Number')
p3.add_run("Demonstrate Image Detection: ").bold = True
p3.add_run("Navigate to the Image tab. First, upload a normal photograph (it should show SAFE). Then, upload an AI-generated image or artwork. The system will flag it as FAKE based on the mathematical heuristics.")

p4 = doc.add_paragraph("4. ", style='List Number')
p4.add_run("Conclude with the Audit Trail: ").bold = True
p4.add_run("Go back to the Live Dashboard. Show the professor how the statistics and the recent scans have instantly updated to reflect the tests you just ran. This proves the full-stack system is fully integrated in real-time.")

# Section 6
add_heading(doc, '6. Expected Q&A')
add_bullet(doc, " Using mathematical heuristics (Laplacian variance, noise estimation) is computationally much faster and requires vastly less memory than running a massive Deep Learning model like ResNet-50. It allows the system to run highly efficiently on a free-tier server while still catching common AI artifacts.", bold_text="Why didn't you use a massive neural network for images? ")
add_bullet(doc, " The backend runs on Render and the frontend on Vercel. I specifically engineered the frontend to ping a '/api/health' endpoint with retries to gracefully handle server cold-starts on Render's free tier.", bold_text="How is it deployed? ")

# Save the document
doc.save('AI_Shield_Presentation.docx')
print("Document generated successfully at AI_Shield_Presentation.docx")
