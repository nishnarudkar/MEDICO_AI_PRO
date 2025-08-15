# MedicoAI Pro 🩺🤖

**An advanced, AI-powered platform for medical and health data analysis. Ask questions in plain English, get intelligent insights, and visualize your data interactively.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medicoaipro.streamlit.app/)

---

## 🚀 Live Demo

You can access a live version of the application here:
**[https://medicoaipro.streamlit.app/](https://medicoaipro.streamlit.app/)**

---

## 🌟 Key Features

MedicoAI Pro is designed to make complex health data analysis accessible and intuitive.

-   **🤖 AI-Powered Chat**: Use natural language to query your datasets. The app leverages Google's Gemini Pro to understand your questions and generate SQL queries on the fly.
-   **📊 Interactive Visualizations**: Automatically generate a wide range of charts and graphs, from basic histograms and bar charts to advanced correlation heatmaps and 3D scatter plots.
-   **📈 Advanced Analytics Suite**: Go beyond basic charts with a built-in analytics dashboard that provides:
    -   Detailed statistical summaries.
    -   K-Means clustering to identify patient groups.
    -   Trend analysis over time.
    -   Outlier detection using IQR and Z-Score methods.
-   **📂 Multi-File Upload**: Supports CSV, Excel (`.xlsx`), and JSON files. Upload multiple datasets and analyze them in one session.
-   **🔒 Secure & Private**: Your data is processed locally. The app uses a local SQLite database to store your data for the session, ensuring privacy.
-   **⚡ High-Performance Caching**: Streamlit's advanced caching is implemented to ensure a smooth and fast user experience, preventing slow re-runs of data processing and model initializations.

---

## 🛠️ Tech Stack

-   **Backend**: Python
-   **Web Framework**: Streamlit
-   **AI/LLM**: Google Gemini Pro
-   **Data Handling**: Pandas, NumPy, Scikit-learn
-   **Database**: SQLite
-   **Plotting**: Plotly Express, Matplotlib, Seaborn

---

## 🚀 Getting Started

Follow these instructions to set up and run MedicoAI Pro on your local machine.

### Prerequisites

-   Python 3.8+
-   A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/MedicoAI-Pro.git](https://github.com/your-username/MedicoAI-Pro.git)
    cd MedicoAI-Pro
    ```

2.  **Create a Virtual Environment**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    All the required packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a file named `.env` in the root directory of the project and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    Replace `"YOUR_GEMINI_API_KEY"` with your actual key.

5.  **Run the Application**
    You're all set! Run the following command to start the Streamlit server.
    ```bash
    streamlit run app.py
    ```
    The application should now be open in your web browser.

---

## 📖 How to Use

1.  **Upload Data**: Drag and drop one or more of your health data files (CSV, XLSX, JSON) into the uploader in the sidebar.
2.  **Explore the Tabs**:
    -   **AI Chat**: Ask questions about your data like, "What is the average age of patients?" or "Show me the distribution of blood pressure."
    -   **Visualizations**: Select a dataset and create custom charts to explore relationships in your data.
    -   **Analytics**: Dive deeper with statistical analysis, clustering, and trend identification.
3.  **Interact**: Use the "Suggest Questions" button for ideas or the "Quick Actions" in the sidebar to get instant insights.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
