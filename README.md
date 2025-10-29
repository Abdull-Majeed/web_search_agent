# Web Search Agent

## 📖 Project Description

The **Conversational Research Agent** is an intelligent AI-powered assistant designed to perform **real-time research** using **Google Gemini 2.5 Flash (Pro)** and **SerpAPI**.  
It can search the web, analyze multiple sources, summarize complex information, and provide **cited answers** with URLs — all through a natural **chat-based interface** built with **Streamlit**.

Unlike traditional chatbots, this agent doesn't rely only on its model knowledge — it actively queries the web using SerpAPI to stay **up-to-date** with the latest information (like breakthroughs in 2025, ongoing events, or new discoveries).  
It’s designed for **researchers, students, journalists, and developers** who need a smart, cited, and conversational way to explore real-world information.

---

## 🚀 Key Features

✅ Real-time web research using **SerpAPI**  
✅ Deep AI synthesis powered by **Gemini 2.5 Flash (Pro)**  
✅ Provides **citations and URLs** for all information  
✅ **Conversational Streamlit UI** with memory-like experience  
✅ Lightweight, modular, and fully open-source  
✅ Works both via **CLI** and **Web UI**

---

## 🧩 Project UI

<img width="1746" height="893" alt="image" src="https://github.com/user-attachments/assets/c9cc3c26-61d3-4711-8896-5023cc462524" />



## ⚙️ Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/web-research-agent.git
cd web-research-agent-main

pip install -r requirements.txt


Create a .env file in the project root:
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here


streamlit run search.py
