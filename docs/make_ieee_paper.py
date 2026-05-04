import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.oxml.ns import qn

def create_ieee_paper(filename):
    doc = Document()

    # --- Title (1 Column) ---
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("Multi-Modal AI Content & Spam Detection System: A Unified Approach to Identifying Fake Images, Deepfake Videos, and Spam Text")
    title_run.bold = True
    title_run.font.size = Pt(16)
    
    # --- Authors (1 Column) ---
    authors = doc.add_paragraph()
    authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    authors_run = authors.add_run("Prof(Dr).Pankaj Gaigole, Shruti Shirude, Soham Shirole, Sidhhi Shirsath, Samarth Shingare")
    authors_run.font.size = Pt(12)
    
    # --- Affiliation (1 Column) ---
    affil = doc.add_paragraph()
    affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
    affil_run = affil.add_run("Department of Engineering, Sciences and Humanities (DESH)\nVishwakarma Institute of Technology, Pune, Maharashtra, India")
    affil_run.font.size = Pt(11)

    # --- Change to 2 Columns ---
    new_section = doc.add_section(WD_SECTION_START.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '708') # ~0.5 inch spacing between columns
    
    # Helper for adding section titles
    def add_section_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(11)

    # --- Abstract ---
    abstract = doc.add_paragraph()
    abstract.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abstract_bold = abstract.add_run("Abstract— ")
    abstract_bold.bold = True
    abstract_bold.italic = True
    abstract_text = abstract.add_run("The rapid evolution of generative Artificial Intelligence has democratized the creation of synthetic media, leading to a pervasive influx of deepfakes, manipulated images, and automated spam. As malicious actors exploit these technologies for misinformation and fraud, the need for robust verification tools is critical. However, existing detection mechanisms are largely fragmented—each tailored to a single modality—and often rely on computationally exhaustive deep learning architectures like Convolutional Neural Networks (CNNs). This paper presents a novel \"Multi-Modal AI Content and Spam Detection System\" that unifies text, image, and video analysis into a singular, highly efficient web platform. The proposed system utilizes a Term Frequency-Inverse Document Frequency (TF-IDF) and Multinomial Naïve Bayes pipeline for instantaneous spam classification, achieving an accuracy of 98.48%. For visual media, a heuristic-based Random Forest classifier extracts statistical properties—such as Laplacian variance, high-frequency energy, and colour entropy—to distinguish authentic images from AI-generated ones. Deepfake videos are processed through an optimized frame-by-frame extraction technique combined with a majority-voting mechanism to ensure high accuracy without requiring GPU acceleration. Deployed using a modern decoupled architecture comprising a Next.js frontend, a FastAPI asynchronous backend, and MongoDB Atlas for secure audit logging, this system demonstrates that lightweight, heuristic-based algorithms can provide a highly scalable, low-latency, and accessible solution against multi-modal digital deception.")
    abstract_text.italic = True
    abstract_text.font.size = Pt(10)

    # --- Section I ---
    add_section_title("I. INTRODUCTION")
    p = doc.add_paragraph("In recent years, the rapid advancement of artificial intelligence and machine learning has led to an unprecedented surge in synthetic media and automated text generation. While generative AI models offer tremendous creative benefits, they also present severe risks when weaponized to create deepfake videos, AI-generated deceptive images, and massive volumes of SMS or email spam. Such malicious content is actively utilized for political misinformation, financial fraud, and identity theft, fundamentally undermining public trust in digital media.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Current detection solutions primarily address these modalities in strict isolation. A user wishing to verify a suspicious news article, an unverified image, and a viral video must typically navigate across multiple independent platforms. Furthermore, many state-of-the-art synthetic media detectors rely heavily on complex Convolutional Neural Networks (CNNs) and transformer models that require expensive GPU infrastructure. This leads to slow processing times and restricted accessibility for everyday users.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("To overcome these limitations, this paper introduces a unified, multi-modal detection platform. By integrating optimized, modality-specific machine learning pipelines within a modern, asynchronous web architecture, the proposed system delivers fast and accurate content verification. It leverages lightweight statistical heuristics for visual media and proven NLP techniques for text, ensuring that the system remains accessible, resource-efficient, and highly scalable.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section II ---
    add_section_title("II. LITERATURE REVIEW")
    p = doc.add_paragraph("The detection of synthetic content and spam has been a highly active area of academic and industrial research. In the domain of text processing, traditional approaches such as Support Vector Machines (SVMs) and Naïve Bayes classifiers, combined with TF-IDF vectorization, have historically shown strong performance for spam detection. Recent literature has shifted towards transformer-based models like BERT; however, these models often introduce significant computational overhead for straightforward binary classification tasks.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("For visual media, the proliferation of Generative Adversarial Networks (GANs) and diffusion models has prompted the development of complex deep learning detectors. Researchers frequently employ heavy architectures like ResNet or EfficientNet to classify images as real or fake. While highly accurate, these models are notoriously resource-intensive. Alternatively, some studies have explored statistical artifact detection, analyzing frequency domains and noise patterns to detect synthetic origins with significantly less computational cost.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Despite significant advancements in these individual domains, there remains a notable gap in the literature regarding unified, multi-modal systems. The proposed system bridges this gap by merging text, image, and video analysis into a single application, utilizing heuristic approaches to maintain low latency without relying on expensive hardware accelerators.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section III ---
    add_section_title("III. PROBLEM STATEMENT")
    p = doc.add_paragraph("Digital platforms are currently inundated with manipulated media and automated spam, making it exceedingly difficult for the average user to verify the authenticity of digital content. Existing solutions are deeply fragmented, requiring users to switch between disparate tools for analyzing text, images, and videos. Furthermore, many of the current high-accuracy detection models are computationally expensive, requiring dedicated GPUs, which makes them impractical for widespread, low-latency public deployment. There is a critical need for a unified, highly efficient, and user-friendly system capable of detecting multiple forms of deceptive digital content in near real-time using accessible, low-cost hardware.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section IV ---
    add_section_title("IV. OBJECTIVES")
    p = doc.add_paragraph("1. To design and implement a unified platform capable of analyzing text, images, and video content for deception.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("2. To detect spam messages using a robust TF-IDF and Multinomial Naïve Bayes NLP pipeline.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("3. To classify images as authentic or AI-generated using computationally lightweight statistical heuristics and a Random Forest classifier.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("4. To detect video deepfakes through efficient frame extraction and a majority-voting aggregation mechanism.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("5. To ensure high-speed, asynchronous request processing using a FastAPI backend.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("6. To provide an intuitive, modern user interface utilizing Next.js and Tailwind CSS.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("7. To maintain persistent audit trails of all detection requests using a NoSQL MongoDB database.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section V ---
    add_section_title("V. PROPOSED SYSTEM")
    p = doc.add_paragraph("The proposed Multi-Modal AI Content Detection System is a sophisticated web-based application designed to instantly evaluate the authenticity of digital media. Unlike traditional single-purpose detectors, this system provides three distinct analysis modules accessible from a single, unified dashboard.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("The system leverages a decoupled architecture. The user interface captures inputs and transmits them via secure API endpoints. The central processing unit (a FastAPI server) asynchronously routes these inputs to the appropriate machine learning module. The text module relies on classical NLP techniques to quickly filter spam. The image and video modules utilize a CPU-friendly heuristic engine that analyzes image gradients, noise variance, and color entropy rather than relying on heavy deep neural networks.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section VI ---
    add_section_title("VI. SYSTEM ARCHITECTURE")
    p = doc.add_paragraph("The system architecture is strictly decoupled and structured into four primary layers:")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Client Tier: Built with Next.js and Tailwind CSS, this layer provides a responsive, dark-themed user interface. It handles file uploads, user authentication, and dynamic rendering of detection results.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("API Tier: Developed using FastAPI, this tier exposes asynchronous RESTful endpoints. It manages concurrent connections and ensures that long-running video analyses do not block the main event loop.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Processing Tier: This layer houses the core machine learning models. It contains the pre-trained NLP pipeline, the computer vision scripts for statistical feature extraction (NumPy, OpenCV), and the Random Forest classifier.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Data Tier: MongoDB Atlas serves as the remote NoSQL database. It securely stores encrypted user credentials (via JWT and bcrypt) and maintains an audit log of all system activity.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section VII ---
    add_section_title("VII. METHODOLOGY")
    p = doc.add_paragraph("Text Processing Methodology: Input text is sanitized by converting to lowercase and stripping punctuation. It is then transformed into numerical vectors using a TF-IDF vectorizer limited to 10,000 unigram and bigram features. These vectors are fed into a Multinomial Naïve Bayes classifier to produce a binary 'Spam' or 'Authentic' prediction.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Image Processing Methodology: Uploaded images are resized to 224x224 pixels. A custom feature extraction pipeline calculates 8 specific heuristics, including Laplacian variance (for blur/texture), gradient magnitude, high-frequency energy, and global noise standard deviation. These specific traits exploit the fact that AI-generated images often lack natural camera noise and possess artificially flat regions. A Random Forest model evaluates these 8 features to determine authenticity.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Video Processing Methodology: To bypass the immense computational load of analyzing standard 30fps video, the system uses OpenCV to extract exactly one frame per second. Each extracted frame is individually analyzed by the image module. A majority-voting algorithm is then applied: if over 50% of the sampled frames are classified as synthetic, the entire video is flagged as a deepfake.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section VIII ---
    add_section_title("VIII. BACKEND IMPLEMENTATION")
    p = doc.add_paragraph("The backend infrastructure is implemented using Python 3.11 and the FastAPI framework. Uvicorn acts as the ASGI server to manage asynchronous requests. Machine learning models were trained offline and serialized using the joblib library to enable instant loading into memory upon server startup.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Integration with the MongoDB database is achieved using the Motor asynchronous driver, ensuring that database I/O operations do not bottleneck the ML inference pipelines. The application logic securely manages user sessions through JSON Web Tokens (JWT). The entire backend is designed to be fully containerizable and operates comfortably within a constrained 512MB RAM environment.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section IX ---
    add_section_title("IX. FRONTEND IMPLEMENTATION")
    p = doc.add_paragraph("The client-facing software was implemented using the Next.js 15 App Router and React. Components are styled using Tailwind CSS, adhering to a modern aesthetic to convey a premium cybersecurity feel. Framer Motion is utilized to manage fluid transitions and state changes, such as loading spinners during asynchronous data fetching.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("The interface features dedicated drag-and-drop zones configured strictly for supported file formats. Client-side validation is implemented to prevent oversized payloads from reaching the server, enhancing overall system stability. The frontend communicates with the FastAPI backend through standardized fetch API calls.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section X ---
    add_section_title("X. RESULTS & DISCUSSION")
    p = doc.add_paragraph("The proposed system was subjected to rigorous testing across all three modalities. The text detection module, evaluated on a standard dataset of 5,572 SMS samples, achieved an accuracy of 98.48%, with a precision of 99.25%. Inference time for text classification averaged less than 100 milliseconds.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("For visual media, the heuristic-based Random Forest classifier successfully distinguished between authentic photographs and AI-generated images with high reliability. Crucially, the reliance on statistical features rather than deep CNNs reduced the memory footprint drastically, allowing the image inference to execute in under 2 seconds on a standard CPU.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("The video deepfake module effectively identified manipulated videos by sampling frames at 1 fps. This approach proved highly effective, confirming that temporal reduction via majority voting sacrifices negligible accuracy while providing exponential gains in processing speed.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section XI ---
    add_section_title("XI. CONCLUSION")
    p = doc.add_paragraph("In this paper, a Multi-Modal AI Content and Spam Detection System was successfully designed and implemented. By integrating text, image, and video analysis into a single unified platform, the project directly addresses the fragmented nature of modern digital forensics. The use of heuristic-based feature extraction for visual media, paired with classic NLP for text, allowed the system to bypass the heavy hardware constraints typically associated with deep learning models.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("Experimental results confirmed the system's high accuracy, rapid response times, and exceptional resource efficiency. Ultimately, this system provides a highly accessible, practical, and effective tool for combating the growing threat of synthetic media and digital spam.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- Section XII ---
    add_section_title("XII. ACKNOWLEDGEMENT")
    p = doc.add_paragraph("The authors would like to thank and appreciate the guidance given by the project guide during the course of development and testing of the project. We would like to thank the Department of Engineering, Sciences and Humanities (DESH) of Vishwakarma Institute of Technology for their resource and infrastructure support.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- References ---
    add_section_title("REFERENCES")
    p = doc.add_paragraph("[1] S. Shingare, et al., \"Multi-Modal AI Content Detection System Requirements,\" Internal Project Documentation, Vishwakarma Institute of Technology, 2026.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("[2] T. Almeida, J. Hidalgo, and A. Yamakami, \"Contributions to the Study of SMS Spam Filtering,\" Proceedings of the ACM Symposium on Applied Computing, 2011.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("[3] F. Marra, D. Gragnaniello, L. Verdoliva, and G. Poggi, \"Do GANs leave artificial fingerprints?\" IEEE Conference on Multimedia Information Processing and Retrieval (MIPR), 2019.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p = doc.add_paragraph("[4] S. Agarwal, H. Farid, Y. Gu, M. He, K. Nagano, and H. Li, \"Protecting World Leaders Against Deep Fakes,\" CVPR Workshops, 2019.")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Fix font sizes for the whole document body
    for p in doc.paragraphs:
        if not p.runs: continue
        # if not a title or heading, set to size 10
        if not p.runs[0].bold and p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
            for r in p.runs:
                r.font.size = Pt(10)

    doc.save(filename)
    print(f"Successfully saved {filename}")

if __name__ == '__main__':
    create_ieee_paper('Research_Paper_IEEE_Format.docx')
