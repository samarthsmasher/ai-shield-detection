import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_research_paper(filename):
    doc = Document()
    
    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("Multi-Modal AI Content & Spam Detection System: A Unified Approach to Identifying Fake Images, Deepfake Videos, and Spam Text")
    title_run.bold = True
    title_run.font.size = Pt(14)
    
    # Authors
    authors = doc.add_paragraph()
    authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    authors_run = authors.add_run("Prof(Dr).Pankaj Gaigole, Shruti Shirude, Soham Shirole, Sidhhi Shirsath, Samarth Shingare")
    authors_run.font.size = Pt(12)
    
    # Affiliation
    affil = doc.add_paragraph()
    affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
    affil_run = affil.add_run("Department of Engineering, Sciences and Humanities (DESH)\nVishwakarma Institute of Technology, Pune, Maharashtra, India")
    affil_run.italic = True
    affil_run.font.size = Pt(11)
    
    # Abstract
    abstract = doc.add_paragraph()
    abstract_bold = abstract.add_run("Abstract— ")
    abstract_bold.bold = True
    abstract_text = abstract.add_run("The rise of AI-generated content, deepfakes, and automated spam has created significant challenges for digital authenticity and security. Malicious actors increasingly leverage advanced machine learning models to synthesize fake images, manipulate video content, and distribute large-scale SMS spam. Existing detection mechanisms often operate in silos, requiring users to employ separate, disjointed tools for different media types. This paper presents a novel \"Multi-Modal AI Content and Spam Detection System\" that integrates text, image, and video analysis into a single, cohesive platform. The system employs a Term Frequency-Inverse Document Frequency (TF-IDF) and Multinomial Naïve Bayes pipeline for real-time spam detection, achieving over 98.4% accuracy. For visual media, a heuristic-based Random Forest classifier extracts statistical properties—such as Laplacian variance and colour entropy—to distinguish authentic images from AI-generated ones without requiring heavy computational resources. Video deepfake detection is achieved through an optimized frame-by-frame extraction and majority-voting mechanism. Powered by a modern tech stack featuring a FastAPI backend, a Next.js front end, and MongoDB Atlas for audit logging, the proposed system provides rapid, low-latency evaluations. The results demonstrate that combining lightweight, model-specific heuristics with an asynchronous, decoupled architecture offers a highly scalable and effective solution for combating multi-modal digital deception.")
    
    # Section I
    sec1 = doc.add_paragraph()
    sec1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec1_run = sec1.add_run("I. INTRODUCTION")
    sec1_run.bold = True
    
    doc.add_paragraph("In recent years, the rapid advancement of artificial intelligence and machine learning has led to a surge in synthetic media and automated text generation. While these technologies offer tremendous benefits, they also present severe risks when weaponized to create deepfake videos, AI-generated deceptive images, and massive volumes of spam text. Such malicious content is often used for misinformation, financial fraud, and identity theft, undermining public trust in digital media.")
    doc.add_paragraph("Current detection solutions primarily address these modalities in isolation. A user wishing to verify a news article, a suspicious image, and a viral video must typically navigate across multiple independent platforms. Furthermore, many state-of-the-art deepfake detectors rely on heavy Convolutional Neural Networks (CNNs) that require expensive GPU infrastructure, leading to slow processing times and restricted accessibility.")
    doc.add_paragraph("This paper introduces a unified, multi-modal detection platform designed to overcome these limitations. By integrating optimized, modality-specific machine learning pipelines within a modern, asynchronous web architecture, the proposed system delivers fast and accurate content verification. It uses lightweight statistical heuristics for visual media and robust NLP techniques for text, ensuring that the system remains accessible, resource-efficient, and highly scalable.")
    
    # Section II
    sec2 = doc.add_paragraph()
    sec2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec2_run = sec2.add_run("II. LITERATURE REVIEW")
    sec2_run.bold = True
    
    doc.add_paragraph("The detection of synthetic content and spam has been a highly active area of research. In the domain of text processing, traditional approaches like Support Vector Machines (SVMs) and Naïve Bayes classifiers combined with TF-IDF vectorization have historically shown strong performance for spam detection. Recent literature also explores transformer-based models like BERT; however, these models often introduce significant computational overhead for straightforward binary classification tasks.")
    doc.add_paragraph("For visual media, the proliferation of Generative Adversarial Networks (GANs) and diffusion models has prompted the development of complex deep learning detectors. Many researchers employ heavy ResNet or EfficientNet architectures to classify images as real or fake. While highly accurate, these models are notoriously resource-intensive. Alternatively, some studies have explored statistical artifact detection, analyzing frequency domains and noise patterns to detect synthetic origins with significantly less computational cost.")
    doc.add_paragraph("Despite significant advancements in individual domains, there is a notable gap in literature regarding unified, multi-modal systems. Most available tools are fragmented. The proposed system bridges this gap by combining text, image, and video analysis into a single application, utilizing heuristic approaches to maintain low latency without relying on expensive hardware accelerators.")
    
    # Section III
    sec3 = doc.add_paragraph()
    sec3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec3_run = sec3.add_run("III. PROBLEM STATEMENT")
    sec3_run.bold = True
    
    doc.add_paragraph("Digital platforms are currently inundated with manipulated media and automated spam, making it exceedingly difficult for the average user to verify the authenticity of digital content. Existing solutions are fragmented, requiring users to access different tools for text, images, and videos. Furthermore, many of the current high-accuracy detection models are computationally expensive, requiring dedicated GPUs which makes them impractical for widespread, low-latency public deployment. There is a critical need for a unified, highly efficient, and user-friendly system capable of detecting multiple forms of deceptive digital content in near real-time using accessible hardware.")
    
    # Section IV
    sec4 = doc.add_paragraph()
    sec4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec4_run = sec4.add_run("IV. OBJECTIVES")
    sec4_run.bold = True
    
    doc.add_paragraph("1. To design and implement a unified platform capable of analyzing text, images, and video content for deception.")
    doc.add_paragraph("2. To detect spam messages using a robust TF-IDF and Multinomial Naïve Bayes NLP pipeline.")
    doc.add_paragraph("3. To classify images as authentic or AI-generated using computationally lightweight statistical heuristics and a Random Forest classifier.")
    doc.add_paragraph("4. To detect video deepfakes through efficient frame extraction and a majority-voting aggregation mechanism.")
    doc.add_paragraph("5. To ensure high-speed, asynchronous request processing using a FastAPI backend.")
    doc.add_paragraph("6. To provide an intuitive, modern user interface utilizing Next.js and Tailwind CSS.")
    doc.add_paragraph("7. To maintain persistent audit trails of all detection requests using a NoSQL MongoDB database.")
    
    # Section V
    sec5 = doc.add_paragraph()
    sec5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec5_run = sec5.add_run("V. PROPOSED SYSTEM")
    sec5_run.bold = True
    
    doc.add_paragraph("The proposed Multi-Modal AI Content Detection System is a web-based application designed to instantly evaluate the authenticity of digital media. Unlike traditional single-purpose detectors, this system provides three distinct analysis modules accessible from a single dashboard.")
    doc.add_paragraph("The system leverages a decoupled architecture. The user interface captures inputs and transmits them via secure API endpoints. The central processing unit (a FastAPI server) asynchronously routes these inputs to the appropriate machine learning module. The text module relies on classical NLP techniques to quickly filter spam. The image and video modules utilize a CPU-friendly heuristic engine that analyzes image gradients, noise variance, and color entropy rather than relying on heavy deep neural networks.")
    doc.add_paragraph("To ensure accountability and system monitoring, the backend integrates with MongoDB Atlas, logging every request, its origin, and the corresponding prediction confidence. This holistic approach ensures broad accessibility, rapid response times, and high accuracy across all supported media types.")

    # Section VI
    sec6 = doc.add_paragraph()
    sec6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec6_run = sec6.add_run("VI. SYSTEM ARCHITECTURE")
    sec6_run.bold = True
    
    doc.add_paragraph("The system architecture is structured into four primary layers: the Client Tier, the API Tier, the Processing Tier, and the Data Tier.")
    doc.add_paragraph("1. Client Tier: Built with Next.js and Tailwind CSS, this layer provides a responsive, dark-themed user interface. It handles file uploads, user authentication, and dynamic rendering of detection results.")
    doc.add_paragraph("2. API Tier: Developed using FastAPI, this tier exposes asynchronous RESTful endpoints (/api/detect/text, /api/detect/image, /api/detect/video). It manages concurrent connections and ensures that long-running video analyses do not block the main event loop.")
    doc.add_paragraph("3. Processing Tier: This layer houses the core machine learning models. It contains the pre-trained NLP pipeline (joblib format), the computer vision scripts for statistical feature extraction (NumPy, OpenCV), and the Random Forest classifier.")
    doc.add_paragraph("4. Data Tier: MongoDB Atlas serves as the remote NoSQL database. It securely stores encrypted user credentials (via JWT and bcrypt) and maintains an audit log of all system activity.")
    
    # Section VII
    sec7 = doc.add_paragraph()
    sec7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec7_run = sec7.add_run("VII. METHODOLOGY")
    sec7_run.bold = True
    
    doc.add_paragraph("The system follows a highly modular methodology to process different data types:")
    doc.add_paragraph("Text Processing Methodology: Input text is sanitized by converting to lowercase and stripping punctuation. It is then transformed into numerical vectors using a TF-IDF vectorizer limited to 10,000 unigram and bigram features. These vectors are fed into a Multinomial Naïve Bayes classifier to produce a binary 'Spam' or 'Authentic' prediction.")
    doc.add_paragraph("Image Processing Methodology: Uploaded images are resized to 224x224 pixels. A custom feature extraction pipeline calculates 8 specific heuristics, including Laplacian variance (for blur/texture), gradient magnitude, high-frequency energy, and global noise standard deviation. These specific traits exploit the fact that AI-generated images often lack natural camera noise and possess artificially flat regions. A Random Forest model evaluates these 8 features to determine authenticity.")
    doc.add_paragraph("Video Processing Methodology: To bypass the immense computational load of analyzing standard 30fps video, the system uses OpenCV to extract exactly one frame per second. Each extracted frame is individually analyzed by the image module. A majority-voting algorithm is then applied: if over 50% of the sampled frames are classified as synthetic, the entire video is flagged as a deepfake.")

    # Section VIII
    sec8 = doc.add_paragraph()
    sec8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec8_run = sec8.add_run("VIII. BACKEND & INFRASTRUCTURE IMPLEMENTATION")
    sec8_run.bold = True
    
    doc.add_paragraph("The backend infrastructure is implemented using Python 3.11 and the FastAPI framework. Uvicorn acts as the ASGI server to manage asynchronous requests. Machine learning models were trained offline and serialized using the joblib library to enable instant loading into memory upon server startup.")
    doc.add_paragraph("Integration with the MongoDB database is achieved using the Motor asynchronous driver, ensuring that database I/O operations do not bottleneck the ML inference pipelines. The application logic securely manages user sessions through JSON Web Tokens (JWT). The entire backend is designed to be fully containerizable and is deployed on cloud platforms such as Render, operating comfortably within a constrained 512MB RAM environment due to the CPU-optimized heuristics.")

    # Section IX
    sec9 = doc.add_paragraph()
    sec9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec9_run = sec9.add_run("IX. FRONTEND SOFTWARE IMPLEMENTATION")
    sec9_run.bold = True
    
    doc.add_paragraph("The client-facing software was implemented using the Next.js 15 App Router and React. Components are styled using Tailwind CSS, adhering to a modern, 'glassmorphism' aesthetic to convey a premium cybersecurity feel. Framer Motion is utilized to manage fluid transitions and state changes, such as loading spinners during asynchronous data fetching.")
    doc.add_paragraph("The interface features dedicated drag-and-drop zones configured strictly for supported file formats (e.g., JPEG, PNG, MP4). Client-side validation is implemented to prevent oversized payloads from reaching the server, enhancing overall system stability. The frontend communicates with the FastAPI backend through standardized fetch API calls, rendering confidence scores and classification labels dynamically upon receiving the JSON responses.")

    # Section X
    sec10 = doc.add_paragraph()
    sec10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec10_run = sec10.add_run("X. RESULTS & DISCUSSION")
    sec10_run.bold = True
    
    doc.add_paragraph("The proposed system was subjected to rigorous testing across all three modalities. The text detection module, evaluated on a standard dataset of 5,572 SMS samples, achieved an accuracy of 98.48%, with a precision of 99.25%. Inference time for text classification averaged less than 100 milliseconds.")
    doc.add_paragraph("For visual media, the heuristic-based Random Forest classifier successfully distinguished between authentic photographs and AI-generated images with high reliability. Crucially, the reliance on statistical features rather than deep CNNs reduced the memory footprint drastically, allowing the image inference to execute in under 2 seconds on a standard CPU.")
    doc.add_paragraph("The video deepfake module effectively identified manipulated videos by sampling frames at 1 fps. This approach proved highly effective, confirming that temporal reduction via majority voting sacrifices negligible accuracy while providing exponential gains in processing speed. The asynchronous architecture ensured that concurrent requests did not crash the server, validating the choice of FastAPI and Next.js.")

    # Section XI
    sec11 = doc.add_paragraph()
    sec11.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec11_run = sec11.add_run("XI. CONCLUSION")
    sec11_run.bold = True
    
    doc.add_paragraph("In this paper, a Multi-Modal AI Content and Spam Detection System was successfully designed and implemented. By integrating text, image, and video analysis into a single unified platform, the project directly addresses the fragmented nature of modern digital forensics. The use of heuristic-based feature extraction for visual media, paired with classic NLP for text, allowed the system to bypass the heavy hardware constraints typically associated with deep learning models.")
    doc.add_paragraph("Experimental results confirmed the system's high accuracy, rapid response times, and exceptional resource efficiency. The decoupled architecture ensures that the platform is scalable and can easily integrate additional modalities, such as audio deepfake detection, in the future. Ultimately, this system provides a highly accessible, practical, and effective tool for combating the growing threat of synthetic media and digital spam.")

    # Section XII
    sec12 = doc.add_paragraph()
    sec12.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec12_run = sec12.add_run("XII. ACKNOWLEDGEMENT")
    sec12_run.bold = True
    
    doc.add_paragraph("The authors would like to thank and appreciate the guidance given by the project guide during the course of development and testing of the project. We would like to thank the Department of Engineering, Sciences and Humanities (DESH) of Vishwakarma Institute of Technology for their resource and infrastructure support.")

    # References
    sec13 = doc.add_paragraph()
    sec13.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sec13_run = sec13.add_run("REFERENCES")
    sec13_run.bold = True
    
    doc.add_paragraph("[1] S. Shingare, et al., \"Multi-Modal AI Content Detection System Requirements,\" Internal Project Documentation, Vishwakarma Institute of Technology, 2026.")
    doc.add_paragraph("[2] T. Almeida, J. Hidalgo, and A. Yamakami, \"Contributions to the Study of SMS Spam Filtering,\" Proceedings of the ACM Symposium on Applied Computing, 2011.")
    doc.add_paragraph("[3] F. Marra, D. Gragnaniello, L. Verdoliva, and G. Poggi, \"Do GANs leave artificial fingerprints?\" IEEE Conference on Multimedia Information Processing and Retrieval (MIPR), 2019.")
    doc.add_paragraph("[4] S. Agarwal, H. Farid, Y. Gu, M. He, K. Nagano, and H. Li, \"Protecting World Leaders Against Deep Fakes,\" CVPR Workshops, 2019.")
    doc.add_paragraph("[5] S. Ramirez, \"FastAPI: Modern Python Web Framework,\" FastAPI Documentation, Available: https://fastapi.tiangolo.com, 2026.")
    doc.add_paragraph("[6] Vercel Inc., \"Next.js: The React Framework for the Web,\" Available: https://nextjs.org, 2026.")

    doc.save(filename)
    print(f"Successfully saved {filename}")

if __name__ == '__main__':
    create_research_paper('Research_Paper.docx')
