# USD-MS-AAI
# Module 2 – Supervised Learning

This folder contains project code for **Module 2** of the M.S. in Applied Artificial Intelligence (AAI) course **AAI500**.

## 📂 Contents
- **Data/** – Hosts the dataset
- **Modelling/** – Hosts all the Jupyter notebooks
- **Visualizations/** – Contains output plots and figures

## 📊 Data
- Data reference: [Kaggle – Symptom-Based Disease Labeling Dataset](https://www.kaggle.com/datasets/krish0202/symptom-based-disease-labeling-dataset/data)

---

# AAI500 - Symptom-Based Disease Classification

## Project Details
This project is part of the final term submission for the **AAI500** course.  
It focuses on building machine learning models for symptom-based disease classification using various approaches including:

- **LSTM/GRU Neural Networks**
- **BERT (Transformer-based)**
- **TF-IDF (Traditional ML)**

## 👤 Team Details
**Team – AAI500 (Final Project)**  
- **Ved Prakash Dwivedi**
- **Bharath TS**
- **Manu Malla**

> **Note:** This assignment has [Turnitin](https://guides.turnitin.com/hc/en-us/articles/24008452116749-Welcome-to-Turnitin-Guides) enabled for plagiarism check. Use the Draft Coach extension in Google Docs to review before submission.

---

## 📂 Project Structure
```
Module 2/
├── Data/
│   └── symptom-dataset.csv
├── Modelling/
│   ├── Improved_Symptom_Classifier_LSTM_GRU.ipynb
│   ├── Multiclass_Symptom_Classifier_Using_BERT.ipynb
│   ├── Multiclass_Symptom_Classifier_Using_LSTM_GRU.ipynb
│   └── Multiclass_Symptom_Classifier_Using_TFIDF.ipynb
└── Visualizations/
    └── model-performance-plots.png
```

---

## 📅 Project Timeline
**Module 2 (Week 2)** – Project initialization and setup  
**Module 4 (Week 4)** – Dataset selection and initial analysis  
**Module 7 (Week 7)** – Final deliverables submission

---

## 📦 Deliverables
### 1. Final Technical Report
- Format: PDF
- Filename: `Final-Project-Report-Symptom-Classification.pdf`
- Sections:
  - Introduction
  - Data Cleaning / Preparation
  - Exploratory Data Analysis (EDA)
  - Model Selection and Implementation
  - Model Analysis and Comparison
  - Conclusion and Recommendations
  - Appendix with notebook output

### 2. Team Presentation
- 8–10 minutes, MP4 format
- Filename: `Final-Project-Presentation-Symptom-Classification.mp4`
- Clear and concise for non-technical audience
- Equal participation from all members

---

## 📏 Evaluation Criteria (235 Points)
| Component | Weight | Points | Description |
|-----------|--------|--------|-------------|
| Project selection and setup, including dataset, objectives, and approach | 15% | 35.25 pts | Clearly stated objectives, feasible approach, available dataset, properly scoped. |
| AI and Machine Learning algorithm descriptions, theory, and source code | 25% | 58.75 pts | Clear algorithms description, explicit discussion of the theory with proper mathematical/logical composition, with well-documented source code. |
| Execution and output, implementing proper AI and Machine Learning algorithms | 25% | 58.75 pts | Program code executes on sample data; produced a complete dataset from multiple runs over the dataset. |
| Analyzing the AI and Machine Learning methods and providing results and conclusions | 20% | 47 pts | Well-presented results, accurate conclusions, successful project outcomes. |
| Report format, citations, and content | 15% | 35.25 pts | Proper length, citations, and professional presentation. |

---

## 🛠 How to Run
**1. Clone the repository**
```bash
git clone https://github.com/vedpd/USD-MS-AAI.git
cd "USD-MS-AAI/Module 2"
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, manually install key packages:)*
```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter tensorflow transformers
```

**3. Download the dataset**
- Get the dataset from [Kaggle](https://www.kaggle.com/datasets/krish0202/symptom-based-disease-labeling-dataset/data)
- Place it inside the `Data/` folder.

**4. Run Jupyter Notebook**
```bash
jupyter notebook
```
- Open the desired notebook from the **Modelling/** folder and run all cells sequentially.

---

##  Project Description
The project aims to develop machine learning models that can accurately classify diseases based on symptom data.  
This application can assist in **early diagnosis** and **treatment planning**, potentially reducing diagnosis time and improving patient outcomes.

---



