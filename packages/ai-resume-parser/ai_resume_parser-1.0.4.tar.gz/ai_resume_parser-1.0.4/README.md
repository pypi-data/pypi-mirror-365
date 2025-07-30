# ResumeParser Pro 🚀

[![PyPI version](https://badge.fury.io/py/ai-resume-parser.svg)](https://badge.fury.io/py/resumeparser-pro)
[![Python Support](https://img.shields.io/pypi/pyversions/ai-resume-parser.svg)](https://pypi.org/project/resumeparser-pro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready AI-powered resume parser with parallel processing capabilities. Extract structured data from resumes in PDF, DOCX, TXT, images, and more, using state-of-the-art language models.

## 🌟 Features

- **🤖 AI-Powered**: Uses advanced language models (GPT, Gemini, Claude, etc.).
- **⚡ Parallel Processing**: Process multiple resumes simultaneously.
- **📊 Structured Output**: Returns clean, validated JSON data.
- **🎯 High Accuracy**: Extracts 20+ fields with intelligent categorization.
- **📁 Multi-Format Support**: Parses PDFs, DOCX, TXT, images (PNG, JPG), HTML, and ODT files.
- **🔌 Easy Integration**: Simple API with just a few lines of code.

## 🚀 Quick Start

### Installation
Core installation (for PDF, DOCX, TXT)
pip install ai-resume-parser

To include support for all file types
pip install ai-resume-parser[full]

See the "Supported File Formats" section for installing specific file handlers.

### Basic Usage
from resumeparser_pro import ResumeParserPro

Initialize parser
parser = ResumeParserPro(
provider="google_genai",
model_name="gemini-2.0-flash",
api_key="your-api-key"
)

Parse single resume (supports .pdf, .docx, .png, etc.)
result = parser.parse_resume("path/to/your/resume.pdf")

if result.success:
print(f"Name: {result.resume_data.contact_info.full_name}")
print(f"Experience: {result.resume_data.total_experience_months} months")

## 📁 Supported File Formats

ResumeParser Pro supports a wide range of file formats. Core dependencies handle PDF, DOCX, and TXT. For other formats, install the optional extras.

| Format          | Extensions               | Required Installation Command          |
|-----------------|--------------------------|----------------------------------------|
| **Core Formats**| `.pdf`, `.docx`, `.txt`  | `pip install ai-resume-parser`         |
| **Images (OCR)**| `.png`, `.jpg`, `.jpeg`  | `pip install ai-resume-parser[ocr]`    |
| **HTML**        | `.html`, `.htm`          | `pip install ai-resume-parser[html]`   |
| **OpenDocument**| `.odt`                   | `pip install ai-resume-parser[odt]`    |

**❗️ Important Note for Image Parsing:**
To parse images, you must have the **Google Tesseract OCR engine** installed on your system. This is a separate step from the `pip` installation.
*   [Tesseract Installation Guide](https://github.com/tesseract-ocr/tesseract/wiki)

## 🎯 Supported AI Providers

Since `ai-resume-parser` uses LangChain's `init_chat_model`, it supports **all LangChain-compatible providers**:

| Provider      | Example Models                            | Setup                  |
|---------------|-------------------------------------------|------------------------|
| **Google**    | Gemini 2.0 Flash, Gemini Pro, Gemini 1.5  | `provider="google_genai"`|
| **OpenAI**    | GPT-4o, GPT-4o-mini, GPT-4 Turbo        | `provider="openai"`      |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus        | `provider="anthropic"`   |

... (and others like Azure, Bedrock, Ollama, etc.)

**Full list**: See [LangChain Model Providers](https://python.langchain.com/docs/integrations/chat/) for complete provider support.


## 📈 Performance

- **Speed**: ~3-5 seconds per resume (depending on the LLM).
- **Parallel Processing**: 5-10x faster for batch operations.
- **Accuracy**: 95%+ field extraction accuracy.

## 🛠️ Advanced Features

### Custom Configuration
parser = ResumeParserPro(
provider="openai",
model_name="gpt-4o-mini",
api_key="your-api-key",
max_workers=10, # Parallel processing workers
temperature=0.1 # Model consistency
)


## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see LICENSE file for details.
